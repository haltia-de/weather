#!/bin/sh
# SPDX-License-Identifier: GPL-2.0
# Install haltia-weather (Погода): sh install.sh [ROOT] [PREFIX]
# ROOT empty or / for this system; PREFIX /usr/local unless given (a
# package passes /usr). It needs Python 3 with PyGObject (GTK 3) only. The
# .desktop file shows it in any desktop's launcher; the Haltia shell puts
# it on its home screen (X-Haltia-Home). The names before ADR 0004
# (b8k-weather, the id io.github.trudenboy.Weather, hidden) stay until 3.0.
set -eu
root=${1:-}
root=${root%/}
prefix=${2:-/usr/local}
here=$(cd "$(dirname "$0")" && pwd)
share=$root$prefix/share
id=io.github.haltia_de.Weather
old=io.github.trudenboy.Weather
install -D -m 755 "$here/haltia-weather" "$root$prefix/bin/haltia-weather"
ln -sfn haltia-weather "$root$prefix/bin/b8k-weather"
install -D -m 644 "$here/data/$id.desktop" "$share/applications/$id.desktop"
install -D -m 644 "$here/data/$old.desktop" "$share/applications/$old.desktop"
install -D -m 644 "$here/data/$id.svg" "$share/icons/hicolor/scalable/apps/$id.svg"
install -D -m 644 "$here/data/$id.metainfo.xml" "$share/metainfo/$id.metainfo.xml"
# Files of the old names a manual install left behind.
rm -f "$share/icons/hicolor/scalable/apps/$old.svg" "$share/metainfo/$old.metainfo.xml"
rm -f "$root/usr/local/share/b8k/apps.d/weather.conf" "$root/usr/local/share/b8k/weather.svg"
