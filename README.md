<h1 align="center">pi-temp-pbs</h1>
<p align="center">
    <a href="LICENSE"><img alt="The Unlicense" src="https://img.shields.io/badge/license-unlicense-gray?logo=unlicense&color=%23808080" /></a>
    <img alt="Python Version from PEP 621 TOML" src="https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fdoublezerowld%2Fpi-temp-pbs%2Frefs%2Fheads%2Fmain%2Fpyproject.toml&logo=Python&logoColor=white">
    <img alt="Current version: 1.0.0" src="https://img.shields.io/badge/version-1.0.0-orange">

</a>
</p>

Kod stworzony w ramach praktyk zawodowych, na Raspberry Pi 5.

Odczytuje temperaturę z czujnika DS18B20 podłączonego do interfejsu 1-wire, i za pomocą Pythona + Flask wyświetlą ją na frontendzie wraz z godzinnym wykresem z ostatniego dnia.

<p align="center">
    <img src="readme/site.jpg" alt="Dashboard screenshot" width="80%" align="center"/>
</p>
<i><p align="center">Zrzut ekranu dashboard</p></i>

## Funkcjonalność
- Odczyt **DS18B20** (1-Wire interface)  
- **Realtime dashboard** Flask + Chart.js (24h wykres)
- **Background logging** APScheduler + SQLite
- **Production deployment** nginx + gunicorn + systemd

## Wykorzystane technologie i języki:
- **Python** *(Flask, APScheduler)*
- Vanilla **HTML, CSS, JS** *(Chart.JS)*
- **SQAlchemy, SQLite**
- **TOML** *(plik konfiguracji `config.toml`)*
- **Bash** *(skrypt `deploy.sh`)*
- **nginx**
- **gunicorn**
- **systemd**
