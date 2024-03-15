import requests


class ERASynth:
    variables = [
        'rfoutput',
        'frequency',
        'amplitude'
    ]
    
    def __init__(self, addr="10.77.11.1"):
        self.addr = addr

    def _update_var(self, var, val):
        URL = f"http://{self.addr}"

        requests.post(URL, data={ var: str(int(val)) })

    def enable_output(self, doit=True):
        self._update_var('rfoutput', 1 if doit else 0)

    def set_frequency(self, f):
        self._update_var('frequency', str(int(f.Hz)))
        
    def set_amplitude(self, dB):
        self._update_var('amplitude', str(int(dB)))
        
