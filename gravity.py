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

    def bodyColors(self):
        return self._colors

    def bodyCount(self):
        return self._bodyCount
    
    def bodyPositions(self):
        return self._positions
    
    def bodySizes(self):
        return self._sizes
    
    def createRandomBodies(self):
        self._massForces = None
        
        # Create 3D random body positions (m, m, m)
        self._positions = numpy.random.rand(self._bodyCount, 3)
        self._positions *= (self._posRange[1] - self._posRange[0])
        self._positions += self._posRange[0]

        # Create 3D random body velocity vectors (m/s, m/s, m/s)
        self._velocities = numpy.random.rand(self._bodyCount, 3)
        self._velocities *= (self._velRange[1] - self._velRange[0])
        self._velocities += self._velRange[0]

        # Create random body masses (Kg)
        self._masses = numpy.random.rand(self._bodyCount)
        self._masses *= (self._massRange[1] - self._massRange[0])
        self._masses += self._massRange[0]

        # Create colors and sizes body visuals
        self._massToSizeFactor = 1.0 / 100.0
        self._sizes = self._masses * self._massToSizeFactor
        self._colors = numpy.random.rand(self._bodyCount, 3)

        # Set centroid mass
#        self._positions[0]  *= 0.0
#        self._velocities[0] *= 0.0
        
    def positionRange(self):
        return self._posRange
    
    def printState(self):
        print(f"TIME = {self._time}")
        print(f"POSITIONS:\n", self._positions)
        print(f"VELOCITIES: {self._velocities}")
        print(f"MASSES: {self._masses}")
        print(f"FORCES: {self._massForces}")

    def jumpOneSecond(self):
        """Sum 3D forces on mass bodies, then update each body position and
        velocoties.
        """
        self.sumForces()

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

    def massRange(self):
        return self._massRange

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
        Sum forces for each body
poss = np.array([[1., 1., 1.], [2., 2., 2.], [3., 3., 3.]])
pos0 = np.array([1., 1., 1.])
pos0 - poss
array([[ 0.,  0.,  0.],
       [-1., -1., -1.],
       [-2., -2., -2.]])
poss - pos0
array([[0., 0., 0.],
       [1., 1., 1.],
       [2., 2., 2.]])
np.linalg.norm(poss)
6.48074069840786
np.linalg.norm(poss, axis=1)
array([1.73205081, 3.46410162, 5.19615242])
        """
        self._massForces = numpy.array([])

        for bdx, mass2 in enumerate(self._masses):
            m2Pos = self._positions[bdx]
            m2Vel = self._velocities[bdx]
            #print(f"MASS2 {mass2}  m2Pos={m2Pos}  m2Vel={m2Vel}")

            otherMasses = numpy.delete(self._masses, bdx)
            otherPoses  = numpy.delete(self._positions, bdx, axis=0)
            #print(f"OTHER MASSES = {otherMasses}  OTHER POSES = {otherPoses}")
            m21Vecs = m2Pos - otherPoses
            #print(f"m21Vecs {m21Vecs}")
            m21Dists = numpy.linalg.norm(m21Vecs, axis=1)
            #print(f"m21Dists = {m21Dists}  {m21Dists[:, numpy.newaxis]}")
            m21Norms = m21Vecs / m21Dists[:, numpy.newaxis]
            #print(f"m21Norms = {m21Norms}")
            m2m1s = mass2 * otherMasses
            #print(f"m2m1s = {m2m1s}")
            m2m1r1s = m2m1s / m21Dists
            #print(f"m2m1r1s = {m2m1r1s}")
            m2fxyz = m2m1r1s[:, numpy.newaxis] * m21Norms
            #print(f"m2fxyz = {m2fxyz}")
            m2fsum = numpy.sum(m2fxyz, axis=0)
            #print(f"m2fsum = {m2fsum}")

            # Multiply force sums by gravitational constants to get
            # forces in Newtons
            m2GravVec = m2fsum * -G
            #print(f"m2GravVec = {m2GravVec}")
            self._massForces = numpy.append(self._massForces, m2GravVec)
            # for qdx

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
