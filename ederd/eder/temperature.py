

class EderTemperature:
    def __init__(self, eder):
        self.eder = eder


    def start(self, threshold=5):
        self.eder.bist_ot_ctrl = 0x00
        self.eder.bist_ot_temp = 0x40 + threshold
        # 
        self.eder.bist_ot_rx_off_mask = self.eder.trx_tx_off
