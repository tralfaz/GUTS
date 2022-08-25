"""
"""

import time

import gravity
from guts_optview import OptionsView
from guts_ctrlr import GutsController
try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtCore import QObject, pyqtSlot
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtWidgets import (QMainWindow,                                 
                                 QDialog,
                                 QHBoxLayout,
                                 QLabel,
                                 QPushButton,
                                 QVBoxLayout,
                                 QWidget)
except:
    from PyQt5.QtCore import QObject, pyqtSlot
    from PyQt5.QtWidgets import (QMainWindow,
                                 QDialog,
                                 QHBoxLayout,
                                 QLabel,
                                 QPushButton,
                                 QVBoxLayout,
                                 QWidget)


import numpy as np

from vispy import app as vispyApp
from vispy import scene as vispyScene


class GutsMainWin(QMainWindow):

    def __init__(self, parent=None, flags=None):
        super().__init__(parent)

        self._vispyApp = vispyApp
        
        self._vpCanvas = vispyScene.SceneCanvas(keys='interactive',
                                                size=(600, 600),
                                                show=True)
        self._vpView = self._vpCanvas.central_widget.add_view()

        # Add Canera view manipulator
        self._vpView.camera = vispyScene.cameras.ArcballCamera(fov=0)
        self._vpView.camera.scale_factor = 500

        widget = QWidget()
        widget.setLayout(QVBoxLayout())
        widget.layout().addWidget(self._vpCanvas.native)

        self.setCentralWidget(widget)

    def vispyApp(self):
        return self._vispyApp

    def vispyCanvas(self):
        return self._vpCanvas

    def vispyView(self):
        return self._vpView




## create canvas and view
#canvas = vispyscene.scenecanvas(keys='interactive', size=(600, 600), show=true)
#print(f"canvas; {canvas} {canvas.__class__.__bases__}")
#view = canvas.central_widget.add_view()
#print(f"view: {view}")
#
## add canera view manipulator
#view.camera = vispyscene.cameras.arcballcamera(fov=0)
#view.camera.scale_factor = 500
#
#w = qmainwindow()
#widget = qwidget()
#w.setcentralwidget(widget)
#widget.setlayout(qvboxlayout())
#widget.layout().addwidget(canvas.native)
#
#w.show()





if __name__ == "__main__":
    print(dir(vispyApp))
    print(dir(vispyApp.canvas))

    app = QApplication([])
    
    mainWin = GutsMainWin()
    mainWin.show()
    
    gravityModel = gravity.Gravity()
    
    gutsCtrlr = GutsController()
    gutsCtrlr.setModel(gravityModel)
    gutsCtrlr.setMainWin(mainWin)
    
    optsView = OptionsView(gutsCtrlr)
    optsView.show()
    gutsCtrlr.setUIView(optsView)
    
    vispyApp.run()
