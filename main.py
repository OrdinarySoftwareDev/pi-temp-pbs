import platform
import threading
import time
from datetime import datetime
from pathlib import Path

import schedule
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from sensor import find_device

DB_FILE = Path(__file__).parent / "db/logs.db"

# Tworzymy bazę danych, jeśli nie istnieje
if not DB_FILE.exists():
    print(
        f"Ostrzeżenie: Nie wykryto pliku pod ścieżką {DB_FILE}. Zostanie on stworzony automatycznie wraz z katalogiem."
    )
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    DB_FILE.touch()

# Inicjalizacja aplikacji Flask
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_FILE.absolute()}"


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Wpis do logów
class LogEntry(db.Model):
    id: Mapped[int] = mapped_column(autoincrement=True, unique=True, primary_key=True)
    temperature: Mapped[int] = mapped_column()
    timestamp: Mapped[datetime] = mapped_column(default=datetime.now(), index=True)

    def __repr__(self) -> str:
        return f"<LogEntry(id={self.id}, temp={self.temperature} @{self.timestamp})>"


sensor = find_device()

with app.app_context():
    db.create_all()

chart_data: dict = {}


# Strona główna
@app.route("/")
def root():
    return render_template(
        "index.html",
        temp2f=str(list(chart_data.values())[0]),
        last_update=str(list(chart_data.keys())[0]).split(".")[0],
        t_data=chart_data,
    )


# Zwraca `n` najnowszych wpisów w bazie danych, posortowanych czasem wpisu rosnąco
@app.route("/api/logs")
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
@app.route("/api/temperature")
def api_temp():
    with app.app_context():
        print("Info: Odczytuję temperaturę z czujnika...")
        reading = sensor.read()

        entry = LogEntry()
        entry.temperature = reading
        entry.timestamp = datetime.now()

        db.session.add(entry)
        db.session.commit()

        return jsonify(
            {"temperature": entry.temperature, "timestamp": entry.timestamp.isoformat()}
        )


def update_temp():
    with app.app_context():
        global chart_data

        api_temp()

        # aktualizacja wykresu
        q = LogEntry.query.order_by(LogEntry.timestamp.desc()).limit(18).all()

        chart_data = {}

        for entry in q:
            chart_data[str(entry.timestamp)] = float(
                f"{entry.temperature / 1000:.1f}"
            )  # zaokrąglenie do jednego miejsca po przecinku
        # print(chart_data)


def loop():
    schedule.every(60).minutes.do(update_temp)
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    schedule.clear()

    os_name = platform.system()
    if os_name.lower() != "linux":
        raise RuntimeError(
            f"Program może być uruchamiany tylko na systemach Linux! Wykryto: {os_name}"
        )
    update_temp()
    updater_thread = threading.Thread(target=loop, daemon=True)
    updater_thread.start()

    app.run("0.0.0.0", 8080, debug=False)
