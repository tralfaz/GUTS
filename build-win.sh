#!/bin/sh
#
# PyInstaller: https://pyinstaller.org/en/stable/index.html
#   pip3 install pyinstaller
#
# Win11:
#    Settings->Privacy & Security->Virus & threat protection->Manage aettings
#      Exclusions:
#        Add Folder: build/Guts
#
set -x

#export PATH="$PATH:/cygdrive/c/opt/Python310/Scripts"

if [ -e /cygdrive/c/opt/python/Scripts/pyinstaller.exe ]; then
  PYINST=/cygdrive/c/opt/python/Scripts/pyinstaller.exe
elif [ -e /cygdrive/c/opt/Python310/Scripts" ]; then
  PYINST=/cygdrive/c/opt/Python310/Scripts/pyinstaller.exe
else
  PYINST=pyinstaller
fi


if [ -e win-Guts.spec ]; then
  if [ win-Guts.spec -nt Guts.spec ]; then
    cp win-Guts.spec Guts.spec
  fi

  $PYINST --noconfirm \
          Guts.spec

else

  $PYINST --windowed \
            --name Guts \
            --hidden-import vispy.glsl \
            --collect-all vispy.glsl   \
            --hidden-import vispy.app.backends \
            --hidden-import vispy.app.backends._pyqt6 \
            guts.py
            #--distpath product \
fi
