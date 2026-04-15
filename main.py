from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from sensor import find_device

DB_FILE = Path(__file__).parent / "db/logs.db"
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_FILE.absolute()}"


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
db.init_app(app)

tz = timezone.utc


class LogEntry(db.Model):
    id: Mapped[int] = mapped_column(autoincrement=True, unique=True, primary_key=True)
    temperature: Mapped[int] = mapped_column()
    timestamp: Mapped[datetime] = mapped_column(default=datetime.now(tz=tz), index=True)

    def __repr__(self) -> str:
        return f"<LogEntry(id={self.id}, temp={self.temperature} @{self.timestamp})>"


sensor = find_device()

with app.app_context():
    db.create_all()


# Strona główna
@app.route("/")
def root():
    return render_template("index.html")


# Zwraca `n` najnowszych wpisów w bazie danych, posortowanych czasem wpisu rosnąco
@app.route("/api/logs")
def logs():
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


# Zwraca aktualną temperaturę z czujnika
@app.route("/api/temperature")
def api_temp():
    reading = sensor.read()

    entry = LogEntry()
    entry.temperature = reading

    db.session.add(entry)
    db.session.commit()

    return jsonify({"temperature": reading})


if __name__ == "__main__":
    app.run("0.0.0.0", 8080, debug=True)
