import json
import os
import pwd
import sys

BODY_COUNT = "BodyCount"
GRAV_CONST = "G"
MASS_RANGE = "MassRange"
POS_RANGE  = "PosRange"
VEL_RANGE  = "VelRange"
FRAME_RATE = "FrameRate"
SPIN_MODE  = "SpinMode"
TRAIL_LEN  = "TrailLen"
COLL_DIST  = "CollDist"

class OptionsStore(object):

    DEFAULTS = { BODY_COUNT: 3,
                 GRAV_CONST: 0.00133440,
                 MASS_RANGE: (4500.0, 5000.0),
                 POS_RANGE:  (-200.0, 200.0),
                 VEL_RANGE:  (-0.2, 0.2),
                 FRAME_RATE: ("1/4", 0.25),
                 SPIN_MODE:  "X",
                 TRAIL_LEN:  1000,
                 COLL_DIST:  5
                }

    def __init__(self):
        super().__init__()

        self._currentOpts = { }

    def findDefaultPath(self):
        fname = ".gutsrc"
        if sys.platform in ("win32", "win64"):
            home = os.getenv("HOME")
        else:
            pwEnt = pwd.getpwuid(os.getuid())
            if pwEnt:
                home = pwEnt.pw_dir
            else:
                home = os.getenv("HOME")
        if home:
            optPath = os.path.join(home, fname)
        else:
            optPath = fname
        return optPath

    def getOption(self, frameMode, optKey):
        modeOpts = self._currentOpts.get(frameMode)
        if modeOpts is None:
            modeOpts = self._currentOpts[frameMode] = {}
            modeOpts.update(self.DEFAULTS)
        return modeOpts.get(optKey)

    def readOptions(self, optPath):
        try:
            with open(optPath, "r") as optFP:
                optStr = optFP.read()
                return json.loads(optStr)
        except FileNotFoundError as fnfx:
            raise fnfx
        except PermissionError as prmx:
            raise prmx
        except:
            raise sys.exc_info()[1]
        return None
            
    def options(self, frameMode=None):
        if frameMode is None:
            return self._currentOpts
        else:
            modeOpts = self._currentOpts.get(frameMode, OptionsStore.DEFAULTS)
            return modeOpts
            
    def setOption(self, frameMode, optKey, optValue):
        modeOpts = self._currentOpts.get(frameMode)
        if modeOpts is None:
            modeOpts = self._currentOpts[frameMode] = {}
        modeOpts[optKey] = optValue

    def setCurrentOptions(self, opts):
        self._currentOpts.update(opts)

    def updateOptions(self, frameMode, options):
        self._currentOpts[frameMode] = options

    def writeOptions(self, optPath, optDict=None):
        if optDict is None:
            optDict = self._currentOpts
        with open(optPath, "w") as optFP:
            optStr = json.dumps(optDict, sort_keys=True, indent=4)
            optFP.write(optStr)


if __name__ == "__main__":
    
    optStore = OptionsStore()

    optDict = {
        "default": {
            "bodies": 3,
            "massRange": (4500.0, 5000.0)
        }
    }

    optPath = optStore.findDefaultPath()
    optStore.writeOptions(optPath, optDict)

    optsRead = optStore.readOptions(optPath)
    print(repr(optsRead))

    optStore = OptionsStore()
    fmo = optStore.options("Move")
    print(f"Move Opts: {fmo}")
    fmo = optStore.options("Radii")
    print(f"Radii Opts: {fmo}")
    optStore.setOption("Move", optStore.BODY_COUNT, 4)
    optStore.setOption("Radii", optStore.BODY_COUNT, 5)
    opts = optStore.options()
    print(f"OPTS after body count changes: {opts}")
