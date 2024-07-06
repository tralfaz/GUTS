#!/bin/sh
#
# PyInstaller: https://pyinstaller.org/en/stable/index.html
#   pip install pyinstaller
# ImageToIcons:
#   https://apps.apple.com/us/app/image2icon-make-your-icons/id992115977?mt=12
#
set -x

if [ -e macos-Guts.spec ]; then
  if [ -e Guts.spec ]; then
    if [ macos-Guts.spec -nt Guts.spec ]; then
      cp macos-Guts.spec Guts.spec
    fi
  else
    cp macos-Guts.spec Guts.spec
  fi

  pyinstaller --noconfirm Guts.spec

else

  pyinstaller --windowed \
              --name Guts \
              -i assets/guts-app.icns \
              --noconfirm \
              --hidden-import vispy.glsl \
              --collect-all vispy.glsl   \
              --hidden-import vispy.app.backends \
              --hidden-import vispy.app.backends._pyqt6 \
              --osx-bundle-identifier com.midoma.pyapps.guts guts.py

  #            --distpat product \

  if [ -e Guts.spec ]; then
    cp Guts.spec macos-Guts.spec
  fi
      
fi

