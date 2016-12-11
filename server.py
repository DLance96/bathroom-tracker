#!/usr/bin/env python3
from flask import Flask, request, render_template, session
from flask_cas import CAS, login_required, login, logout
import psycopg2
import os

app = Flask(__name__)
app.config['CAS_SERVER'] = 'https://login.case.edu'
app.config['CAS_AFTER_LOGIN'] = 'hello'
cas = CAS(app, '/cas')

conn = psycopg2.connect(os.environ['PGCONN'])


@app.route("/bathroom/<int:id>")
def bathroom(id):
    username = cas.username
    cur = conn.cursor()
    cur.execute("""SELECT bathroom.brid, bathroom.gender, bathroom.floor,
                building.name FROM bathroom INNER JOIN building ON
                bathroom.bid=building.bid WHERE bathroom.brid=%s""", (id,))
    bathroom = cur.fetchone()
    cur.execute("""SELECT review, case_id, rating FROM review WHERE
                brid=%s""", (id,))
    reviews = cur.fetchall()
    conn.commit()
    cur.close()
    session['CAS_AFTER_LOGIN_SESSION_URL'] = request.path
    return render_template(
        "bathroom.html",
        bathroom=bathroom,
        reviews=reviews,
        username=username,
    )


@app.route("/building/add", methods=["POST"])
@login_required
def add_building():
    name = request.form['name']
    cur = conn.cursor()
    cur.execute("""INSERT INTO building (name) VALUES (%s)
               ON CONFLICT (name) DO UPDATE SET opens=EXCLUDED.opens,
               closes=EXCLUDED.closes RETURNING bid""", (name,))
    x = cur.fetchone()
    conn.commit()
    cur.close()
    return "Successfully created bathroom %s with bid %s" % (name, x[0])


@app.route("/building/add", methods=["GET"])
@login_required
def add_building_view():
    return render_template("add_building.html")


@app.route("/building/major", methods=["POST"])
@login_required
def building_major():
    building = int(request.form['building'])
    major = int(request.form['major'])
    cur = conn.cursor()
    cur.execute("""INSERT INTO building_access (bid, mid) VALUES
                (%s, %s) ON CONFLICT (bid, mid) DO UPDATE SET
                bid=EXCLUDED.bid RETURNING (SELECT name FROM building
                WHERE bid=%s), (SELECT name FROM major WHERE mid=%s)""",
                (major, building, building, major,))
    conn.commit()
    x = cur.fetchone()
    cur.close()
    return "Associated building %s with major %s" % (x[0], x[1])


@app.route("/building/major", methods=["GET"])
@login_required
def building_major_view():
    cur = conn.cursor()
    cur.execute("""SELECT bid, name FROM building""")
    buildings = cur.fetchall()
    cur.execute("""SELECT mid, name FROM major""")
    majors = cur.fetchall()
    conn.commit()
    cur.close()
    return render_template(
        "building_major.html",
        buildings=buildings,
        majors=majors,
    )


@app.route("/bathroom/add", methods=["POST"])
@login_required
def add_bathroom():
    building_id = int(request.form['building'])
    floor = int(request.form['floor'])
    gender = request.form['gender']

    cur = conn.cursor()
    cur.execute("""INSERT INTO bathroom (bid, floor, gender) VALUES
                (%s, %s, %s) RETURNING brid, (SELECT name FROM building WHERE
                bid=%s)""", (building_id, floor, gender, building_id,))
    x = cur.fetchone()
    conn.commit()
    cur.close()

    return "Added bathroom to building %s on floor %s with id %s" % (x[1],
                                                                     floor,
                                                                     x[0])


@app.route("/bathroom/add", methods=["GET"])
@login_required
def add_bathroom_view():
    gender = ['male', 'female', 'neither']
    cur = conn.cursor()
    cur.execute("""SELECT bid, name FROM building""")
    buildings = cur.fetchall()
    conn.commit()
    cur.close()
    return render_template(
        "add_bathroom.html",
        buildings=buildings,
        gender=gender,
    )


@app.route("/")
@app.route("/bathrooms")
def list_bathrooms():
    cur = conn.cursor()
    cur.execute("""SELECT bathroom.brid, bathroom.floor, bathroom.gender,
                building.name FROM bathroom INNER JOIN building ON
                bathroom.bid=building.bid""")
    bathrooms = cur.fetchall()
    conn.commit()
    cur.close()
    return render_template(
        "bathrooms.html",
        bathrooms=bathrooms,
    )


@app.route("/you")
@login_required
def you():
    return cas.username


@app.route("/major/add", methods=["POST"])
@login_required
def add_major():
    major = request.form['major']
    cur = conn.cursor()
    cur.execute("""INSERT INTO major (name) VALUES (%s) ON CONFLICT (name)
                DO UPDATE SET name=EXCLUDED.name RETURNING name""", (major,))
    x = cur.fetchone()
    conn.commit()
    cur.close()
    return "Successfully added the major %s" % x[0]


@app.route("/major/add", methods=["GET"])
@login_required
def add_major_view():
    return render_template("add_major.html")


@app.route("/user/add/<string:username>")
@login_required
def add_user(username):
    cur = conn.cursor()
    cur.execute("""INSERT INTO person (case_id) VALUES (%s) ON CONFLICT
                (case_id) DO UPDATE SET case_id=EXCLUDED.case_id
                RETURNING case_id""", (username,))
    x = cur.fetchone()
    conn.commit()
    cur.close()
    return str(x)


@app.route("/user/modify", methods=["POST"])
@login_required
def mod_user():
    username = cas.username
    major = int(request.form['major'])
    cur = conn.cursor()
    cur.execute("""INSERT INTO person (case_id, mid) VALUES (%s, %s)
                ON CONFLICT (case_id) DO UPDATE SET mid=EXCLUDED.mid
                RETURNING case_id""", (username, major,))
    conn.commit()
    cur.close()
    return "Successfully modified"


@app.route("/user/modify", methods=["GET"])
@login_required
def mod_user_view():
    username = cas.username
    cur = conn.cursor()
    cur.execute("""SELECT mid, name FROM major""")
    majors = cur.fetchall()
    conn.commit()
    cur.close()
    return render_template(
        "modify_user.html",
        majors=majors,
        username=username,
    )


@app.route("/review/add/<int:bathroom>", methods=["POST"])
@login_required
def add_review(bathroom):
    username = cas.username
    review = request.form['review']
    rating = int(request.form['rating'])

    cur = conn.cursor()
    cur.execute("""INSERT INTO review (brid, review, case_id, rating) VALUES
                (%s, %s, %s, %s)""", (bathroom, review, username, rating,))
    conn.commit()
    cur.close()
    return "Review added"


app.route("/login")(login)
app.route("/logout")(logout)


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
