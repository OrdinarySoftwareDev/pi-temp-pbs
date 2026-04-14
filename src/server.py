from enum import Enum

from flask import Flask, request

app = Flask(__name__)


@app.route("/")
def root():
    return "Hello, world!"


@app.route("/temperature")
def temperature():
    return ""
