import yaml

from pathlib import Path

config_base_path = Path("/etc/piradio/SIVERS/Eder")

class EderConfig:
    def __init__(self, eder):
        self._config = dict()
        self.path = config_base_path / str(eder.N) / "config"

        if self.path.exists():
            with open(self.path, "r") as f:
                self._config = yaml.load(f, Loader=yaml.SafeLoader)
        
    def save(self):
        if not self.path.exists():
            self.path.parent.mkdir(mode=0o775, parents=True, exist_ok=True)

        with open(self.path, "w") as f:
            yaml.dump(self._config, f)

    def __getitem__(self, k):
        return self._config[k]

    def __setitem__(self, k, v):
        self._config[k] = v
        self.save()

    def __contains__(self, k):
        return k in self._config
