import sqlite3

from flask import Flask, render_template, request, jsonify

from flask_cors import CORS


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def init_sqlite_db():
    conn = sqlite3.connect('database.db')
    print("Opened database successfully")
    conn.execute('CREATE TABLE IF NOT EXISTS blogs (id INTEGER PRIMARY KEY AUTOINCREMENT ,header TEXT, title TEXT, '
                 'description TEXT, body TEXT)')
    print("Table created successfully")

    conn.close()


init_sqlite_db()

app = Flask(__name__)
CORS(app)


@app.route('/')
@app.route('/blog-form/')
def enter_data():
    return render_template('blog-form.html')


@app.route('/add-data/', methods=['POST'])
def add_new_record():
    if request.method == "POST":
        try:
            header = request.form['header']
            title = request.form['title']
            description = request.form['description']
            body = request.form['body']
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute("INSERT INTO blogs (header, title, description, body) VALUES (?, ?, ?, ?)",
                            (header, title, description, body))
                con.commit()
                msg = "Record successfully added."
        except Exception as e:
            con.rollback()
            msg = "Error occurred in insert operation: " + e
        finally:
            con.close()
            return render_template('result.html', msg=msg)


@app.route('/show-data/', methods=['GET'])
def show_data():
    data = []
    try:
        with sqlite3.connect('database.db') as con:
            con.row_factory = dict_factory
            cur = con.cursor()
            cur.execute("SELECT * FROM blogs")
            data = cur.fetchall()
    except Exception as e:
        con.rollback()
        print("There was an error fetching results from the database.")
    finally:
        con.close()
    return jsonify(data)


@app.route('/show-data/<int:data_id>/', methods=['GET'])
def show_data(data_id):
    data = []
    try:
        with sqlite3.connect('database.db') as con:
            con.row_factory = dict_factory
            cur = con.cursor()
            cur.execute("SELECT * FROM blogs WHERE id=" + str(data_id))
            data = cur.fetchall()
    except Exception as e:
        con.rollback()
        print("There was an error fetching results from the database.")
    finally:
        con.close()
    return jsonify(data)


@app.route('/delete-data/<int:data_id>/', methods=["GET"])
def delete_data(data_id):
    msg = None
    try:
        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute("DELETE FROM blogs WHERE id=" + str(data_id))
            con.commit()
            msg = "A record was deleted successfully from the database."
    except Exception as e:
        con.rollback()
        msg = "Error occurred when deleting a student in the database: " + str(e)
    finally:
        con.close()
    return render_template('delete-success.html', msg=msg)


if __name__ == '__main__':
    app.run(debug=True)
