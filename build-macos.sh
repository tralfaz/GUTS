#!/bin/sh

pyinstaller --windowed \
            --hidden-import vispy.glsl \
            --collect-all vispy.glsl   \
            --hidden-import vispy.app.backends \
            --hidden-import vispy.app.backends._pyqt6 \
            --osx-bundle-identifier com.midoma.pyapps.guts guts.py
