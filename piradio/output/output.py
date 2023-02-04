
class PiOutput:
    def __init__(self):
        pass

    def info(self, s):
        print(s)
    
    def print(self, s):
        print(s)

    def debug(self, s):
        if False:
            print(s)

output = PiOutput()
