from threading import Condition

class ShutdownHandler:
    def __init__(self):
        self.handlers = []
        
    def register(self, v):
        self.handlers.append(v)

    def shutdown(self):
        for h in self.handlers:
            h.shutdown()

        assert len(self.handlers) == 0
        
    def deregister(self, v):
        self.handlers.remove(v)
            
            
shutdown = ShutdownHandler()
