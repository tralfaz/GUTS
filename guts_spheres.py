import random
import sys

import numpy

from vispy import app as vispyApp
from vispy import scene as vispyScene
from vispy.visuals.transforms import STTransform


def ArgbToRgba(argb):
    return argb[0] + argb[3:] + argb[1:3]

def RgbaToArgb(rgba):
    return rgba[0] + rgba[7:] + rgba[1:7]

def RandomRGBA():
    rgba = [f"{random.randrange(0, 256):02X}" for _ in range(4)]
    return "#" + "".join(rgba)

def RandomRGBA2():
    rgba = [f"{random.randrange(0, 256):02X}" for _ in range(3)]
    rgba.append(f"{random.randrange(128, 256):02X}")
    return "#" + "".join(rgba)


class Sphere(object):
    
    def __init__(self, vpSphere, method, radius=1.0,
                 shading=None, face=None, edge=None,
                 icoSubdivs=3,
                 cubeRows=10, cubeCols=10, cubeDepth=10):
        self.vpSphere = vpSphere
        self.method   = method
        self.shading  = shading 
        self.face     = face if face else RandomRGBA()
        self.edge     = edge if edge else RandomRGBA()
        self.pos      = numpy.array([0.0, 0.0, 0.0, 0.0], numpy.float32)
        self.scale    = numpy.array([1.0, 1.0, 1.0, 1.0], numpy.float32)
        self.selected = False

    def move(self, xpos, ypos, zpos):
        self.vpSphere.transform = STTransform(scale=self.scale,
                                              translate=[xpos,ypos,zpos])
        self.pos = self.vpSphere.transform.translate
#        self.pos = numpy.array([xpos, ypos, zpos, 0.0], numpy.float32)

    def translate(self, pos):
#        self.vpSphere.transform = STTransform(scale=self.scale,
#                                              translate=pos)
#        self.pos = self.vpSphere.transform.translate
#        self.pos = numpy.array([xpos, ypos, zpos, 0.0], numpy.float32)
        self.pos = pos
        self.vpSphere.transform.translate = self.pos
        self.vpSphere.transform.update()

    def moveX(self, xpos):
        self.pos[0] = xpos
        self.vpSphere.transform = STTransform(translate=self.pos)

    def moveY(self, ypos):
        self.pos[2] = ypos
        self.vpSphere.transform = STTransform(translate=self.pos)

    def moveZ(self, zpos):
        self.pos[1] = zpos
        self.vpSphere.transform = STTransform(translate=self.pos)

    def scaleAll(self, scale):
        self.vpSphere.transform = STTransform(scale=[scale,scale,scale],
                                              translate=self.pos)
        self.scale = self.vpSphere.transform.scale

        

class OrbStore(object):

    def __init__(self, viewScene):
        self._viewScene = viewScene
        self._orbs = []

    def addOrb(self,
               radius=1.0, method="latitude",
               shading=None, face=None, edge=None,
               scale=None, pos=None,
               icoSubdivs=3,
               cubeRows=10, cubeCols=10, cubeDepth=10):

        if method == "latitude":
            vpSphere = vispyScene.visuals.Sphere(parent=self._viewScene,
                                                 radius=radius,
                                                 method=method,
                                                 shading=shading,
                                                 color=face,
                                                 edge_color=edge)
        elif method == "ico":
            vpSphere = vispyScene.visuals.Sphere(parent=self._viewScene,
                                                 radius=radius,
                                                 method=method,
                                                 shading=shading,
                                                 color=face,
                                                 edge_color=edge,
                                                 subdivisions=icoSubdivs)
        elif method == "cube":
            vpSphere = vispyScene.visuals.Sphere(parent=self._viewScene,
                                                 radius=radius,
                                                 method=method,
                                                 shading=shading,
                                                 color=face,
                                                 edge_color=edge,
                                                 rows=cubeRows,
                                                 cols=cubeCols,
                                                 depth=cubeDepth)
        else:
            return
        vpSphere.transform = STTransform(scale=scale, translate=[0.0,0.0,0.0])
        
        orb = Sphere(vpSphere, method, radius,
                  shading, face, edge,
                  icoSubdivs,
                  cubeRows, cubeCols, cubeDepth)
        self._orbs.append(orb)

        return orb

    def get(self, odx):
        return self._orbs[odx]

    def moveSpheres(self, newPos):
        newPos2 = numpy.append(newPos, self._newPosCol4, axis=1)
#        for pos,sphere in zip(newPos2, self._orbs):
#            sphere.translate(pos)
        for sdx,sphere in enumerate(self._orbs):
            sphere.translate(newPos2[sdx])

    def newSpheres(self, positions, colors, sizes):
        # Delete old spheres from vispy scene
        for orb in self._orbs:
            orb.vpSphere.parent = None
        self._orbs = []

#        print(f"newSpheres:\n   {positions=}\n   {colors=}\n    {sizes=}")
        for sdx in range(len(positions)):
            pos = positions[sdx]
            scale = numpy.array([1.0, 1.0, 1.0, 1.0], numpy.float32)
            scale *= sizes[sdx]
            orb = self.addOrb(radius=1.0, method="ico",
                              shading="smooth",
                              face=RandomRGBA2(), edge=RandomRGBA2(),
                              scale=scale, pos=positions[sdx],
                              icoSubdivs=3)
            orb.move(pos[0], pos[1], pos[2])
            orb.scaleAll(sizes[sdx])
#            print(f"ORB: {positions[sdx]}")

        self._newPosCol4 = numpy.zeros((len(positions),1), numpy.float32)

        return self._orbs
       
    def orbList(self):
        return self._orbs
