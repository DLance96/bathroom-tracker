#!/usr/bin/env python3
from flask import Flask
from flask_cas import CAS, login_required
import psycopg2
import os

app = Flask(__name__)
app.config['CAS_SERVER'] = 'https://login.case.edu'
app.config['CAS_AFTER_LOGIN'] = 'index'
cas = CAS(app, '/cas')

conn = psycopg2.connect(os.environ['PGCONN'])


@app.route("/bathroom/<int:id>")
def bathroom(id):
    return "THIS IS A BATHROOM WITH ID %s" % id

@app.route("/bathrooms")
def list_bathrooms():
    return "LIST OF BATHROOMS YAY"

@app.route("/")
def hello():
    return "Hello world"

if __name__ == "__main__":
    try:
        port = os.environ['PORT']
    except:
        port = 5000
    app.run(host='0.0.0.0', port=port)
