#!/usr/bin/env python3
from flask import Flask, request, render_template
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
    cur = conn.cursor()
    cur.execute("SELECT * FROM bathroom WHERE id=%s", (id,))
    x = cur.fetchone() or 'none'
    conn.commit()
    cur.close()
    # TODO: return real info here
    return x


@app.route("/building/add", methods=["POST"])
@login_required
def add_building():
    name = request.form['name']
    cur = conn.cursor()
    cur.execute("""INSERT INTO building (name) VALUES (%s)
               ON CONFLICT (name) DO UPDATE SET opens=EXCLUDED.opens,
               closes=EXCLUDED.closes RETURNING id""", (name,))
    x = cur.fetchone()
    conn.commit()
    cur.close()
    return "Successfully created building %s with id %s" % (name, x[0])


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
    cur.execute("""INSERT INTO building_access (building, major) VALUES
                (%s, %s) ON CONFLICT (building, major) DO UPDATE SET
                building=EXCLUDED.building RETURNING (SELECT name FROM building
                WHERE id=%s), (SELECT name FROM major WHERE id=%s)""",
                (major, building, building, major,))
    conn.commit()
    x = cur.fetchone()
    cur.close()
    return "Associated building %s with major %s" % (x[0], x[1])


@app.route("/building/major", methods=["GET"])
@login_required
def building_major_view():
    cur = conn.cursor()
    cur.execute("""SELECT ids, name FROM building""")
    buildings = cur.fetchall()
    cur.execute("""SELECT id, name FROM major""")
    majors = cur.fetchall()
    conn.commit()
    cur.close()
    # TODO: a form that allows users to select one of each of these
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
    cur.execute("""INSERT INTO bathroom (building, floor, gender) VALUES
                (%s, %s, %s) RETURNING id, (SELECT name FROM building WHERE
                id=%s)""", (building_id, floor, gender, building_id,))
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
    cur.execute("""SELECT id, name FROM building""")
    buildings = cur.fetchall()
    conn.commit()
    cur.close()
    return render_template(
        "add_bathroom.html",
        buildings=buildings,
        gender=gender,
    )


@app.route("/bathrooms")
def list_bathrooms():
    query = request.args.get('query')
    building = request.args.get('building')
    bathroom = request.args.get('bathroom')

    cur = conn.cursor()

    if query == 'query-1':
        cur.execute("""
            SELECT bathroom.id, bathroom.floor, bathroom.gender,
            building.name FROM bathroom JOIN building ON
            bathroom.building=building.id;
            """)
    elif query == 'query-2':
        cur.execute("""
            SELECT bathroom.id, bathroom.floor, bathroom.gender 
            FROM bathroom NATURAL JOIN building
            """)
    elif query == 'query-3':
        pass
    elif query == 'query-4':
        pass
    elif query == 'query-5':
        pass
    elif query == 'query-6':
        pass
    elif query == 'query-7':
        pass

    ret = cur.fetchall()

    cur.execute("""
        SELECT id, name FROM building;
        """)
    building_names = cur.fetchall()

    conn.commit()
    cur.close()

    return render_template(
        "list_bathrooms.html",
        bathrooms=ret,
        buildings=building_names,
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
                DO UPDATE SET name=EXCLUDED.name RETURNING id""", (major,))
    x = cur.fetchone()
    conn.commit()
    cur.close()
    return str(x)


@app.route("/major/add", methods=["GET"])
@login_required
def add_major_view():
    # TODO: form to add a major
    return "FORM TO ADD A MAJOR"


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


@app.route("/user/modify/<string:username>", methods=["POST"])
@login_required
def mod_user(username):
    if cas.username != username:
        return "You can only edit you"
    username = cas.username
    major = int(request.post['major'])
    cur = conn.cursor()
    cur.execute("""INSERT INTO person (case_id, major) VALUES (%s, %s)
                ON CONFLICT (case_id) DO UPDATE SET major=EXCLUDED.major
                RETURNING case_id""", (username, major,))
    x = cur.fetchone()
    conn.commit()
    cur.close()
    return str(x)


@app.route("/user/modify/<string:username>", methods=["GET"])
@login_required
def mod_user_view(username):
    cur = conn.cursor()
    cur.execute("""SELECT id, name FROM major""")
    majors = cur.fetchall()
    conn.commit()
    cur.close()
    # TODO: make a form here too
    return str(majors)


@app.route("/review/add/<int:bathroom>", methods=["POST"])
@login_required
def add_reivew(bathroom):
    username = cas.username
    bathroom = int(request.form['bathroom'])
    review = request.form['review']
    rating = int(request.form['rating'])

    cur = conn.cursor()
    cur.execute("""INSERT INTO review (bathroom, review, person, rating) VALUES
                (%s, %s, %s, %s)""", (bathroom, review, username, rating,))
    conn.commit()
    cur.close()
    return "DONE"


@app.route("/review/add/<int:bathroom>", methods=["GET"])
@login_required
def add_reivew_view(bathroom):
    cur = conn.cursor()
    cur.execute("""SELECT id, name FROM bathroom""")
    bathrooms = cur.fetchall()
    conn.commit()
    cur.close()
    # TODO: form here
    return str(bathrooms)


@app.route("/review/<int:bathroom>")
def get_review(bathroom):
    cur = conn.cursor()
    cur.execute("""SELECT bathroom, review, rating FROM review WHERE
                bathroom=(%s)""", (bathroom,))
    x = cur.fetchall()
    conn.commit()
    cur.close()
    return str(x)


@app.route("/")
def hello():
    return "Hello world"


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
