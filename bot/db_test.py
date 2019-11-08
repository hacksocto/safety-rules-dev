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

request = """INSERT INTO customers
VALUES (226549738, 1, 0, 0, 1, 2)"""

cursor.execute(request)
db.commit()

request = """INSERT INTO customers
VALUES (226549888, 1, 0, 0, 1, 2)"""

cursor.execute(request)
db.commit()


chat_id = 226549739
# request = """SELECT is_admin
#             FROM customers
#             WHERE chat_id = """ + str(chat_id)

# cursor.execute(request)
# print(cursor.fetchone())
# print(cursor.fetchone()[0])


def db_select(request):
    db_path = dn(dn(ap(__file__))) + '/data/db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    return cursor.execute(request).fetchall()


request = """SELECT is_admin, is_debug, state, test_points, test_state
                 FROM customers
                 WHERE chat_id = """ + str(chat_id)

response = db_select(request)[0]
print(response)
print(type(response[0]))
print(type(response[1]))
print(type(response[2]))
print(type(response[3]))
print(type(response[4]))

request = """SELECT chat_id
             FROM customers"""

response = db_select(request)
print(type(response[0][0]))

customer = {'chat_id': chat_id, 'is_admin': 0, 'is_debug': 0,
            'state': 0, 'test_points': 0, 'test_state': 0}

request = """UPDATE customers
                 SET is_admin={}, is_debug={}, state={},
                 test_points={}, test_state={}
                 WHERE chat_id={}""".format(customer.get('is_admin'),
                                            customer.get('is_debug'),
                                            customer.get('state'),
                                            customer.get('test_points'),
                                            customer.get('test_state'),
                                            customer.get('chat_id'))

cursor.execute(request)
db.commit()

request = """SELECT is_admin, is_debug, state, test_points, test_state
                 FROM customers
                 WHERE chat_id = """ + str(chat_id)

response = db_select(request)[0]
print(response)
