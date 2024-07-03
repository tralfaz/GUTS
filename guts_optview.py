import gravity
import optstore

from PyQt6.QtCore import QObject, pyqtSlot
from PyQt6.QtWidgets import (QMainWindow,
                             QComboBox,
                             QDialog,
                             QDoubleSpinBox,
                             QGroupBox,
                             QHBoxLayout,
                             QLabel,
                             QLineEdit,
                             QPushButton,
                             QSpinBox,
                             QVBoxLayout,
                             QWidget)


def _stof(text):
    try:
        return float(text)
    except ValueError as valx:
        return None


class OptionsView(QDialog):

    def __init__(self, optCtrlr, parent=None):
        super().__init__(parent)
        self.setWindowTitle("GUTS - Options")

        self._optCtrlr = optCtrlr
        
        self._dlgLayout = QHBoxLayout()

        self._actsLayout = QVBoxLayout()
        self._optsLayout = QVBoxLayout()
        self._dlgLayout.addLayout(self._actsLayout)
        self._dlgLayout.addLayout(self._optsLayout)

        self._makeActionsUI()
        self._makeOptionsUI()

        self.setLayout(self._dlgLayout)

    def applyOptions(self, opts):
        optval = opts.get(optstore.BODY_COUNT)
        if optval is not None:
            self._bodiesSBX.setValue(optval)
        optval = opts.get(optstore.GRAV_CONST)
        if optval is not None:
            self._gravSBX.setValue(optval)
        optval = opts.get(optstore.MASS_RANGE)
        if optval is not None:
            self._massMinLE.setText(f"{optval[0]:1.1f}")
            self._massMaxLE.setText(f"{optval[1]:1.1f}")
        optval = opts.get(optstore.POS_RANGE)
        if optval is not None:
            self._posMinLE.setText(f"{optval[0]:1.1f}")
            self._posMaxLE.setText(f"{optval[1]:1.1f}")
        optval = opts.get(optstore.VEL_RANGE)
        if optval is not None:
            self._velMinLE.setText(f"{optval[0]:1.1f}")
            self._velMaxLE.setText(f"{optval[1]:1.1f}")
        optval = opts.get(optstore.FRAME_RATE)
        if optval is not None:
            rates = [1.0, 0.5, 0.25, 0.125, 0.0625, 1.0/60.0]
            try:
                rateIndex = rates.index(optval)
            except ValueError:
                rateIndex = 2
            self._frameRateCOMBO.setCurrentIndex(rateIndex)
        optval = opts.get(optstore.SPIN_MODE)
        if optval is not None:
            spins = ["X", "Y", "Z", "XY", "XZ", "YZ", "XYZ"]
            try:
                spinIndex = spins.index(optval)
            except ValueError:
                spinIndex = 2
            self._spinModeCOMBO.setCurrentIndex(spinIndex)
        optval = opts.get(optstore.TRAIL_LEN)
        if optval is not None:
            self._trailLenSBX.setValue(optval)
        optval = opts.get(optstore.COLL_DIST)
        if optval is not None:
            self._collDistSBX.setValue(int(optval))

    def newSimulation(self):
        self._optCtrlr.actionNewSimulation()
    
    def setRunning(self, running):
        self._newSimBTN.setEnabled(not running)
        self._startStopBTN.setEnabled(True)
        self._jumpOneBTN.setEnabled(not running)
        self._addBTN.setEnabled(not running)
        self._delBTN.setEnabled(not running)
        self._frameModeCOMBO.setEnabled(not running)
        
    def _makeActionsUI(self):
        actslo = self._actsLayout
        
        self._newSimBTN = QPushButton("New Simulation")
        actslo.addWidget(self._newSimBTN)
        self._newSimBTN.clicked.connect(self._optCtrlr.actionNewSimulation)

        self._startStopBTN = QPushButton("Start")
        actslo.addWidget(self._startStopBTN)
        self._startStopBTN.clicked.connect(self._startStopCB)
        self._startStopBTN.setEnabled(False)

        wgt = QPushButton("Jump One Second")
        actslo.addWidget(wgt)
        wgt.clicked.connect(self._optCtrlr.actionJumpOneSecond)
        wgt.setEnabled(False)
        self._jumpOneBTN = wgt
        
        wgt = QPushButton("Add")
        actslo.addWidget(wgt)
        wgt.clicked.connect(self._optCtrlr.actionAddMarker)
        self._addBTN = wgt

        wgt = QPushButton("Delete")
        actslo.addWidget(wgt)
        wgt.clicked.connect(self._optCtrlr.actionDeleteOldestMarker)
        self._delBTN = wgt
        
        wgt = QPushButton("Test")
        actslo.addWidget(wgt)
        wgt.clicked.connect(self._optCtrlr._testCB)
        self._test1BTN = wgt

        wgt = QPushButton("Spin Off")
        actslo.addWidget(wgt)
        wgt.clicked.connect(self._optCtrlr.actionSpinSwitch)
        self._spinSwitchBTN = wgt

        wgt = QPushButton("Save Options")
        actslo.addWidget(wgt)
        wgt.clicked.connect(self._optCtrlr.actionSaveOptions)
        self._saveOptionsBTN = wgt

        quitBTN = QPushButton("Quit")
        actslo.addWidget(quitBTN)
        quitBTN.clicked.connect(self._optCtrlr.actionQuit)

    def _makeOptionsUI(self):
        optslo = self._optsLayout
        ctlr = self._optCtrlr

        paramGRP = QGroupBox()
        paramGRP.setTitle("Parameters")
        paramGRP.setFlat(False)
        pvbox = QVBoxLayout()
        paramGRP.setLayout(pvbox)
        optslo.addWidget(paramGRP)

        # Body Count
        bodiesLBL = QLabel()
        bodiesLBL.setText("Bodies: ")

        self._bodiesSBX = QSpinBox()
        self._bodiesSBX.setRange(1, 16)
        self._bodiesSBX.setValue(3)
        self._bodiesSBX.valueChanged.connect(ctlr.bodyCountChanged)

        hbox = QHBoxLayout()
        hbox.addWidget(bodiesLBL)
        hbox.addWidget(self._bodiesSBX)
        pvbox.addLayout(hbox)

        lbl = QLabel()
        lbl.setText("Gravity: ")
        
        wgt = QDoubleSpinBox()
        wgt.setDecimals(15)
        wgt.setValue(ctlr.gravityConst())
        wgt.setSingleStep(gravity.G)
        wgt.valueChanged.connect(ctlr.gravityConstChanged)
        self._gravSBX = wgt
        
        gravHbox = QHBoxLayout()
        gravHbox.addWidget(lbl)
        gravHbox.addWidget(wgt)
        pvbox.addLayout(gravHbox)

        # Mass Random Range in Kg
        massRange = ctlr.massRange()
        massMinLBL = QLabel("Mass Range: min ")
        self._massMinLE  = QLineEdit()
        self._massMinLE.setText(f"{massRange[0]}")
        self._massMinLE.textChanged.connect(self._massMinChanged)
        self._massMinLE.editingFinished.connect(self._massMinChangeDone)
        massMaxLBL = QLabel()
        massMaxLBL.setText("max ")
        self._massMaxLE = QLineEdit()
        self._massMaxLE.textChanged.connect(self._massMaxChanged)
        self._massMaxLE.editingFinished.connect(self._massMaxChangeDone)
        self._massMaxLE.setText(f"{massRange[1]}")

        massHbox = QHBoxLayout()
        massHbox.addWidget(massMinLBL)
        massHbox.addWidget(self._massMinLE)
        massHbox.addWidget(massMaxLBL)
        massHbox.addWidget(self._massMaxLE)
        pvbox.addLayout(massHbox)

        # Position XYZ Random Range
        posRange = ctlr.positionRange()
        posMinLBL = QLabel("Position Range: min ")
        self._posMinLE  = QLineEdit()
        self._posMinLE.setText(f"{posRange[0]}")
        self._posMinLE.textChanged.connect(self._posMinChanged)
        self._posMinLE.editingFinished.connect(self._posMinChangeDone)
        posMaxLBL = QLabel()
        posMaxLBL.setText("max ")
        self._posMaxLE = QLineEdit()
        self._posMaxLE.setText(f"{posRange[1]}")
        self._posMaxLE.textChanged.connect(self._posMaxChanged)
        self._posMaxLE.editingFinished.connect(self._posMaxChangeDone)

        posHbox = QHBoxLayout()
        posHbox.addWidget(posMinLBL)
        posHbox.addWidget(self._posMinLE)
        posHbox.addWidget(posMaxLBL)
        posHbox.addWidget(self._posMaxLE)
        pvbox.addLayout(posHbox)

        # Velocity XYZ Random Range
        velRange = ctlr.velocityRange()
        velMinLBL = QLabel("Velocity Range: min ")
        self._velMinLE  = QLineEdit()
        self._velMinLE.setText(f"{velRange[0]}")
        self._velMinLE.textChanged.connect(self._velMinChanged)
        self._velMinLE.editingFinished.connect(self._velMinChangeDone)
        velMaxLBL = QLabel()
        velMaxLBL.setText("max ")
        self._velMaxLE = QLineEdit()
        self._velMaxLE.setText(f"{velRange[1]}")
        self._velMaxLE.textChanged.connect(self._velMaxChanged)
        self._velMaxLE.editingFinished.connect(self._velMaxChangeDone)

        velHbox = QHBoxLayout()
        velHbox.addWidget(velMinLBL)
        velHbox.addWidget(self._velMinLE)
        velHbox.addWidget(velMaxLBL)
        velHbox.addWidget(self._velMaxLE)
        pvbox.addLayout(velHbox)

        # Frame Mode Option Menu
        frameModeLBL = QLabel()
        frameModeLBL.setText("Frame Mode: ")

        wgt = QComboBox()
        wgt.insertItems(0, ["Move","Radii","Trails","Tubular",
                            "Snakes","Merge","Cloud", "Spheres",
                            "SphereTrails"])
        wgt.currentIndexChanged.connect(ctlr.frameModeChanged)
        self._frameModeCOMBO = wgt

        frameModeHbox = QHBoxLayout()
        frameModeHbox.addWidget(frameModeLBL)
        frameModeHbox.addWidget(wgt)
        pvbox.addLayout(frameModeHbox)

        # Frame Rate Option Menu
        lbl = QLabel()
        lbl.setText("Frame Rate: ")

        wgt = QComboBox()
        wgt.insertItems(0, ["1/sec", "2/sec", "4/sec", "8/sec",
                            "16/sec", "auto"])
        wgt.setCurrentIndex(2)
        wgt.currentIndexChanged.connect(ctlr.frameRateChanged)
        self._frameRateCOMBO = wgt

        hbox = QHBoxLayout()
        hbox.addWidget(lbl)
        hbox.addWidget(wgt)
        pvbox.addLayout(hbox)

        # Spin Mode
        lbl = QLabel()
        lbl.setText("Spin Mode:")

        wgt = QComboBox()
        wgt.insertItems(0, ["X", "Y", "Z", "XY", "XZ", "YZ", "XYZ"])
        wgt.setCurrentIndex(0)
        wgt.currentIndexChanged.connect(ctlr.spinModeChanged)
        self._spinModeCOMBO = wgt
        
        hbox = QHBoxLayout()
        hbox.addWidget(lbl)
        hbox.addWidget(wgt)
        pvbox.addLayout(hbox)

        # Trail Limit
        trailLenLBL = QLabel()
        trailLenLBL.setText("Trail Length:")

        wgt = QSpinBox()
        wgt.setRange(1, 10000)
        wgt.setValue(1000)
        wgt.setSingleStep(100)
        wgt.valueChanged.connect(ctlr.trailLengthChanged)
        self._trailLenSBX = wgt
        
        hbox = QHBoxLayout()
        hbox.addWidget(trailLenLBL)
        hbox.addWidget(self._trailLenSBX)
        pvbox.addLayout(hbox)

        lbl = QLabel()
        lbl.setText("Collision Distance:")

        wgt = QSpinBox()
        wgt.setRange(1, 15)
        wgt.setValue(int(ctlr.collisionDistance()))
        wgt.setSingleStep(1)
        wgt.valueChanged.connect(ctlr.collDistChanged)
        self._collDistSBX = wgt
        
        hbox = QHBoxLayout()
        hbox.addWidget(lbl)
        hbox.addWidget(wgt)
        pvbox.addLayout(hbox)

    def _massMaxChanged(self, text):
        massRange = self._optCtrlr.massRange()
        newMax = _stof(text)
        if newMax is not None and newMax > massRange[0]:
            self._optCtrlr.setMassRange(massRange[0], newMax)

    def _massMaxChangeDone(self):
        text = self._massMaxLE.text()
        massRange = self._optCtrlr.massRange()
        newMax = _stof(text)
        if newMax is not None and newMax > massRange[0]:
            self._optCtrlr.setMassRange(massRange[0], newMax)
            return
        self._massMaxLE.setText(f"{massRange[1]}")

    def _massMinChanged(self, text):
        massRange = self._optCtrlr.massRange()
        newMin = _stof(text)
        if newMin is not None and newMin < massRange[1]:
            self._optCtrlr.setMassRange(newMin, massRange[1])

    def _massMinChangeDone(self):
        text = self._massMinLE.text()
        massRange = self._optCtrlr.massRange()
        newMin = _stof(text)
        if newMin is not None and newMin < massRange[1]:
            self._optCtrlr.setMassRange(newMin, massRange[1])
            return
        self._massMinLE.setText(f"{massRange[0]}")

    def _posMaxChanged(self, text):
        posRange = self._optCtrlr.positionRange()
        newMax = _stof(text)
        if newMax is not None and newMax > posRange[0]:
            self._optCtrlr.setPositionRange(posRange[0], newMax)

    def _posMaxChangeDone(self):
        text = self._posMaxLE.text()
        posRange = self._optCtrlr.positionRange()
        newMax = _stof(text)
        if newMax is not None and newMax > posRange[0]:
            self._optCtrlr.setPositionRange(posRange[0], newMax)
            return
        self._posMaxLE.setText(f"{posRange[1]}")

    def _posMinChanged(self, text):
        posRange = self._optCtrlr.positionRange()
        newMin = _stof(text)
        if newMin is not None and newMin < posRange[1]:
            self._optCtrlr.setPositionRange(newMin, posRange[1])

    def _posMinChangeDone(self):
        text = self._posMinLE.text()
        posRange = self._optCtrlr.positionRange()
        newMin = _stof(text)
        if newMin is not None and newMin < posRange[1]:
                self._optCtrlr.setPositionRange(newMin, posRange[1])
                return
        self._posMinLE.setText(f"{posRange[0]}")

    def _startStopCB(self):
        text = self._startStopBTN.text()
        if text == "Start":
            self._startStopBTN.setText("Stop")
            self._optCtrlr.actionStartSimulation()
        else:
            self._startStopBTN.setText("Start")
            self._optCtrlr.actionStopSimulation()

    def _velMaxChanged(self, text):
        velRange = self._optCtrlr.velocityRange()
        newMax = _stof(text)
        if newMax is not None and newMax > velRange[0]:
            self._optCtrlr.setVelocityRange(velRange[0], newMax)

    def _velMaxChangeDone(self):
        text = self._velMaxLE.text()
        velRange = self._optCtrlr.velocityRange()
        newMax = _stof(text)
        if newMax is not None and newMax > velRange[0]:
            self._optCtrlr.setVelocityRange(velRange[0], newMax)
            return
        self._velMaxLE.setText(f"{velRange[1]}")

    def _velMinChanged(self, text):
        velRange = self._optCtrlr.velocityRange()
        newMin = _stof(text)
        if newMin is not None and newMin < velRange[1]:
            self._optCtrlr.setVelocityRange(newMin, velRange[1])

    def _velMinChangeDone(self):
        text = self._velMinLE.text()
        velRange = self._optCtrlr.velocityRange()
        newMin = _stof(text)
        if newMin is not None and newMin < velRange[1]:
            self._optCtrlr.setVelocityRange(newMin, velRange[1])
            return
        self._velMinLE.setText(f"{velRange[0]}")
