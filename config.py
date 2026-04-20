import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

import tomlkit
import tomllib

ALLOW_INCOMPLETE_CONFIG = False

DEFAULTS = {
    "behavior": {
        "debug": False,
        "log_on_start": False,
        "chart_max_ticks": 24,
        "precision": 2,
    },
    "scheduler": {
        "logging_interval": 3600,
        "update_interval": 300,
        "sleep_time": 10,
    },
    "filesystem": {"db_file": "db/temperature_log.db"},
    "web": {"ip": "0.0.0.0", "port": "8080"},
}


def checked_grab(path: str, default_value=None) -> Any:
    config = CONFIG
    layers = path.lower().split(".")

    for layer in layers:
        if isinstance(config, dict):
            config = config.get(layer)
        else:
            raise AttributeError("`config.toml` nie przypomina pliku konfiguracji!")

        if config is None:
            if ALLOW_INCOMPLETE_CONFIG:
                fallback = DEFAULTS
                for f_layer in layers:
                    if default_value:
                        default_value = default_value.get(f_layer)
                    else:
                        raise AttributeError(
                            f"Klucz `{path.lower()}` nie istnieje w konfiguracji domyślnej!"
                        )
                print(
                    f"Ostrzeżenie: Brak `{path}`, użyta zostanie wartość `{default_value}`!"
                )
                return fallback or default_value

            raise AttributeError(f"Plik konfiguracyjny nie zawiera `{path}`!")

    if path.lower() != "behavior.debug":
        if checked_grab("behavior.debug", False):
            print(f"{path}: {config}")

    return config


try:
    with open("config.toml", "rb") as cfile:
        CONFIG: dict = tomllib.load(cfile)

        DEBUG_MODE: bool = checked_grab("behavior.debug")
        LOG_ON_START: bool = checked_grab("behavior.log_on_start")
        CHART_MAX_TICKS: int = checked_grab("behavior.chart_max_ticks")
        PRECISION: int = checked_grab("behavior.precision")

        LOGGING_INTERVAL: int = checked_grab("scheduler.logging_interval")
        UPDATE_INTERVAL: int = checked_grab("scheduler.update_interval")
        SCHEDULER_SLEEP_TIME: int = checked_grab("scheduler.sleep_time")

        DB_PATH: Path = Path(checked_grab("filesystem.db_file"))
        HOST_IP: str = checked_grab("web.ip")
        PORT: int = int(checked_grab("web.port"))

        DB_FILE = Path(__file__).parent / DB_PATH

        log_file = Path(__file__).parent / "latest.log"
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5
        )
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )

        logging.basicConfig(handlers=[file_handler], level=logging.INFO)

        if DEBUG_MODE:
            console = logging.StreamHandler()
            console.setLevel(logging.DEBUG)
            logging.getLogger().addHandler(console)
            logging.warning(
                "W trybie debug temperatury NIE są zapisywany do bazy danych!"
            )

        # tworzymy bazę danych, jeśli nie istnieje
        if not DB_FILE.exists():
            logging.warning(
                f"Nie wykryto pliku pod ścieżką {DB_FILE}. Zostanie on stworzony automatycznie wraz z katalogiem."
            )
            DB_FILE.parent.mkdir(parents=True, exist_ok=True)
            DB_FILE.touch()

        clamped_precision = min(3, max(0, PRECISION))
        if clamped_precision != PRECISION:
            logging.warning("Wartość `behavior.precision` powinna wynosić od 0 do 3.")

        PRECISION = clamped_precision
except FileNotFoundError:
    if ALLOW_INCOMPLETE_CONFIG:
        logging.warning(
            "Nie znaleziono config.toml - zapisano do niego konfigurację domyślną!"
        )
        CONFIG = DEFAULTS

        with open("config.toml", "w") as cfg:
            cfg.write(tomlkit.dumps(DEFAULTS))
    else:
        raise
except Exception as e:
    raise e

logger = logging.getLogger(__name__)
