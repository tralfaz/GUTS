import gravity

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
        if opts.get("trailMax"):
            self._trailLenSBX.setValue(opts.get("trailMax", 1000))

    def setRunning(self, running):
        self._newSimBTN.setEnabled(not running)
        self._startBTN.setEnabled(not running)
        self._stopBTN.setEnabled(running)
        self._jumpOneBTN.setEnabled(not running)
        self._addBTN.setEnabled(not running)
        self._delBTN.setEnabled(not running)
        self._frameModeCOMBO.setEnabled(not running)
        
    def _makeActionsUI(self):
        actslo = self._actsLayout
        
        self._newSimBTN = QPushButton("New Simulation")
        actslo.addWidget(self._newSimBTN)
        self._newSimBTN.clicked.connect(self._optCtrlr.actionNewSimulation)

        self._startBTN = QPushButton("Start")
        actslo.addWidget(self._startBTN)
        self._startBTN.clicked.connect(self._optCtrlr.actionStartSimulation)
        self._startBTN.setEnabled(False)

        self._stopBTN = QPushButton("Stop")
        actslo.addWidget(self._stopBTN)
        self._stopBTN.clicked.connect(self._optCtrlr.actionStopSimulation)
        self._stopBTN.setEnabled(False)

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
        wgt.clicked.connect(self._optCtrlr._test3)
        self._test1BTN = wgt

        wgt = QPushButton("Spin Off")
        actslo.addWidget(wgt)
        wgt.clicked.connect(self._optCtrlr.actionSpinSwitch)
        self._spinSwitchBTN = wgt

