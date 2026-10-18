#!/bin/sh
# SPDX-License-Identifier: GPL-2.0
# Install b8k-weather (Погода): sh install.sh [ROOT] [PREFIX]
# ROOT empty or / for this system; PREFIX /usr/local unless given (a
# package passes /usr). It needs Python 3 with PyGObject (GTK 3) only. The
# .desktop file
# shows it in any desktop's launcher; the b8k tablet shell puts it on its
# home screen (X-B8K-Home).
set -eu
root=${1:-}
root=${root%/}
prefix=${2:-/usr/local}
here=$(cd "$(dirname "$0")" && pwd)
share=$root$prefix/share
install -D -m 755 "$here/b8k-weather" "$root$prefix/bin/b8k-weather"
install -D -m 644 "$here/data/io.github.trudenboy.Weather.desktop" "$share/applications/io.github.trudenboy.Weather.desktop"
install -D -m 644 "$here/data/io.github.trudenboy.Weather.svg" "$share/icons/hicolor/scalable/apps/io.github.trudenboy.Weather.svg"
install -D -m 644 "$here/data/io.github.trudenboy.Weather.metainfo.xml" "$share/metainfo/io.github.trudenboy.Weather.metainfo.xml"
# The shell's old entry for this program, from before the .desktop file.
rm -f "$root/usr/local/share/b8k/apps.d/weather.conf" "$root/usr/local/share/b8k/weather.svg"
