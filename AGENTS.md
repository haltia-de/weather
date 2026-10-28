# Weather

Weather (`haltia-weather`) is a GTK 3 application that shows the current
weather and a forecast for a chosen city on one page, using Gismeteo XML.
It is part of Haltia and also runs on other GTK desktops.
Its application ID is `io.github.haltia_de.Weather`.

## Shared rules

The project root and shared decisions live in
[haltia-de/haltia](https://github.com/haltia-de/haltia).
Follow the [shared conventions](https://github.com/haltia-de/haltia/blob/main/docs/conventions.md)
when editing code, documentation, packaging, or preparing a release.

## Repository layout

- `haltia-weather`: Python application, including the UI, data fetching,
  city selection, configuration, cache, and icon drawing.
- `data/`: desktop launchers, SVG icon, and AppStream metainfo.
- `install.sh`: installs the program and its desktop integration.
- `packaging/alpine/`: Alpine APKBUILD.
- `packaging/flatpak/`: Flatpak manifest.
- `debian/`: Debian and Ubuntu packaging.
- `.github/workflows/release.yml`: release workflow using `haltia-de/ci`.
- `README.md`: user documentation; `NEWS.md`: release notes.

## Run and install

With Python 3, PyGObject, and GTK 3 available, run from the checkout:
`python3 haltia-weather`. A graphical desktop session is required.

Run `sh install.sh` as root to install under `/usr/local`.
For a staged package install, use `sh install.sh /path/to/staging /usr`;
the first argument is the destination root and the second is the prefix.

`install.sh` installs the script as the module
`PREFIX/lib/haltia-weather/haltia_weather_main.py` and writes
`PREFIX/bin/haltia-weather` as a stub that runs it with
`runpy.run_module(..., alter_sys=False)`: Python never caches the script it
is started by, so the program's code loads from the `__pycache__` the
package build writes (haltia-de/ci compiles every module). `sys.argv` and
the command line `python3 PREFIX/bin/haltia-weather` stay as they were (the
Haltia shell finds programs by it); `__file__` is the module in
`PREFIX/lib/haltia-weather`. The Flatpak manifest writes the same stub and
compiles `/app/lib/haltia-weather`.

## Releases

Obtain the user's explicit approval before publishing a release or its tag.
Prepare `NEWS.md`, the Alpine `pkgver`, and the AppStream `<release>` for
the same SemVer version as the `vX.Y.Z` tag, following the shared conventions.
Pushing that tag triggers the reusable workflows in `haltia-de/ci` to build
Alpine, Debian, Ubuntu, and Flatpak packages and attach them to the release.
