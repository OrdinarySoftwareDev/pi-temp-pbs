import platform
import threading
import time
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from flask_apscheduler import APScheduler
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

import config
from config import logger
from sensor import find_device

# inicjalizacja Flask
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{config.DB_FILE.absolute()}"

# harmonogram zadań
scheduler = APScheduler()
scheduler.init_app(app)


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
db.init_app(app)


# klasa dla wierszy w bazie danych
class LogEntry(db.Model):
    id: Mapped[int] = mapped_column(autoincrement=True, unique=True, primary_key=True)
    temperature: Mapped[int] = mapped_column()
    timestamp: Mapped[datetime] = mapped_column(default=datetime.now, index=True)

    def __repr__(self) -> str:
        return f"<LogEntry(id={self.id}, temp={self.temperature} @{self.timestamp})>"


sensor = find_device()

chart_data: dict = {}
latest_measurement: tuple = ()


"""FUNKCJE POMOCNICZE"""


# proste formatowanie temperatury
def format_temperature(milicelsius: int, precision: int, separator: str = ".") -> str:
    celsius = f"{(milicelsius / 1000):.{precision}f}".replace(".", separator)
    return celsius


# uruchomienie fukcji z kontekstem aplikacji
def run_with_context(func):
    with app.app_context():
        func()


# dekorator zapewniający kontekst dla zadań APScheduler
def run_with_context_job(func):
    def wrapper(*args, **kwargs):
        run_with_context(lambda: func(*args, **kwargs))

    return wrapper


run_with_context(lambda: db.create_all())


# aktualizacja tekstu na stronie
@run_with_context_job
def update_temp():
    global latest_measurement

    reading = sensor.read()
    if reading:
        latest_measurement = (
            format_temperature(reading, config.PRECISION),
            str(datetime.now()).split(".")[0],
        )

    else:
        logger.error("Temperature read request to server failed!")


# zapis temperatury do bazy daych
@run_with_context_job
def log_temp():
    global latest_measurement

    reading = sensor.read()
    if reading:
        entry = LogEntry()
        entry.temperature = reading
        entry.timestamp = datetime.now()

        db.session.add(entry)
        db.session.commit()

        # aktualizacja temperatury na stronie
        latest_measurement = (
            format_temperature(reading, config.PRECISION),
            str(entry.timestamp).split(".")[0],
        )

        chart_from_db()
    else:
        logger.error("Temperature read request to server failed!")


# aktualizacja danych służących do generacji wykresu po stronie klienta
@run_with_context_job
def chart_from_db():
    global chart_data

    q = (
        LogEntry.query.order_by(LogEntry.timestamp.desc())
        .limit(config.CHART_MAX_TICKS)
        .all()
    )

    chart_data = {}

    for entry in q:
        chart_data[str(entry.timestamp)] = float(
            format_temperature(entry.temperature, 3, ".")
        )


"""ENDPOINTY"""


# strona główna
@app.route("/")
def root():
    if not latest_measurement:
        update_temp()

    logger.debug(chart_data)

    return render_template(
        "index.html",
        temp2f=latest_measurement[0],
        last_update=latest_measurement[1],
        t_data=chart_data,
    )


# healthcheck
@app.route("/health")
def health():
    return jsonify(
        {
            "status": "healthy",
            "latest_measurement": jsonify(latest_measurement)
            if latest_measurement
            else None,
            "jobs": len(scheduler.get_jobs()),
        }
    )


# zwraca `n` najnowszych wpisów w bazie danych, posortowanych czasem wpisu rosnąco
@app.route("/logs")
def api_logs():
    n = request.args.get("n")
    if n:
        n = max(1, min(int(n), 250))
    else:
        n = 50
    q = LogEntry.query.order_by(LogEntry.timestamp.desc()).limit(n).all()[::-1]
    return jsonify(
        [
            {"temperature": line.temperature, "time": line.timestamp.isoformat()}
            for line in q
        ]
    )


# Zwraca aktualną temperaturę z czujnika w formacie JSON
# Zwraca temperaturę w milicelsjuszach
@app.route("/temperature")
def api_temp():
    reading = sensor.read()
    logger.info(f"Endpoint `/temperature` hit. Aktualna temperatura: {reading}")
    return jsonify({"temperature": reading, "timestamp": datetime.now().isoformat()})


"""INIT"""


def init_app():
    logger.info("Application init")

    os_name = platform.system()
    if os_name.lower() != "linux":
        raise RuntimeError(
            f"Program może być uruchamiany tylko na systemach Linux! Wykryto: {os_name}"
        )

    if config.LOG_ON_START:
        run_with_context(log_temp)

    run_with_context(chart_from_db)

    scheduler.add_job(
        id="log_temp",
        func=log_temp,
        trigger="interval",
        seconds=config.LOGGING_INTERVAL,
    )
    scheduler.add_job(
        id="update_temp",
        func=update_temp,
        trigger="interval",
        seconds=config.UPDATE_INTERVAL,
    )

    scheduler.start()


init_app()
