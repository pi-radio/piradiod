
class EEPROM:
    eeprom_addr = 0x53
    temp_sens_addr = 0x1b
    
    def __init__(self, i2c):
        self.i2c = i2c

    def startup(self):
        # Load product data
        # Get calibration offsets
        #eder.py:85
        pass
