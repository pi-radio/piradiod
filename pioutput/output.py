
class PiOutput:
    def __init__(self):
        pass

    def print(self, s):
        print(s)

    def debug(self, s):
        if False:
            print(s)

pioutput = PiOutput()
