from typing import Any

import tomllib

ALLOW_INCOMPLETE_CONFIG = False

DEFAULTS = {
    "behavior": {
        "debug": False,
        "update_on_start": False,
        "logging_interval": 3600,
        "update_interval": 300,
        "chart_max_ticks": 24,
        "precision": 2,
    },
    "database": {"path": "db/logs.db"},
    "web": {"ip": "0.0.0.0", "port": "8080"},
}


def checked_grab(path: str, default_value=None) -> Any:
    config = CONFIG
    layers = path.lower().split(".")

    for layer in layers:
        if isinstance(config, dict):
            config = config.get(layer)
        else:
            raise AttributeError("BŁĄD: config.toml nie przypomina pliku konfiguracji")

        if config is None:
            if ALLOW_INCOMPLETE_CONFIG:
                if not default_value:
                    default = DEFAULTS
                    for d_layer in layers:
                        default_value = default.get(d_layer)

                print(
                    f"Ostrzeżenie: Brak {path}, użyta zostanie wartość `{default_value}`!"
                )
                return default_value
            raise AttributeError(f"Missing config path: {path}")

    return config


try:
    with open("config.toml", "rb") as cfile:
        CONFIG = tomllib.load(cfile)

        DEBUG_MODE = CONFIG["behavior"]["debug"]
        UPDATE_ON_START = CONFIG["behavior"]["update_on_start"]
        LOGGING_INTERVAL = CONFIG["behavior"]["logging_interval"]
        UPDATE_INTERVAL = CONFIG["behavior"]["update_interval"]
        CHART_MAX_TICKS = CONFIG["behavior"]["chart_max_ticks"]
        PRECISION = CONFIG["behavior"]["precision"]

        # Baza danych
        DB_PATH = CONFIG["database"]["path"]

        # Sieć
        HOST_IP = CONFIG["web"]["ip"]
        PORT = CONFIG["web"]["port"]

except FileNotFoundError:
    if ALLOW_INCOMPLETE_CONFIG:
        print(
            "Ostrzeżenie: Nie znaleziono config.toml - użyta zostana konfiguracja domyślna!"
        )
        CONFIG = DEFAULTS
    else:
        raise
