from flask import Flask
from flask import request
from flask import render_template
from flask import g
import sqlite3
import re


app = Flask(__name__)
app.config['DEBUG'] = True

# << database
DATABASE = 'database.db'
SCHEMA = 'schema.sql'

def get_db():
  db = sqlite3.connect(DATABASE)
  return db

@app.teardown_appcontext
def close_connection(exception):
  db = getattr(g, '_database', None)
  if db is not None:
      db.close()

def init_database():
  with app.app_context():
    db = get_db()
    with app.open_resource(SCHEMA, mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
# >> database 

@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
  return render_template('hello.html', name=name)

@app.route('/save', methods=['POST'])
def save():
  if request.method == 'POST':
    save_request(request.form)
    return "SAVED"

@app.route('/init_db')
def init_db():
  init_database()
  return "created"

def save_request(form):
  conn = sqlite3.connect(DATABASE)
  c = conn.cursor()
  for i in form:
    offer_id = re.findall(r'\d+', i)[0]
    grade = form["input[%s]" % offer_id]
    c.execute("INSERT into offers_grade values (?,?)", (offer_id, grade))