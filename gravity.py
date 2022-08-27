import math

import numpy

# Gravitation Constant
G = 2.0 * 6.672e-4  # N * m^2 / kg^2


class Gravity(object):

    def __init__(self):
        super().__init__()

        self._bodyCount = 0

        self._positions  = None
        self._velocities = None
        self._masses     = None

        self._posRange = (-200.0, 200.0)   # Body XYZ position rand range (m)
        self._velRange = (-0.2, 0.2)       # Body XYZ velocity rand range (m/s)
        self._massRange = (4500.0, 5000.0) # Body mass rand range (Kg)

        self._time = 0    # seconds

        self._collisionDist = 5.0          # Distance threshold for collision
        self._collisionIndexes = None      # Indexes of colliding bodies
        self._collisionDetect  = False     # Whether to look for collisions

    def bodyColors(self):
        return self._colors

    def bodyCount(self):
        return self._bodyCount
    
    def bodyPositions(self):
        return self._positions
    
    def bodySizes(self):
        return self._sizes
    
    def collisionDistance(self):
        return self._collisionDist

    def createRandomBodies(self):
        self._massForces = None
        
        # Create 3D random body positions (Xm, Ym, Zm)
        self._positions = numpy.random.rand(self._bodyCount, 3)
        self._positions *= (self._posRange[1] - self._posRange[0])
        self._positions += self._posRange[0]

        # Create 3D random body velocity vectors (Xm/s, Ym/s, Zm/s)
        self._velocities = numpy.random.rand(self._bodyCount, 3)
        self._velocities *= (self._velRange[1] - self._velRange[0])
        self._velocities += self._velRange[0]

        # Create random body masses (Kg)
        self._masses = numpy.random.rand(self._bodyCount)
        self._masses *= (self._massRange[1] - self._massRange[0])
        self._masses += self._massRange[0]

        # Create colors and sizes body visuals
        mSizer = numpy.vectorize(self.massToSize)
        self._sizes = mSizer(self._masses)
        self._colors = numpy.random.rand(self._bodyCount, 3)

        # Set centroid mass
