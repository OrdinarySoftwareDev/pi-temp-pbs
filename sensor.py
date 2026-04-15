import glob
import subprocess
from pathlib import Path

DEVICES_DIR = "/sys/bus/w1/devices/"


# Czujnik powinien być podłączony do pinu GPIO4 (GPCLK0).
# Urządzenie działa na interfejsie 1-wire.
def find_device():
    for c in ["gpio", "therm"]:
        subprocess.run(f"w1-{c}", -1, "modprobe")

    device_folder = glob.glob(DEVICES_DIR + "28*")
    _len = len(device_folder)

    dev = None

    if _len > 1:
        print(
            f"\t{i + 1}: {name.split('/')[-1]}\n"
            for i, name in enumerate(device_folder)
        )
        choice = int(
            input(
                "Ostrzeżenie: Znaleziono wiele urządzeń zaczynających się od `28`. Wybierz jedno z nich wpisując numer."
            )
        )
        dev = device_folder[choice - 1]
    elif _len == 1:
        dev = device_folder[0]
    else:
        raise FileNotFoundError("Nie znaleziono czujnika!")

    device_file = dev + "/w1_slave"
    print(f"Znaleziono czujnik: `{device_file}`!")

    return DS18B20(device_path=Path(device_file))


# Klasa czujnika
class DS18B20:
    def __init__(self, device_path: Path):
        self.device_path = device_path

    def read(self) -> int:
        with open(self.device_path, "r") as data:
            return int(data.readlines()[-1].split("=")[-1])
