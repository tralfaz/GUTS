import math

import gravity
import optstore

import numpy
from vispy import app   as vispyApp
from vispy import scene as vispyScene
from vispy.util.quaternion import Quaternion


class GutsController(object):

    def __init__(self):
        super().__init__()

        self._vpApp      = None
        self._vpAppTimer = None

        self._gravity = None

        self._spinSwitch  = "Spin Off"
        self._spinAngles  = numpy.array([0.0, 0.0, 0.0])
        self._spinModes   = { "X"   : numpy.array([0.5, 0.0, 0.0]),
                              "Y"   : numpy.array([0.0, 0.5, 0.0]),
                              "Z"   : numpy.array([0.0, 0.0, 0.5]),
                              "XY"  : numpy.array([0.5, 0.5, 0.0]),
                              "XZ"  : numpy.array([0.5, 0.0, 0.5]),
                              "YZ"  : numpy.array([0.0, 0.5, 0.5]),
                              "XYZ" : numpy.array([0.5, 0.5, 0.5]) }
        self._spinDeltas  = self._spinModes["X"]
        self._spinTimer = None
        
        self._frameMode = "Move"
        self._frameRate = 0.25
        
        self._firstMarkers = None

        self._optStore = optstore.OptionsStore()

        self._optionsUI = None
        
        self._running = False

        self._sceneOrigin = numpy.array([0.0, 0.0, 0.0])

        self._bodyCount = 3
        self._trailMax  = 1000
        self._trailVis  = None

        self._t2Marker = None
        
    def actionAddMarker(self):
        newPos   = numpy.random.normal(size=(1, 3), loc=0, scale=100)
        newSize  = numpy.random.rand(1, 1) * 100 + 10
        newColor = numpy.random.rand(1, 3)
        newVis = vispyScene.visuals.Markers(pos=newPos,
                                       size=newSize,
                                       antialias=0,
                                       face_color=newColor,
                                       edge_color='white',
                                       edge_width=0,
                                       scaling=True,
                                       spherical=True)
        newVis.parent = self._vpView.scene
        self._t2Marker = newVis
        
    def actionDeleteOldestMarker(self):
        print(f"actionDeleteOldestMarker")
        viewKids = self._vpView.children
        subSceneKids = viewKids[0].children
        print(f"subSceneKids = {subSceneKids}")
        for mdx, obj in enumerate(subSceneKids):
            print(type(obj))
            if type(obj) is vispyScene.visuals.Markers:
                break
        print(f"MDX: {mdx}")
        if mdx > 0:
            subSceneKids[mdx].parent = None

    def actionJumpOneSecond(self):
        self.advanceOneFrame(self._frameMode)

    def actionNewSimulation(self):
        if self._running:
            return
         
        self.clearScene()
        self._gravity.setBodyCount(self._bodyCount)
        self._radiiVis = None

        self._trails = None
        self._trailLen = 0
        self._trailVis = None

        self._gravity.createRandomBodies()
        #self._gravity.printState()

        bodyPoses = self._gravity.bodyPositions()
        self._makeBodyMarkers()

        if self._frameMode == "Radii":
            self._radiiVis = [ ]
            for pos in bodyPoses:
                radii = numpy.array([self._sceneOrigin, pos])
                line = vispyScene.visuals.Line(pos=radii, color=(1.0, 1.0, 0.0),
                                               parent=self._vpView.scene,
                                               width=0.5, method="gl",
                                               antialias=True)
                self._radiiVis.append(line)

        elif self._frameMode == "Trails":
            self._trails = numpy.array(self._gravity.bodyPositions())
        
        self._optionsUI.setRunning(False)

        self._mainWin.setWindowTitle("GUTS - %s(%s)" %
                                     (self._frameMode, bodyPoses.shape[0]))
    def actionQuit(self):
        if self._vpApp:
            self._vpApp.quit()

    def actionSaveOptions(self):
        print("Save Options")

    def actionSpinSwitch(self):
        if not self._spinTimer:
            self._spinTimer = vispyApp.Timer(0.1, start=False)
            self._spinTimer.connect(self._spinTimerCB)

        spinBTN = self._optionsUI.sender()
        btntxt = spinBTN.text()
        if btntxt == "Spin On":
            self._spinTimer.stop()
            spinBTN.setText("Spin Off")
        else:
            self._spinTimer.start()
            spinBTN.setText("Spin On")
        
    def actionStartSimulation(self):
        if not self._vpAppTimer:
            self._vpAppTimer = vispyApp.Timer(self._frameRate, start=False)
            self._vpAppTimer.connect(self._vpAppTimerCB)
        else:
            self._vpAppTimer.disconnect()
            self._vpAppTimer = vispyApp.Timer(self._frameRate, start=False)
            self._vpAppTimer.connect(self._vpAppTimerCB)

        if self._frameMode == "Merge":
            self._gravity.detectCollisions(True)

        if self._vpAppTimer:
            self._vpAppTimer.start()
            self._running =True
            if self._optionsUI:
                self._optionsUI.setRunning(self._running)
            
    def actionStopSimulation(self):
        if self._vpAppTimer and self._running:
            self._vpAppTimer.stop()
            self._running = False
            if self._optionsUI:
                self._optionsUI.setRunning(self._running)
             
    def advanceOneFrame(self, mode="add"):
        coll = self._gravity.jumpOneSecond()
        
        newPos = self._gravity.bodyPositions()
        bodySizes = self._gravity.bodySizes()
        bodyColors = self._gravity.bodyColors()
        if mode == "Add":
            newVis = vispyScene.visuals.Markers(pos=newPos,
                                                size=bodySizes,
                                                antialias=0,
                                                face_color=bodyColors,
                                                edge_color='white',
                                                edge_width=0,
                                                scaling=True,
                                                spherical=True)
            newVis.parent = self._vpView.scene

            self._trailLen += 1
            if self._trailLen > self._trailMax:
                subSceneKids = self._vpView.children[0].children
                if len(subSceneKids) > 2:
                    subSceneKids[2].parent = None

        elif mode != "Add" and self._firstMarkers:
            if coll:
                self._gravity.mergeBodies(coll[0], coll[1])
                self._makeBodyMarkers()
                title = f"GUTS - Merge({self._gravity.bodyCount()}) :"
                title = f"{title} Mass {coll[0]} collided with mass {coll[1]}"
                self._mainWin.setWindowTitle(title)
                self._gravity.detectCollisions(mode == "Merge")
                
            self._firstMarkers.set_data(pos=newPos, size=bodySizes,
                                        edge_width=0.0,
                                        edge_width_rel=None,
                                        edge_color='white',
                                        face_color=bodyColors,
                                        symbol='o')

            if mode == "Radii":
                for pos, rVis in zip(newPos, self._radiiVis):
                    #print("POS,VIS", pos, rVis)
                    pnts = numpy.array([ self._sceneOrigin, pos ])
                    rVis.set_data(pos=pnts)
            elif mode == "Trails":
                bodies = newPos.shape[0]
                if self._trails is None:
                    self._trails = newPos
                    return
                #print(f"TRAIL LEN: {self._trailLen}")
                if self._trailLen == 0:
                    newLen = self._trailLen + 1
                    newTrails = self._trails.reshape(bodies, newLen*3)
                    newTrails = numpy.concatenate((newTrails,newPos), axis=1)
                    self._trails = newTrails.reshape(bodies, newLen+1, 3)
                    self._trailLen += 1
                    self._trailVis = [ ]
                    parentVis = self._vpView.scene
                    for tdx, points in enumerate(self._trails):
                        trail = vispyScene.visuals.Line(pos=points,
                                                        color=bodyColors[tdx], #(1.0, 1.0, 0.0),
                                                        parent=parentVis,
                                                        width=0.5, method="gl",
                                                        antialias=True)
                        self._trailVis.append(trail)
                else:
                    newLen = self._trailLen + 1
                    newTrails = self._trails.reshape(bodies, newLen*3)
                    newTrails = numpy.concatenate((newTrails,newPos), axis=1)
                    self._trails = newTrails.reshape(bodies, newLen+1, 3)
                    self._trailLen += 1
                    if self._trailLen > self._trailMax:
                        # Delete first vertex of each trail vertex list
                        self._trails = numpy.delete(self._trails, 0, axis=1)
                        self._trailLen = self._trailMax
                    # update the trail points of each trail
                    for tvx, trailVis in enumerate(self._trailVis):
                        trailVis.set_data(pos=self._trails[tvx])

    def applyOptions(self, opts):
        self._optionsUI.applyOptions(opts)
                    
    def bodyCountChanged(self, value):
        self._bodyCount = value
        self._gravity.setBodyCount(value)

    def clearScene(self):
        viewKids = self._vpView.children
        subSceneKids = viewKids[0].children
        print(f"subSceneKids = {subSceneKids}")
        for mdx, obj in enumerate(subSceneKids):
            if mdx > 1:
                subSceneKids[mdx].parent = None

    def collDistChanged(self, value):
        self._gravity.setCollisiionDistance(value)

    def collisionDistance(self):
        return self._gravity.collisionDistance()

    def frameModeChanged(self, value):
        gravOpts = self._gravity.options()
        gravOpts.update({
            "frameRate" : self._frameRate,
            "trailMax"  : self._trailMax,
            "collDist"  : self.collisionDistance() })
        self._optStore.updateOptions(self._frameMode, gravOpts)
        self._frameMode = self._optionsUI.sender().currentText()
        
    def frameRateChanged(self, value):
        text = self._optionsUI.sender().currentText()
        rates = [1.0, 0.5, 0.25, 0.125, 0.0625, "auto"]
        self._frameRate = rates[value]

    def gravityConst(self):
        return self._gravity.gravitation()

    def gravityConstChanged(self, value):
        self._gravity.setGravitation(value)

    def massRange(self):
        return self._gravity.massRange()

    def positionRange(self):
        return self._gravity.positionRange()

    def setMainWin(self, mainWin):
        self._mainWin = mainWin
        self._vpView  = mainWin.vispyView()
        self._vpApp   = mainWin.vispyApp()

    def setMassRange(self, massMin, massMax):
        self._gravity.setMassRange(massMin, massMax)

    def setModel(self, model):
        self._gravity = model
        self._gravity.setBodyCount(3)

    def setPositionRange(self, posMin, posMax):
        self._gravity.setPositionRange(posMin, posMax)

    def setVelocityRange(self, velMin, velMax):
        self._gravity.setVelocityRange(velMin, velMax)

    def setTimer(self, vpAppTimer):
        self._vpAppTimer = vpAppTimer

    def setUIView(self, uiView):
        self._optionsUI = uiView
        
    def spinModeChanged(self, value):
        spinMode = self._optionsUI.sender().currentText()
        self._spinDeltas = self._spinModes[spinMode]

    def trailLengthChanged(self, value):
        self._trailMax = value

    def velocityRange(self):
        return self._gravity.velocityRange()


    def _makeBodyMarkers(self):
        if self._firstMarkers:
            self._firstMarkers.parent = None

        bodyPoses = self._gravity.bodyPositions()
        newVis = vispyScene.visuals.Markers(pos=bodyPoses,
                                size=self._gravity.bodySizes(),
                                antialias=0,
                                face_color=self._gravity.bodyColors(),
                                edge_color='white',
                                edge_width=0,
                                scaling=True,
                                spherical=True,
                                parent=self._vpView.scene)
        self._firstMarkers = newVis

    def _vpAppTimerCB(self, event):
        #print(f"Timer: blocked={event.blocked}, count={event.count} dt={event.dt}")
        #'elapsed', 'handled', 'iteration', 'native', 'source', 'sources', 'type'
        self.advanceOneFrame(self._frameMode)

    def _spinTimerCB(self, event):