#        self._positions[0]  *= 0.0
#        self._velocities[0] *= 0.0

    def detectCollisions(self, value):
        self._collisionDetect = value

    def printState(self):
        print(f"TIME = {self._time}")
        print(f"POSITIONS:\n", self._positions)
        print(f"VELOCITIES: {self._velocities}")
        print(f"MASSES: {self._masses}")
        print(f"FORCES: {self._massForces}")

    def jumpOneSecond(self):
        """Sum 3D forces on mass bodies, then update each body position and
        velocities.
        """
        self.sumForces()
        if not self._collisionIndexes is None:
            cdx = self._collisionIndexes
            self._collisionIndexes = None
            self._collisionDetect  = False
            return cdx

        # [[f0X, f0Y, f0Z],[f1X, f1Y, f1Z], ...] / [[m0], [m1], ...]
        #
        accel3D = self._massForces / self._masses[:, numpy.newaxis]

        # Determine new mass positions
        # posXYZ + velXYZ + (accelXYZ / 2.0)
        accel3D2 = accel3D / 2.0
        newPos3D = self._positions + self._velocities + accel3D2

        # final velocity = initial velocity + acceleration * time(=1)
        newVel3D = self._velocities + accel3D

        # set updated positions
        self._positions  = newPos3D

        # set updated velocities
        self._velocities = newVel3D

        self._time += 1

    def massToSize(self, mass):
        """Mass marker size kept in range from 10 - 60"""
        mMin, mMax = self._massRange
        return 10.0 + (mass-mMin) / ((mMax-mMin) / 50.0)
    
    def massRange(self):
        return self._massRange

    def mergeBodies(self, b1Index, b2Index):
        """Merge two colliding bodies.  Add masses, combine velocities with
        each bodies momentum, add volumes to determine new size, combine
        colors"""
        mass1 = self._masses[b1Index]
        mass2 = self._masses[b2Index]
        newMass = mass1 + mass2
        
        vel1 = self._velocities[b1Index]
        vel2 = self._velocities[b2Index]
        newVel = (mass1 * vel1 + mass2 * vel2) / newMass
        
        size1 = self._sizes[b1Index]
        size2 = self._sizes[b2Index]
        newSize = math.pow(size1,3) + math.pow(size2,3) 
        newSize = math.pow(newSize, 1.0/3.0)

        color1 = self._colors[b1Index]
        color2 = self._colors[b2Index]
        newColor  = (color1 + color2) / 2.0

        if mass1 > mass2:
            updIndex, delIndex = b1Index, b2Index
        else:
            updIndex, delIndex = b2Index, b1Index
        self._masses[updIndex] = newMass
        self._masses = numpy.delete(self._masses, delIndex)
        self._velocities[updIndex] = newVel
        self._velocities = numpy.delete(self._velocities, delIndex, axis=0)
        self._sizes[updIndex] = newSize
        self._sizes = numpy.delete(self._sizes, delIndex)
        self._colors[updIndex] = newColor
        self._colors = numpy.delete(self._colors, delIndex, axis=0)
        self._positions = numpy.delete(self._positions, delIndex, axis=0)
        self._bodyCount -= 1
        
    def positionRange(self):
        return self._posRange

    def setCollisiionDistance(self, dist):
        self._collisionDist = float(dist)

    def setBodyCount(self, count):
        self._bodyCount = count

    def setMassRange(self, massMin, massMax):
        self._massRange = (massMin, massMax)

    def setPositionRange(self, posMin, posMax):
        self._posRange = (posMin, posMax)

    def setVelocityRange(self, velMin, velMax):
        self._velRange = (velMin, velMax)

    def sumForces(self):
        """
        Sum forces for each body.  For each body in make it m2 [v2x, v2y, v2z].
        Then create lists of other masses and positions [m1, m3, m4, ...]
        [ [x1, y1, z1], [x3, y3, z3], [x4, y4, z4], ...].  Then calculate
        distances between current body and other bodies [d1, d3, d4, ...].
        Then build a list of vector normals between current body and all other
        bodies [ [n1x, n1y, n1z], [n3x, n3y, n3z], [n4x, n4y, n4z], ...].
        Then calculate the 3D gravitational force between this mass and other
        bodies.
          m2 * other masses:
            [[m2m1x,m2m1y,m2m1z],[m2m3x,m2m3y,m2m3z],[m2m4x,m2m4y,m2m4z] ...]
          m2 * other masses / other distances
            [[m2m1x,m2m1y,m2m1z]/m2m1d,[m2m3x,m2m3y,m2m3z]/m2m3d,
             [m2m4x,m2m4y,m2m4z]/m2m3d ...]
        Then calculate pull of other masses on current mass
          m2 * other masses / other distances * -G
            [[m2m1x,m2m1y,m2m1z]/m2m1d,[m2m3x,m2m3y,m2m3z]/m2m3d,
             [m2m4x,m2m4y,m2m4z]/m2m3d ...] * -G
        Lastly sum 3D force vectors of all ther bodies
            [m2m1x,m2m1y,m2m1z]/m2m1d] + [m2m3x,m2m3y,m2m3z]/m2m3d] +
            [m2m4x,m2m4y,m2m4z]/m2m3d ...] * -G
        End result list of forceSums for each body
           [ [F1x,F1y,F1z], [F2x,F2y,F2z], [F3x,F3y,F3z], [F4x,F4y,F4z], ...] 
        """
        self._massForces = numpy.array([])
        detectCollision = self._collisionDetect

        # For each body calculate gravitatational force vectors of ather bodies
        #    F = G * m1 * m2 / d ** 2
        for bdx, mass2 in enumerate(self._masses):
            # Make this body m2 and v2
            m2Pos = self._positions[bdx]
            m2Vel = self._velocities[bdx]
            #print(f"MASS2 {mass2}  m2Pos={m2Pos}  m2Vel={m2Vel}")

            # Lists of other masses and other velocity vectors
            otherMasses = numpy.delete(self._masses, bdx)
            otherPoses  = numpy.delete(self._positions, bdx, axis=0)
            #print(f"OTHER MASSES = {otherMasses}  OTHER POSES = {otherPoses}")

            # Get normalized vectors from current body to other bodies
            m21Vecs = m2Pos - otherPoses
            #print(f"m21Vecs {m21Vecs}")
            m21Dists = numpy.linalg.norm(m21Vecs, axis=1)
            #print(f"m21Dists = {m21Dists}  {m21Dists[:, numpy.newaxis]}")
            m21Norms = m21Vecs / m21Dists[:, numpy.newaxis]
            #print(f"m21Norms = {m21Norms}")

            # if collision detection enabled, check distances
            if detectCollision:
                cds = numpy.where(m21Dists < self._collisionDist)
                if cds[0].shape[0] > 0:
                    cdx = cds[0][0]
                    if cdx >= bdx:
                        cdx += 1
                    self._collisionIndexes = bdx, cdx
                    detectCollision = False

            # Get vector forces between current mass and other masses 
            m2m1s = mass2 * otherMasses
            #print(f"m2m1s = {m2m1s}")
            m2m1r1s = m2m1s / m21Dists
            #print(f"m2m1r1s = {m2m1r1s}")
            m2fxyz = m2m1r1s[:, numpy.newaxis] * m21Norms
            #print(f"m2fxyz = {m2fxyz}")

            # Sum the list of force vectors
            m2fsum = numpy.sum(m2fxyz, axis=0)
            #print(f"m2fsum = {m2fsum}")

            # Multiply force sums by gravitational constants to get
            # forces in Newtons
            m2GravVec = m2fsum * -G
            #print(f"m2GravVec = {m2GravVec}")
            self._massForces = numpy.append(self._massForces, m2GravVec)
            # for qdx

        # Rearrange force sums to list of 3D force vectors for each body
        #   [ [F1x, F1y, F1z], [F2x, F2y, F2z], ... ]
        self._massForces = self._massForces.reshape(-1,3)

    def velocityRange(self):
        return self._velRange

    

