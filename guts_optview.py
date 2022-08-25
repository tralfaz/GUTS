from gravity import G as Gconst

try:
    from PyQt6.QtCore import QObject, pyqtSlot
    from PyQt6.QtWidgets import QApplication
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
except:
    from PyQt5.QtCore import QObject, pyqtSlot
    from PyQt5.QtWidgets import (QMainWindow,
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
        
        wgt = QPushButton("Test 1")
        actslo.addWidget(wgt)
        wgt.clicked.connect(self._optCtrlr.ActionTest1)
        self._test1BTN = wgt

        wgt = QPushButton("Test 2")
        actslo.addWidget(wgt)
        wgt.clicked.connect(self._optCtrlr.ActionTest2)
        self._test2BTN = wgt

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

        bodiesHbox = QHBoxLayout()
        bodiesHbox.addWidget(bodiesLBL)
        bodiesHbox.addWidget(bodiesSBX)
        pvbox.addLayout(bodiesHbox)

        gravLBL = QLabel()
        gravLBL.setText("Gravity: ")
        
        gravSBX = QDoubleSpinBox()
        gravSBX.setDecimals(15)
        gravSBX.setValue(Gconst)
        gravSBX.setSingleStep(Gconst)

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
        print(f"PosRange: {posRange}")
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
        wgt.insertItems(0, ["Add", "Move", "Radii", "Trails"])
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
        self._frameRateeCOMBO = wgt

        hbox = QHBoxLayout()
        hbox.addWidget(frameRateLBL)
        hbox.addWidget(wgt)
        pvbox.addLayout(hbox)

    def _massMaxChangeDone(self):
        text = self._massMaxLE.text()
        massRange = self._optCtrlr.massRange()
        print(f"_massMaxChangeDone: {text} {massRange}")
        newMax = _stof(text)
        if newMax is not None:
            if newMax > massRange[0]:
                self._optCtrlr.setMassRange(massRange[0], newMax)
                return
        self._massMaxLE.setText(f"{massRange[1]}")

    def _massMinChangeDone(self):
        text = self._massMinLE.text()
        massRange = self._optCtrlr.massRange()
        print(f"_massMinChangeDone: {text} {massRange}")
        newMin = _stof(text)
        if newMin is not None:
            if newMin < massRange[1]:
                self._optCtrlr.setMassRange(newMin, massRange[1])
                return
        self._massMinLE.setText(f"{massRange[0]}")

    def _posMaxChangeDone(self):
        text = self._posMaxLE.text()
        posRange = self._optCtrlr.positionRange()
        print(f"_posMaxChangeDone: {text} {posRange}")
        newMax = _stof(text)
        if newMax is not None:
            if newMax > posRange[0]:
                self._optCtrlr.setPositionRange(posRange[0], newMax)
                return
        self._posMaxLE.setText(f"{posRange[1]}")

    def _posMinChangeDone(self):
        text = self._posMinLE.text()
        posRange = self._optCtrlr.positionRange()
        print(f"_posMinChangeDone: {text} {posRange}")
        newMin = _stof(text)
        if newMin is not None:
            if newMin < posRange[1]:
                self._optCtrlr.setPositionRange(newMin, posRange[1])
                return
        self._posMinLE.setText(f"{posRange[0]}")

    def _velMaxChangeDone(self):
        text = self._velMaxLE.text()
        velRange = self._optCtrlr.velocityRange()
        print(f"_velMaxChangeDone: {text} {velRange}")
        newMax = _stof(text)
        if newMax is not None:
            if newMax > velRange[0]:
                self._optCtrlr.setVelocityRange(velRange[0], newMax)
                return
        self._velMaxLE.setText(f"{velRange[1]}")

    def _velMinChangeDone(self):
        text = self._velMinLE.text()
        velRange = self._optCtrlr.velocityRange()
        print(f"_velMinChangeDone: {text} {velRange}")
        newMin = _stof(text)
        if newMin is not None:
            if newMin < velRange[1]:
                self._optCtrlr.setVelocityRange(newMin, velRange[1])
                return
        self._velMinLE.setText(f"{velRange[0]}")