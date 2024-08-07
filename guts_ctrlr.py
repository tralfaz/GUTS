import math
import sys

import gravity
import optstore

import numpy
from vispy import app   as vispyApp
from vispy import scene as vispyScene
from vispy.util.quaternion import Quaternion


import vispy
import vispy.scene.visuals# .Markers
#import vispy.scene.visuals.Line

class GutsController(object):

    def __init__(self):
        super().__init__()

        self._vpApp      = None

        self._gravity = None
        
        self._spinSwitch  = "Spin Off"
        self._spinAngles  = numpy.array([0.0, 0.0, 0.0])
        self._spinMode    = "X"
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
        self._frameAction = self._frameActionMove
        
        self._firstMarkers = None

        self._optStore = optstore.OptionsStore()

        self._optionsUI = None
        
        self._vpAppTimer = vispyApp.Timer(self._frameRate, start=False)
        self._vpAppTimer.connect(self._vpAppTimerCB)
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
        #print(f"actionDeleteOldestMarker")
        viewKids = self._vpView.children
        subSceneKids = viewKids[0].children
        #print(f"subSceneKids = {subSceneKids}")
        for mdx, obj in enumerate(subSceneKids):
            #print(type(obj))
            if type(obj) is vispyScene.visuals.Markers:
                break
        #print(f"MDX: {mdx}")
        if mdx > 0:
            subSceneKids[mdx].parent = None

    def actionJumpOneSecond(self):
        self.advanceOneFrame(self._frameMode)

    def actionNewSimulation(self):
        if self._running:
            return
         
        self.clearScene()
        self._gravity.setBodyCount(self._bodyCount)
        self._gravity.detectCollisions(self._frameMode == "Merge")

        self._orbStore = self._mainWin.orbStore()

        self._radiiVis = None
        self._trails = None
        self._trailLen = 0
        self._trailVis = None
        self._tubeColors = None
        self._tubeSizes  = None
        
        if self._frameMode == "Cloud":
            self._gravity.setBodyCount(self._bodyCount*100)
        else:
            self._gravity.setBodyCount(self._bodyCount)
            
        self._gravity.createRandomBodies()
        #self._gravity.printState()

        bodyPoses = self._gravity.bodyPositions()
        self._makeBodyMarkers()

        if self._frameMode == "Cloud":
            self._frameAction = self._frameActionCloud
            
        elif self._frameMode == "Move":
            self._frameAction = self._frameActionMove
            
        elif self._frameMode == "Merge":
            self._frameAction = self._frameActionMerge
            
        elif self._frameMode == "Radii":
            self._frameAction = self._frameActionRadii
            self._radiiVis = [ ]
            for pos in bodyPoses:
                radii = numpy.array([self._sceneOrigin, pos])
                line = vispyScene.visuals.Line(pos=radii, color=(1.0, 1.0, 0.0),
                                               parent=self._vpView.scene,
                                               width=0.5, method="gl",
                                               antialias=True)
                self._radiiVis.append(line)

        elif self._frameMode == "Snakes":
            self._frameAction = self._frameActionSnakes

        elif self._frameMode == "Spheres":
            self._frameAction = self._frameActionSpheres

        elif self._frameMode == "SphereTrails":
            self._frameAction = self._frameActionSpheresWithTrails

        elif self._frameMode == "Trails":
            self._frameAction = self._frameActionTrails
            self._trails = numpy.array(self._gravity.bodyPositions())
        
        elif self._frameMode == "Tubular":
            self._frameAction = self._frameActionTubular
            self._trails = numpy.array(self._gravity.bodyPositions())
        
        self._optionsUI.setRunning(False)

        self._mainWin.setWindowTitle("GUTS - %s(%s)" %
                                     (self._frameMode, bodyPoses.shape[0]))

    def actionQuit(self):
        if self._vpApp:
            self._vpApp.quit()

    def actionSaveOptions(self):
        self._stashOptions(self._frameMode)
        optPath = self._optStore.findDefaultPath()
        self._optStore.writeOptions(optPath)

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
        if self._gravity.bodyPositions() is None:
            return  # No simulation ready
        if self._frameMode == "Merge":
            self._gravity.detectCollisions(True)
        self._running = True
        if self._optionsUI:
            self._optionsUI.setRunning(self._running)
        self._vpAppTimer.start()
            
    def actionStopSimulation(self):
        if self._running:
            self._vpAppTimer.stop()
            self._running = False
            if self._optionsUI:
                self._optionsUI.setRunning(self._running)
             
    def advanceOneFrame(self, mode="add"):
        self._frameAction()

    def _frameActionCloud(self):
        coll = self._gravity.jumpOneSecond()
        newPos = self._gravity.bodyPositions()

        self._firstMarkers.set_data(pos=newPos,
                                    size=5.0,
                                    face_color=self._cloudRGBA,
                                    edge_color=None)

    def _frameActionMerge(self):
        coll       = self._gravity.jumpOneSecond()
        newPos     = self._gravity.bodyPositions()
        bodySizes  = self._gravity.bodySizes()
        bodyColors = self._gravity.bodyColors()

        if coll:
            self._gravity.mergeBodies(coll[0], coll[1])
            self._makeBodyMarkers()
            title = f"GUTS - Merge({self._gravity.bodyCount()}) :"
            title = f"{title} Mass {coll[0]} collided with mass {coll[1]}"
            self._mainWin.setWindowTitle(title)
