import time
from threading import Event, Thread, Timer
from piradio.command import shutdown
from piradio.output import output

class Monitor:
    def __init__(self):
        self.eders = []
        self.timer = None
        shutdown.register(self)

    def shutdown(self):
        if self.timer is not None:
            self.timer.cancel()
        shutdown.deregister(self)

    def register(self, eder):
        self.eders.append(eder)

        if len(self.eders) == 1:
            self.timer = Timer(5, self.run)
            self.timer.start()

    def run(self):
        output.info("Monitor running")
        self.timer = Timer(5, self.run)
        self.timer.start()
        

monitor = Monitor()
        
def register_eder(eder):
    monitor.register(eder)
