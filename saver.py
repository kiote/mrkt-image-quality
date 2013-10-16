from flask import Flask
from flask import request
from flask import render_template
from flask import g
import sqlite3
import re
import time


app = Flask(__name__)
app.config['DEBUG'] = True

# << database
DATABASE = './database.db'
SCHEMA = './schema.sql'

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

@app.route('/save', methods=['POST'])
def save():
  if request.method == 'POST':
    save_request(request.form)
    return "SAVED"

@app.route('/init_db')
def init_db():
  init_database()
  return "created"

@app.route('/show')
def show():
  return render_template('show.html')

def save_request(form):
  conn = sqlite3.connect(DATABASE)
  c = conn.cursor()
  for i in form:
    match = re.findall(r'offer_id\[(\d+)\]', i)
    if not match: continue
    offer_id = match[0]
    grade = form["offer_id[%s]" % offer_id]
    c.execute("INSERT into offers_grade values (?,?,?)", (offer_id, grade, int(time.time())))

if __name__ == '__main__':
    app.run()