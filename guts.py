"""
"""

import time

import gravity
from guts_optview import OptionsView
from guts_ctrlr import GutsController

from PyQt6.QtCore import Qt
from PyQt6.QtCore import QObject, pyqtSlot
from PyQt6.QtWidgets import (QApplication,
                             QVBoxLayout,
                             QWidget)

from vispy import app as vispyApp
from vispy import scene as vispyScene
from vispy.visuals.transforms import MatrixTransform

class GutsMainWin(QWidget):

    def __init__(self, parent=None, flags=None):
        super().__init__(parent)

        self._vispyApp = vispyApp
        
        self._vpCanvas = vispyScene.SceneCanvas(keys='interactive',
                                                size=(600, 600),
                                                show=True)
        self._vpView = self._vpCanvas.central_widget.add_view()
        print("VIEW:", self._vpView)
       
        # Add Camera view manipulator
        self._vpView.camera = vispyScene.cameras.ArcballCamera(fov=0)
        self._vpView.camera.scale_factor = 500

#        self._vpView.camera.rotation = MatrixTransform()

        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self._vpCanvas.native)
        self.setLayout(vbox)

    def vispyApp(self):
        return self._vispyApp

    def vispyCanvas(self):
        return self._vpCanvas

    def vispyView(self):
        return self._vpView


if __name__ == "__main__":
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
