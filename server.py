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
    cur = conn.cursor()
    cur.execute("SELECT * FROM bathroom WHERE id=%s", (id,))
    x = cur.fetchone() or 'none'
    cur.close()
    return x


@app.route("/bathroom/add", methods=["POST"])
@login_required
def add_bathroom():
    return ""


@app.route("/bathroom/add", methods=["GET"])
@login_required
def add_bathroom_view():
    return "form goes here"


@app.route("/bathrooms")
def list_bathrooms():
    cur = conn.cursor()
    cur.execute("SELECT * FROM bathroom")
    cur.close()
    return str(cur.fetchall())


@app.route("/you")
@login_required
def you():
    return cas.username


@app.route("/")
def hello():
    return "Hello world"


if not os.path.exists('secret'):
    print('NOTE: New secret key. All sessions lost.')
    with open('secret', 'wb') as f:
        f.write(os.urandom(24))
with open('secret', 'rb') as f:
    app.secret_key = f.read(24)


if __name__ == "__main__":
    try:
        port = os.environ['PORT']
    except:
        port = 5000
    app.run(host='0.0.0.0', port=port)