#            self._gravity.detectCollisions(self._frameMode == "Merge")
                
        self._firstMarkers.set_data(pos=newPos, size=bodySizes,
                                    edge_width=0.0,
                                    edge_width_rel=None,
                                    edge_color='white',
                                    face_color=bodyColors,
                                    symbol='o')

    def _frameActionMove(self):
        coll = self._gravity.jumpOneSecond()
        newPos = self._gravity.bodyPositions()
        bodySizes = self._gravity.bodySizes()
        bodyColors = self._gravity.bodyColors()

        self._firstMarkers.set_data(pos=newPos, size=bodySizes,
                                    edge_width=0.0,
                                    edge_width_rel=None,
                                    edge_color='white',
                                    face_color=bodyColors,
                                    symbol='o')

    def _frameModeNull(self):
        pass
    
    def _frameActionRadii(self):
        coll = self._gravity.jumpOneSecond()
        newPos = self._gravity.bodyPositions()
        bodySizes = self._gravity.bodySizes()
        bodyColors = self._gravity.bodyColors()

        self._firstMarkers.set_data(pos=newPos, size=bodySizes,
                                    edge_width=0.0,
                                    edge_width_rel=None,
                                    edge_color='white',
                                    face_color=bodyColors,
                                    symbol='o')
        
        for pos, rVis in zip(newPos, self._radiiVis):
            pnts = numpy.array([ self._sceneOrigin, pos ])
            rVis.set_data(pos=pnts)

    def _frameActionSnakes(self):
        coll       = self._gravity.jumpOneSecond()
        newPos     = self._gravity.bodyPositions()
        bodySizes  = self._gravity.bodySizes()
        bodyColors = self._gravity.bodyColors()

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

    def _frameActionSpheres(self):
        coll       = self._gravity.jumpOneSecond()
        newPos     = self._gravity.bodyPositions()
        self._orbStore.moveSpheres(newPos)

    def _frameActionSpheresWithTrails(self):
        coll       = self._gravity.jumpOneSecond()
        newPos     = self._gravity.bodyPositions()
        self._orbStore.moveSpheres(newPos)
        bodySizes = self._gravity.bodySizes()
        bodyColors = self._gravity.bodyColors()

        self._makeTracks(newPos, bodyColors, bodySizes)
        
    def _frameActionTrails(self):
        coll = self._gravity.jumpOneSecond()
        newPos = self._gravity.bodyPositions()
        bodySizes = self._gravity.bodySizes()
        bodyColors = self._gravity.bodyColors()

        self._firstMarkers.set_data(pos=newPos, size=bodySizes,
                                    edge_width=0.0,
                                    edge_width_rel=None,
                                    edge_color='white',
                                    face_color=bodyColors,
                                    symbol='o')
        self._makeTracks(newPos, bodyColors, bodySizes)

    def _frameActionTubular(self):
        coll = self._gravity.jumpOneSecond()
        newPos = self._gravity.bodyPositions()
        bodySizes = self._gravity.bodySizes()
        bodyColors = self._gravity.bodyColors()

        self._firstMarkers.set_data(pos=newPos, size=bodySizes,
                                    edge_width=0.0,
                                    edge_width_rel=None,
                                    edge_color='white',
                                    face_color=bodyColors,
                                    symbol='o')

        self._makeTubes(newPos, bodyColors, bodySizes)
            
    def bodyCountChanged(self, value):
        self._bodyCount = value
        self._gravity.setBodyCount(value)

    def clearScene(self):
        viewKids = self._vpView.children
        subSceneKids = viewKids[0].children
        for mdx, obj in enumerate(subSceneKids):
            if mdx > 1:
                if obj.name != "GUTSAxis":
                    subSceneKids[mdx].parent = None

    def collDistChanged(self, value):
        self._gravity.setCollisiionDistance(value)

    def collisionDistance(self):
        return self._gravity.collisionDistance()

    def frameModeChanged(self, value):
        self._stashOptions(self._frameMode)
        self._frameMode = self._optionsUI.sender().currentText()
        opts = self._restoreOptions(self._frameMode)

    def frameRateChanged(self, value):
        text = self._optionsUI.sender().currentText()
        rates = [1.0, 0.5, 0.25, 0.125, 0.0625, 1.0/60.0]
        self._frameRate = rates[value]
        if self._vpAppTimer:
            self._vpAppTimer.interval = self._frameRate
        
    def gravityConst(self):
        return self._gravity.gravitation()

    def gravityConstChanged(self, value):
        self._gravity.setGravitation(value)

    def massRange(self):
        return self._gravity.massRange()

    def positionRange(self):
        return self._gravity.positionRange()

    def recoverOptions(self):
        if len(sys.argv) > 1:
            optPath = sys.argv[1]
            defaultPath = False
        else:
            optPath = self._optStore.findDefaultPath()
            defaultPath = True
        opts = None
        try:    
            opts = self._optStore.readOptions(optPath)
        except FileNotFoundError as fnfx:
            if not defaultPath:
                print(f"GUTS ERROR: Option file not found: {fnfx.filename}")
        except PermissionError as prmx:
            print(f"GUTS ERROR: Can't read options file: {prmx.filename}")
        except:
            print(f"GUTS ERROR: Reading options file: {sys.exc_info()}")

        if opts:
            self._optStore.setCurrentOptions(opts)
            self._restoreOptions(self._frameMode)

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
        self._spinMode = self._optionsUI.sender().currentText()
        self._spinDeltas = self._spinModes[self._spinMode]

    def trailLengthChanged(self, value):
        self._trailMax = value
        
    def velocityRange(self):
        return self._gravity.velocityRange()

    def _makeBodyMarkers(self):
        if self._firstMarkers:
            if type(self._firstMarkers) is list:
                for marker in self._firstMarkers:
                    marker.parent = None
            else:
                self._firstMarkers.parent = None

        bodyPoses  = self._gravity.bodyPositions()
        bodyColors = self._gravity.bodyColors()
        if self._frameMode == "Cloud":
            alpha = numpy.ones((bodyColors.shape[0],1)) * 0.5
            self._cloudRGBA = numpy.hstack([bodyColors, alpha])
            newVis = vispyScene.visuals.Markers(parent=self._vpView.scene)
            newVis.set_data(pos=bodyPoses,
                            size=5.0,
                            face_color=self._cloudRGBA,
                            edge_color=None)
        elif self._frameMode in ("Spheres", "SphereTrails"):
            orbStore = self._mainWin.orbStore()
            newVis = orbStore.newSpheres(positions=bodyPoses,
                                         colors=bodyColors,
                                         sizes=self._gravity.bodySizes())
            
        else:
            newVis = vispyScene.visuals.Markers(pos=bodyPoses,
                                                size=self._gravity.bodySizes(),
                                                antialias=0,
                                                face_color=bodyColors,
                                                edge_color='white',
                                                edge_width=0,
                                                scaling=True,
                                                spherical=True,
                                                parent=self._vpView.scene)
        self._firstMarkers = newVis

    def _makeTracks(self, bodyPoses, bodyColors, bodySizes):
        bodyCount = bodyPoses.shape[0]
        
        if self._trailLen == 0:
            self._trails = numpy.array(bodyPoses)
            newLen    = 1
            newTrails = self._trails.reshape(bodyCount, newLen*3)
            newTrails = numpy.concatenate((newTrails,bodyPoses), axis=1)
            self._trails = newTrails.reshape(bodyCount, newLen+1, 3)
            self._trailLen += 1
            self._trailVis = [ ]
            parentVis = self._vpView.scene
        
            for tdx, endPoints in enumerate(self._trails):
                newVis = vispyScene.visuals.Line(pos=endPoints,
                                                 color=bodyColors[tdx],
                                                 width=0.5, method="gl",
                                                 antialias=True,
                                                 parent=parentVis)
                self._trailVis.append(newVis)

        else:
            # extending trails one segment, erase oldest segments > max
            pntCount = self._trailLen + 1    # trailLen to point count
            # Change bodyCount x pntCount x 3 3D array to 2D
            newTrails = self._trails.reshape(bodyCount, pntCount*3)

            # extend each 1D x0,y0,z0,x1,y1,z1 array by one xyz point
            newTrails = numpy.concatenate((newTrails,bodyPoses), axis=1)

            # Reshape extended 2D array back to 3D
            self._trails = newTrails.reshape(bodyCount, pntCount+1, 3)
            self._trailLen += 1
            if self._trailLen > self._trailMax:
                # Delete first vertex of each trail vertex list
                self._trails = numpy.delete(self._trails, 0, axis=1)
                self._trailLen = self._trailMax

            # update each existing trail visual with new 3D line data
            for tvx, trailVis in enumerate(self._trailVis):
                trailVis.set_data(pos=self._trails[tvx])
                
    def _makeTubes(self, bodyPoses, bodyColors, bodySizes):
        bodyCount = bodyPoses.shape[0]

        if self._trailLen == 0:
            # create tube heads
            newLen = self._trailLen + 1
            newTrails = self._trails.reshape(bodyCount, newLen*3)
            newTrails = numpy.concatenate((newTrails,bodyPoses), axis=1)
            self._trails = newTrails.reshape(bodyCount, newLen+1, 3)
            self._trailLen += 1
            self._trailVis = [ ]
            parentVis = self._vpView.scene
        
            # Add alpha to colors for tube colors
            alpha = numpy.ones((bodyCount, 1)) * 0.5
            self._tubeColors = numpy.hstack( (bodyColors, alpha) )
            self._tubeSizes  = bodySizes / 4.0
            
            for tdx, endPoints in enumerate(self._trails):
                newVis = vispyScene.visuals.Tube(points=endPoints,
                                                 color=self._tubeColors[tdx],
                                                 radius=5.0,
                                                 parent=parentVis)
                self._trailVis.append(newVis)
                
        else:
            # extend tubes
            # Need to create new visuals, then delete previous vis (for now)
            if self._trailLen % 2 == 0:
                self._trailLen += 1
                return  #only every other position
            pntCount = (self._trailLen+1) // 2 + 1
            newTrails = self._trails.reshape(bodyCount, pntCount*3)
            newTrails = numpy.concatenate((newTrails,bodyPoses), axis=1)
            self._trails = newTrails.reshape(bodyCount, pntCount+1, 3)
            self._trailLen += 1
            if self._trailLen > self._trailMax:
                # Delete first vertex of each trail vertex list
                self._trails = numpy.delete(self._trails, 0, axis=1)
                self._trailLen = self._trailMax

            newTrails = []
            for tvx, trailVis in enumerate(self._trailVis):
                newVis = vispyScene.visuals.Tube(points=self._trails[tvx],
                                                 color=self._tubeColors[tvx],
                                                 radius=self._tubeSizes[tvx],
                                                 parent=self._vpView.scene)
                trailVis.parent = None
                newTrails.append(newVis)
            self._trailVis = newTrails

    def _restoreOptions(self, mode):
        opts = self._optStore.options(mode)
        self._optionsUI.applyOptions(opts)

    def _spinTimerCB(self, event):
