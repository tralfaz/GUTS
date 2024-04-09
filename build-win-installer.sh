#!/bin/sh

MAKENSIS="/cygdrive/c/opt/NSIS/makensis.exe"


if [ "$1" = "clean" ]; then
  rm -rf Guts-install.exe
  exit
fi

"$MAKENSIS" build-win-installer.nsi
