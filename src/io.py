import subprocess
from pathlib import Path


class DS18B20:
    def __init__(self, device_path: Path):
        self.device_path = device_path
        for c in ["gpio", "therm"]:
            subprocess.run(f"modprobe w1-{c}")

    def read(self): ...