#        print(f"_spinTimerCB: SA={self._spinAngles}")
        sa = self._spinAngles + self._spinDeltas
        sa %= 360.0
                                                         # roll,  pitch, yaw
        viewAngle =  Quaternion.create_from_euler_angles(sa[2], sa[1], sa[0], True)
        self._vpView.camera.set_state({ "_quaternion": viewAngle })
        self._vpView.camera.view_changed()
        self._spinAngles = sa

    def _stashOptions(self, mode):
        opts = { optstore.BODY_COUNT: self._bodyCount,
                 optstore.GRAV_CONST: self.gravityConst(),
                 optstore.MASS_RANGE: self.massRange(),
                 optstore.POS_RANGE:  self.positionRange(),
                 optstore.VEL_RANGE:  self.velocityRange(),
                 optstore.FRAME_RATE: self._frameRate,
                 optstore.SPIN_MODE:  self._spinMode,
                 optstore.TRAIL_LEN:  self._trailMax,
                 optstore.COLL_DIST:  self.collisionDistance() }
        self._optStore.updateOptions(mode, opts)
        
    def _vpAppTimerCB(self, event):
        #print(f"Timer: blocked={event.blocked}, count={event.count} dt={event.dt}")
        #'elapsed', 'handled', 'iteration', 'native', 'source', 'sources', 'type'
        self.advanceOneFrame(self._frameMode)

    def _testCB(self):
        self._test1()

    def _test1(self):
        print(f"Test1")
        viewKids = self._vpView.children
        print(f"VIEW:.children {viewKids}")
        subScene = viewKids[0]
        print(f"SubScene: {dir(subScene)}")
        subSceneKids = viewKids[0].children
        print(f"SubScene:.children {subScene.children}")
        for vis in subScene.children:
            print(f"Child Type: {type(vis)}")
            if type(vis) is vispy.scene.visuals.Markers:
                print(f"dir(Markers): {dir(vis)}")
                print(f"Markers.children: {vis.children}")
            if type(vis) is vispy.scene.visuals.Line:
                print(f"dir(Line): {dir(vis)}")
                print(f"Line.pos: {vis.pos}")
        if len(subSceneKids) > 2:
            print(f"Markers: {subSceneKids[2].children}")
            print(f"VIEW.scene.children: {self._vpView.scene.children}")
            print(f"VIEW.scene.children[2].children: {self._vpView.scene.children[2].children}")
            print(f"MARKERS.pos: {dir(subSceneKids[2])}")
        #    markers = obj

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