#        print(f"_spinTimerCB: SA={self._spinAngles}")
        sa = self._spinAngles + self._spinDeltas
        sa %= 360.0
                                                      # roll,  pitch, yaw
#        viewAngle = Quaternion.create_from_euler_angles(sa[2], sa[0], sa[1], True)
        viewAngle =  Quaternion.create_from_euler_angles(sa[2], sa[1],
                                                         sa[0], True)
        self._vpView.camera.set_state({ "_quaternion": viewAngle })
        self._vpView.camera.view_changed()
        self._spinAngles = sa

    def _test1(self):
        print(f"ActionTest1")
        viewKids = self._vpView.children
        print(f"VIEW:  .children {viewKids}")
        subSceneKids = viewKids[0].children
        print(f"VIEW:  .children.children {viewKids[0].children}")
        if len(subSceneKids) > 2:
            print(f"Markers: {subSceneKids[2].children}")
            print(f"VIEW.scene.children: {self._vpView.scene.children}")
            print(f"VIEW.scene.children[2].children: {self._vpView.scene.children[2].children}")
            print(f"MARKERS.pos: {dir(subSceneKids[2])}")
        #    markers = obj

        bodyPoses = self._gravity.bodyPositions()
#        linePos = numpy.array([ [-30.0, -30.0, -30.0], [30.0, 30.0, 30.0] ])
#        axisPos = numpy.array([ [-30.0, 0.0, 0.0], [30.0, 0.0, 0.0],
#                                [0.0, -30.0, 0.0], [0.0, 30.0, 0.0],
#                                [0.0, 0.0, -30.0], [0.0, 0.0, 30.0] ])
#        line = vispyScene.visuals.Line(pos=axisPos, color=(1.0, 1.0, 0.0),
#                          parent=self._vpView.scene, width=4.0, method="gl",
#                          antialias=True)
        origin = numpy.array([0.0, 0.0, 0.0])
        self._radiiVis = [ ]
        for pos in bodyPoses:
            radii = numpy.array([origin, pos])
            line = vispyScene.visuals.Line(pos=radii, color=(1.0, 1.0, 0.0),
                                           parent=self._vpView.scene, width=0.5, method="gl",
                                           antialias=True)
            self._radiiVis.append(line)


    def _test2(self):
        if self._t2Marker:
            print(self._t2Marker)
