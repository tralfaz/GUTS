import json

class OptionsStore(object):

    def __init__(self):
        super().__init__()

        self._currentOpts = { }

    def findDefaultPath(self):
        return "guts.opts"

    def readOptions(self, optPath):
        with open(optPath, "r") as optFP:
            optStr = optFP.read()
            return json.loads(optStr)

    def options(self, frameMode=None):
        if frameMode is None:
            return self._currentOpts
        else:
            return self._currentOpts.get(frameMode, {})
            
    def updateOptions(self, frameMode, options):
        self._currentOpts[frameMode] = options
        print(f"CUR OPTS: {self._currentOpts}")

    def writeOptions(self, optPath, optDict):
        with open(optPath, "w") as optFP:
            optStr = json.dumps(optDict)
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

