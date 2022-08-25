"""
"""

import time

import gravity
from guts_optview import OptionsView
from guts_ctrlr import GutsController

from PyQt6.QtCore import Qt
from PyQt6.QtCore import QObject, pyqtSlot
from PyQt6.QtWidgets import (QApplication,
                             QMainWindow,
                             QVBoxLayout,
                             QWidget)

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

        # Add Camera view manipulator
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