#            self._t2Marker.set_data(pos=numpy.array([[100.0, 100.0, 100.0], [0.s0, 0.0, 0.0]]))
            self._t2Marker.set_data(pos=numpy.array([[0.0, 0.0, 0.0]]), size=40.0)
            #set_data(pos=None, size=10.0, edge_width=1.0, edge_width_rel=None, edge_color='black', face_color='white', symbol='o')

    def _test3(self):
        print("TEST 3: ")
        props = self._vpView.camera.get_state()
        print(props)
        print(props["_quaternion"], id(props["_quaternion"]))
        newProps = { "_quaternion": Quaternion(1, 0, 0, 0.5) }
        print("self._vpView.transform", self._vpView.transform)
        print("self._vpView.camera.transform", self._vpView.camera.transform)
        print("self._vpView.camera.transform.matrix", self._vpView.camera.transform.matrix)
#        self._vpView.camera.set_state(newProps)
#        self._vpView.camera.view_changed()
#You should be able to call `app.process_events()` to force an update.
        return
        mtxrot.rotate(0.2 ** 0.5, (1, 0, 0))
        mtxrot.rotate(0.3 ** 0.5, (0, 1, 0))
        mtxrot.rotate(0.5 ** 0.5, (0, 0, 1))
        self._vpView.update()
