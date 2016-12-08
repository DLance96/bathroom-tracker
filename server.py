#!/usr/bin/env python3
from flask import Flask
import psycopg2

app = Flask(__name__)

conn = psycopg2.connect(
    "dbname=bathroom_tracker user=bathroom password=bath host=localhost"
)


@app.route("/")
def hello():
    return "Hello world"

if __name__ == "__main__":
    app.run()
