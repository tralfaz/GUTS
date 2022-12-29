#!/bin/sh

export PATH="$PATH:/cygdrive/c/opt/Python310/Scripts"

pyinstaller --windowed \
            --hidden-import vispy.glsl \
            --collect-all vispy.glsl   \
            --hidden-import vispy.app.backends \
            --hidden-import vispy.app.backends._pyqt6 \
            guts.py
