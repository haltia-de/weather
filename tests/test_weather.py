# SPDX-License-Identifier: GPL-2.0
"""Offline regression tests; GTK widgets are replaced for headless execution."""
import http.server
import json
from pathlib import Path
import runpy
import tempfile
import threading
import time
import types
import unittest
from unittest import mock


class Widget:
    texts = []

    def __init__(self, *args, **kwargs):
        if 'label' in kwargs:
            self.texts.append(kwargs['label'])

    def __getattr__(self, name):
        return lambda *args, **kwargs: None

    def get_style_context(self):
        return self


def idle_add(callback, *args, **kwargs):
    while callback(*args):
        pass


def load_weather(directory):
    gi = types.ModuleType('gi')
    gi.require_version = lambda *args: None
    repository = types.ModuleType('gi.repository')
    repository.GLib = types.SimpleNamespace(
        set_prgname=lambda *args: None,
        get_user_config_dir=lambda: directory,
        get_user_cache_dir=lambda: directory,
        idle_add=idle_add, PRIORITY_LOW=300)
    repository.Gdk = types.SimpleNamespace()
    repository.Gtk = types.SimpleNamespace(
        Application=Widget, Box=Widget, Grid=Widget, Label=Widget,
        Button=Widget, DrawingArea=Widget,
        Orientation=types.SimpleNamespace(VERTICAL=1),
        Align=types.SimpleNamespace(CENTER=1, END=2),
        Justification=types.SimpleNamespace(CENTER=1, LEFT=2))
    with mock.patch.dict('sys.modules', {'gi': gi, 'gi.repository': repository}):
        return runpy.run_path(str(Path(__file__).resolve().parents[1] / 'haltia-weather'))


class WeatherTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.weather = load_weather(self.directory.name)

    def test_trickling_download_obeys_overall_deadline(self):
        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.end_headers()
                try:
                    for _ in range(100):
                        self.wfile.write(b' ')
                        self.wfile.flush()
                        time.sleep(0.05)
                except (BrokenPipeError, ConnectionResetError):
                    pass

            def log_message(self, *args):
                pass

        try:
            server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        except PermissionError:
            self.skipTest('sandbox prohibits loopback sockets')
        server.daemon_threads = True
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            get_xml = self.weather['get_xml']
            with mock.patch.dict(get_xml.__globals__, FETCH_SEC=0.3):
                start = time.monotonic()
                with self.assertRaises(TimeoutError):
                    get_xml('http://127.0.0.1:%d/' % server.server_port)
                elapsed = time.monotonic() - start
                self.assertGreaterEqual(elapsed, 0.25)
                self.assertLess(elapsed, 1.2)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def test_deadline_is_checked_between_socket_reads(self):
        read = self.weather['_read_bounded']
        response = mock.Mock()
        response.read1.return_value = b'x'
        with mock.patch.object(read.__globals__['time'], 'monotonic',
                               side_effect=[10, 10.1, 10.2, 11]), \
                mock.patch.dict(read.__globals__, FETCH_MAX=100):
            with self.assertRaises(TimeoutError):
                read(response, 11)
        self.assertEqual(response.read1.call_count, 2)
        response.read.assert_not_called()
        timeouts = response.fp.raw._sock.settimeout.call_args_list
        self.assertAlmostEqual(timeouts[0].args[0], 1)
        self.assertAlmostEqual(timeouts[1].args[0], 0.8)

    def test_bad_numeric_fields_keep_forecast_and_are_not_cached(self):
        data = json.loads('''{
            "city_id": 4079, "city": "Test", "fetched": 1790000000,
            "now": {"t": 12, "ws": NaN, "hum": "bad", "p": 750},
            "days": [{"date": "2026-10-22", "tmax": 14, "tmin": 7,
                      "gust_speed": NaN, "wsmin": "bad", "wsmax": 5,
                      "prflt": "bad", "pt": 1,
                      "steps": [{"valid": "2026-10-22T12:00:00",
                                 "t": 13, "ws": "bad", "hum": NaN,
                                 "prflt": "bad", "pt": 1, "p": 751}]}]
        }''')
        cache = Path(self.weather['CACHE'])
        cache.write_text(json.dumps(data))
        clean = self.weather['load_cache'](4079)
        self.assertEqual(clean['now']['t'], 12)
        self.assertIsNone(clean['now']['ws'])
        self.assertIsNone(clean['now']['hum'])
        self.assertEqual(clean['days'][0]['steps'][0]['t'], 13)
        self.assertEqual(self.weather['precip_text'](clean['days'][0]), 'дождь')

        app = object.__new__(self.weather['Weather'])
        app.city_id = 4079
        app.day_index = None
        app.scroll = Widget()
        app.when = Widget()
        app.button = Widget()
        app.generation = 0
        Widget.texts.clear()
        # Repeated refreshes must neither discard the forecast nor blank the page.
        for _ in range(2):
            app.loaded(clean, None)
            app.day_card(app.data['days'][0])
            self.assertIs(app.data, clean)
        self.assertIn('— м/с', Widget.texts)
        self.assertIn('— %', Widget.texts)
        self.assertIn('+12°', Widget.texts)
        self.assertIn('750 мм', Widget.texts)
        # Saving the original invalid input also sanitizes every numeric field.
        self.weather['save_cache'](data)
        saved = json.loads(cache.read_text(), parse_constant=lambda x: self.fail(x))
        self.assertIsNone(saved['now']['ws'])
        self.assertIsNone(saved['now']['hum'])
        self.assertIsNone(saved['days'][0]['steps'][0]['prflt'])
        self.assertEqual(saved['now']['p'], 750)
        self.assertEqual(self.weather['load_cache'](4079), clean)

    def test_service_fields_reject_nonfinite_and_nonnumeric_values(self):
        import xml.etree.ElementTree as ET
        values = self.weather['values'](ET.fromstring(
            '<values t="9" ws="NaN" p="oops" hum="Infinity" descr="Rain"/>'))
        self.assertEqual(values, {'t': 9, 'ws': None, 'p': None,
                                  'hum': None, 'descr': 'Rain'})


if __name__ == '__main__':
    unittest.main()
