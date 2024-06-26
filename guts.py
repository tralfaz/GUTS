"""
"""

import time

import gravity
from guts_optview import OptionsView
from guts_ctrlr import GutsController
from guts_spheres import OrbStore

import numpy

from PyQt6.QtCore import Qt
from PyQt6.QtCore import QObject, pyqtSlot
from PyQt6.QtWidgets import (QApplication,
                             QVBoxLayout,
                             QWidget)

from vispy import app as vispyApp
from vispy import scene as vispyScene
from vispy.util import keys as vispyKeys
from vispy.visuals.transforms import MatrixTransform

__version__ = "0.8.1"

class GutsMainWin(QWidget):

    def __init__(self, parent=None, flags=None):
        super().__init__(parent)

        self._vispyApp = vispyApp
        
        self._vpCanvas = vispyScene.SceneCanvas(keys='interactive',
                                                size=(600, 600),
                                                show=True)
        self._vpCanvas.events.key_press.connect(self._vpCanvasKeyPressCB)
        self._vpView = self._vpCanvas.central_widget.add_view()
       
        self._orbStore = OrbStore(self._vpView.scene)
        
        # Add Camera view manipulator
        self._vpView.camera = vispyScene.cameras.ArcballCamera(fov=0)
        self._vpView.camera.scale_factor = 500

        self._axisSize = 0.0
        self._axisPoints = numpy.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0],
                                        [0.0, 0.0, 0.0], [0.0, 1.0, 0.0],
                                        [0.0, 0.0, 0.0], [0.0, 0.0, 1.0]])
        self._axisVis = vispyScene.visuals.XYZAxis(pos=self._axisPoints,
                                                   name="GUTSAxis",
                                                   parent=self._vpView.scene)
        self._axisVis.visible = False

        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self._vpCanvas.native)
        self.setLayout(vbox)

        self._optWidget = None

    def orbStore(self):
        return self._orbStore
    
    def setOptionsView(self, optWidget):
        self._optWidget = optWidget

    def vispyApp(self):
        return self._vispyApp

    def vispyCanvas(self):
        return self._vpCanvas

    def vispyView(self):
        return self._vpView

    def _vpCanvasKeyPressCB(self, event):
#        print(f"_vpCanvasKeyPressCB: {dir(event)}")
        if event.key == "c":
            if self._optWidget.isVisible():
                self._optWidget.lower()
                self._optWidget.setVisible(False)
            else:
                self._optWidget.raise_()
                self._optWidget.setVisible(True)

        elif event.key == "m":
            if self.isMaximized():
                self.showNormal()
            else:
                self.showMaximized()

        elif event.key == "n":
            self._optWidget.newSimulation()

        elif event.key == "s":
            self._optWidget._startStopCB()
            
        elif event.key == "x" and vispyKeys.SHIFT in event.modifiers:
            if self._axisSize == 0.0:
                self._axisSize = 50.0
            else:
                self._axisSize *= 2.0
            axisPoints = self._axisPoints * self._axisSize
            self._axisVis.set_data(pos=axisPoints)
            self._axisVis.visible = self._axisSize > 0.0
        elif event.key == "x":
            if self._axisSize < 10.0:
                self._axisSize = 0.0
            else:
                self._axisSize /= 2.0
            axisPoints = self._axisPoints * self._axisSize
            self._axisVis.set_data(pos=axisPoints)
            self._axisVis.visible = self._axisSize > 0.0
            


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
    gutsCtrlr.recoverOptions()
    
    mainWin.setOptionsView(optsView)
    
    vispyApp.run()