#        wgt = QPushButton("Save Options")
#        actslo.addWidget(wgt)
#        wgt.clicked.connect(self._optCtrlr.actionSaveOptions)
#        self._saveOptionsBTN = wgt

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

        bodiesLBL = QLabel()
        bodiesLBL.setText("Bodies: ")

        bodiesSBX = QSpinBox()
        bodiesSBX.setRange(1, 16)
        bodiesSBX.setValue(3)
        bodiesSBX.valueChanged.connect(ctlr.bodyCountChanged)

        hbox = QHBoxLayout()
        hbox.addWidget(bodiesLBL)
        hbox.addWidget(bodiesSBX)
        pvbox.addLayout(hbox)

        gravLBL = QLabel()
        gravLBL.setText("Gravity: ")
        
        gravSBX = QDoubleSpinBox()
        gravSBX.setDecimals(15)
        gravSBX.setValue(ctlr.gravityConst())
        gravSBX.setSingleStep(gravity.G)
        gravSBX.valueChanged.connect(ctlr.gravityConstChanged)
        
        gravHbox = QHBoxLayout()
        gravHbox.addWidget(gravLBL)
        gravHbox.addWidget(gravSBX)
        pvbox.addLayout(gravHbox)

        # Mass Random Range in Kg
        massRange = ctlr.massRange()
        massMinLBL = QLabel("Mass Range: min ")
        self._massMinLE  = QLineEdit()
        self._massMinLE.setText(f"{massRange[0]}")
        self._massMinLE.editingFinished.connect(self._massMinChangeDone)
        massMaxLBL = QLabel()
        massMaxLBL.setText("max ")
        self._massMaxLE = QLineEdit()
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
        self._posMinLE.editingFinished.connect(self._posMinChangeDone)
        posMaxLBL = QLabel()
        posMaxLBL.setText("max ")
        self._posMaxLE = QLineEdit()
        self._posMaxLE.setText(f"{posRange[1]}")
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
        self._velMinLE.editingFinished.connect(self._velMinChangeDone)
        velMaxLBL = QLabel()
        velMaxLBL.setText("max ")
        self._velMaxLE = QLineEdit()
        self._velMaxLE.setText(f"{velRange[1]}")
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
        wgt.insertItems(0, ["Move", "Radii", "Trails", "Add", "Merge"])
        wgt.currentIndexChanged.connect(ctlr.frameModeChanged)
        self._frameModeCOMBO = wgt

        frameModeHbox = QHBoxLayout()
        frameModeHbox.addWidget(frameModeLBL)
        frameModeHbox.addWidget(wgt)
        pvbox.addLayout(frameModeHbox)

        # Frame Rate Option Menu
        frameRateLBL = QLabel()
        frameRateLBL.setText("Frame Rate: ")

        wgt = QComboBox()
        wgt.insertItems(0, ["1/sec", "2/sec", "4/sec", "8/sec",
                            "16/sec", "auto"])
        wgt.setCurrentIndex(2)
        wgt.currentIndexChanged.connect(ctlr.frameRateChanged)
        self._frameRateCOMBO = wgt

        hbox = QHBoxLayout()
        hbox.addWidget(frameRateLBL)
        hbox.addWidget(wgt)
        pvbox.addLayout(hbox)

        # Spin Mode
        lbl = QLabel()
        lbl.setText("Spin Mode:")

        wgt = QComboBox()
        wgt.insertItems(0, ["X", "Y", "Z", "XY", "XZ", "YZ", "XYZ"])
        wgt.setCurrentIndex(0)
        wgt.currentIndexChanged.connect(ctlr.spinModeChanged)

        hbox = QHBoxLayout()
        hbox.addWidget(lbl)
        hbox.addWidget(wgt)
        pvbox.addLayout(hbox)

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

        colDistLBL = QLabel()
        colDistLBL.setText("Collision Distance:")

        colDistSBX = QSpinBox()
        colDistSBX.setRange(1, 15)
        colDistSBX.setValue(int(ctlr.collisionDistance()))
        colDistSBX.setSingleStep(1)
        colDistSBX.valueChanged.connect(ctlr.collDistChanged)

        hbox = QHBoxLayout()
        hbox.addWidget(colDistLBL)
        hbox.addWidget(colDistSBX)
        pvbox.addLayout(hbox)

    def _massMaxChangeDone(self):
        text = self._massMaxLE.text()
        massRange = self._optCtrlr.massRange()
        newMax = _stof(text)
        if newMax is not None:
            if newMax > massRange[0]:
                self._optCtrlr.setMassRange(massRange[0], newMax)
                return
        self._massMaxLE.setText(f"{massRange[1]}")

    def _massMinChangeDone(self):
        text = self._massMinLE.text()
        massRange = self._optCtrlr.massRange()
        newMin = _stof(text)
        if newMin is not None:
            if newMin < massRange[1]:
                self._optCtrlr.setMassRange(newMin, massRange[1])
                return
        self._massMinLE.setText(f"{massRange[0]}")

    def _posMaxChangeDone(self):
        text = self._posMaxLE.text()
        posRange = self._optCtrlr.positionRange()
        newMax = _stof(text)
        if newMax is not None:
            if newMax > posRange[0]:
                self._optCtrlr.setPositionRange(posRange[0], newMax)
                return
        self._posMaxLE.setText(f"{posRange[1]}")

    def _posMinChangeDone(self):
        text = self._posMinLE.text()
        posRange = self._optCtrlr.positionRange()
        newMin = _stof(text)
        if newMin is not None:
            if newMin < posRange[1]:
                self._optCtrlr.setPositionRange(newMin, posRange[1])
                return
        self._posMinLE.setText(f"{posRange[0]}")

    def _velMaxChangeDone(self):
        text = self._velMaxLE.text()
        velRange = self._optCtrlr.velocityRange()
        newMax = _stof(text)
        if newMax is not None:
            if newMax > velRange[0]:
                self._optCtrlr.setVelocityRange(velRange[0], newMax)
                return
        self._velMaxLE.setText(f"{velRange[1]}")

    def _velMinChangeDone(self):
        text = self._velMinLE.text()
        velRange = self._optCtrlr.velocityRange()
        newMin = _stof(text)
        if newMin is not None:
            if newMin < velRange[1]:
                self._optCtrlr.setVelocityRange(newMin, velRange[1])
                return
        self._velMinLE.setText(f"{velRange[0]}")