def normalize(v):
    norm = numpy.linalg.norm(v)
    if norm == 0:
       return v
    return v / norm



MASS_RANGE = (10.0, 50.0)
POSITION_RANGE = (-50.0, 50.0)
VELOCITY_RANGE = (-5.0, 5.0)

if __name__ == '__main__':
    nbodies = 5

    masses = numpy.random.rand(nbodies)
    masses *= (MASS_RANGE[1] - MASS_RANGE[0])
    masses += MASS_RANGE[0]
    print(f"MASSES: {masses}")

    positions = numpy.random.rand(nbodies, 3)
    positions *= (POSITION_RANGE[1] - POSITION_RANGE[0])
    positions += POSITION_RANGE[0]
    print(f"POSITIONS: {positions}")

    velocities = numpy.random.rand(nbodies, 3)
    velocities *= (VELOCITY_RANGE[1] - VELOCITY_RANGE[0])
    velocities += VELOCITY_RANGE[0]
    print(f"VELOCITIES: {velocities}")

    print(f"P0: {positions[0]} P1: {positions[1]} P0->P1: {positions[1]-positions[0]}")
    p0dists = numpy.delete(positions, 0, axis=0)
    p0dists -= positions[0]
    print(f"P0-P[1:]: {p0dists}")
          
    grav = Gravity()
#    grav.createRandomBodies(3, test3Masses, test3Poses, test3Velos)
    grav.printState()
 #   grav.sumForces()
    cmd = ""
    while cmd != "exit":
        cmd = input("Command: ")
        cmd.strip()
        if cmd in ("step", "s"):
            grav.jumpOneSecond()
            grav.printState()
