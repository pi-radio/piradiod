
class EderChild:
    def __init__(self, eder):
        self.eder = eder
        
    @property
    def regs(self):
        return self.eder.regs

    def __setattr__(self, name, value):
        if hasattr(self, "eder") and name in self.regs.registers:
            raise RuntimeError("Attempt to assign to variable with reg name on object")

        return super().__setattr__(name, value)
