import gravity

import numpy
from vispy import app   as vispyApp
from vispy import scene as vispyScene

class GutsController(object):

    def __init__(self):
        super().__init__()

        self._vpApp      = None
        self._vpAppTimer = None

        self._gravity = None

        self._frameMode = "Move"
        self._frameRate = 0.25
        
        self._firstMarkers = None

        self._optionsUI = None
        
        self._running = False
        self._sceneOrigin = numpy.array([0.0, 0.0, 0.0])

        self._trailMax = 1000
        self._trailVis = None

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
        self._gravity.jumpOneSecond()
#        self._gravity.printState()
        newVis = vispyScene.visuals.Markers(pos=self._gravity.bodyPositions(),
                                       size=self._gravity.bodySizes(),
                                       antialias=0,
                                       face_color=self._gravity.bodyColors(),
                                       edge_color='white',
                                       edge_width=0,
                                       scaling=True,
                                       spherical=True)
        newVis.parent = self._vpView.scene

    def actionNewSimulation(self):
        if self._running:
            return
         
        self.clearScene()
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
                title = f"Mass {coll[0]} collided with mass {coll[1]}"
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
                    
    def bodyCountChanged(self, value):
        self._gravity.setBodyCount(value)
        
    def collDistChanged(self, value):
        self._gravity.setCollisiionDistance(value)
 
    def frameModeChanged(self, value):
        self._frameMode = self._optionsUI.sender().currentText()
        
    def frameRateChanged(self, value):
        text = self._optionsUI.sender().currentText()
        rates = [1.0, 0.5, 0.25, 0.125, 0.0625, "auto"]
        self._frameRate = rates[value]

    def ActionTest1(self):
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


    def ActionTest2(self):
        if self._t2Marker:
            print(self._t2Marker)
#            self._t2Marker.set_data(pos=numpy.array([[100.0, 100.0, 100.0], [0.s0, 0.0, 0.0]]))
            self._t2Marker.set_data(pos=numpy.array([[0.0, 0.0, 0.0]]), size=40.0)
            #set_data(pos=None, size=10.0, edge_width=1.0, edge_width_rel=None, edge_color='black', face_color='white', symbol='o')

    def clearScene(self):
        viewKids = self._vpView.children
        subSceneKids = viewKids[0].children
        #print(f"subSceneKids = {subSceneKids}")
        for mdx, obj in enumerate(subSceneKids):
            if mdx > 1:
                subSceneKids[mdx].parent = None

    def collisionDistance(self):
        return self._gravity.collisionDistance()

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
