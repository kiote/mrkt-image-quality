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
DATABASE = 'database.db'
SCHEMA = 'schema.sqlt'

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
  ids = request.args.get('ids', '')
  ids_list = get_valid_ids(ids)
  
  conn = sqlite3.connect(DATABASE)
  c = conn.cursor()
  if ids <> '':
    rows = c.execute("SELECT avg(offer_grade) FROM offers_grade where offer_id in ('%s')" % ids_list)
  else:
    rows = c.execute("SELECT * FROM offers_grade")
  return render_template('show.html', rows=rows)

def save_request(form):
  conn = sqlite3.connect(DATABASE)
  c = conn.cursor()
  check_id = form["checkId"]
  for i in form:
    match = re.findall(r'offer_id\[(\d+)\]', i)
    if not match: continue
    offer_id = match[0]
    grade = form["offer_id[%s]" % offer_id]
    c.execute("INSERT into offers_grade values (?,?,?,?,?)", \
      (offer_id, grade, check_id, request.headers.get('User-Agent'), int(time.time())))
  conn.commit()
  conn.close()

def get_valid_ids(ids):
  ids = ids.split(",")
  
  clear_list = []
  for id in ids:
    if id.isdigit(): clear_list.append(id)
  
  return "','".join(clear_list)

if __name__ == '__main__':
    app.run()