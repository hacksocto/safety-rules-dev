import sqlite3
from os.path import dirname as dn, abspath as ap

db_path = dn(dn(ap(__file__))) + '/data/db'
db = sqlite3.connect(db_path)
cursor = db.cursor()

request = """CREATE TABLE customers (
    chat_id integer,
    is_admin integer,
    is_debug integer,
    state integer,
    test_points integer,
    test_state integer
)"""

cursor.execute(request)
db.commit()

request = """SELECT *
             FROM customers"""

print(cursor.execute(request).fetchall())
