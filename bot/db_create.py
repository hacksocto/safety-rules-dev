import sqlite3
from os.path import dirname as dn, abspath as ap

db_path = dn(dn(ap(__file__))) + '/data/db'
db = sqlite3.connect(db_path)
cursor = db.cursor()

request = """CREATE TABLE customer (
    chat_id integer,
    is_admin integer,
    is_debug integer,
    state text,
    points integer,
    test_points integer,
    test_state integer
)"""

cursor.execute(request)
db.commit()

request = """SELECT *
             FROM customer"""

print(cursor.execute(request).fetchall())

request = """CREATE TABLE script (
    ID text,
    option text,
    type text,
    points integer,
    links text
)"""

cursor.execute(request)
db.commit()

request = """SELECT *
             FROM script"""

print(cursor.execute(request).fetchall())

records = [('0', 'Начало', 'other', 0, '22'),
           ('22', 'Оказание первой доврачебной медицинской помощи при гипогликемии', 'other', 0, '221'),
           ('221', 'Вы идете по улице ранним летним утром. Проходя мимо парка краем глаза замечаете, что лежит мужчина, от него пахнет алкоголем. Ваши действия:', 'other', 0, '2211 2212'),
           ('2211', 'Пройти мимо, подумая что он просто пьянный', 'other', 0, '22111'),
           ('22111', 'Вы прошли мимо. Возможно этому мужчине требовалась медицинская помощь и он вовсе не пьяный.', 'bad', 0, ''),
           ('2212', 'Подойти и спросить нужна ли помощь.', 'other', 5, '22121'),
           ('22121', 'В ответ тишина...Что дальше?', 'other', 0, '221211 221212'),
           ('221212', 'Вызвать ему скорую помощь и уйти', 'other', 0, '2212121'),
           ('2212121', 'Ему могла понадобиться ваша помощь', 'bad', 0, ''),
           ('221211', 'Проверить дышит ли он и проверить пульс', 'other', 5, '2212111'),
           ('2212111', 'У него есть пульс. Что дальше?', 'other', 0, '22121111 22121112'),
           ('22121111', 'Сначала поднять его', 'other', 0, '221211111'),
           ('221211111', 'При гипогликемии ни в коем случае нельзя поднимать человека, ему нужно лежачее положение.', 'bad', 0, ''),
           ('22121112', 'Сначала вызвать скорую', 'other', 5, '22121112'),
           ('22121112', 'Попытаться спросить, что случилось, он достает из кармана бумажку. У больных гипогликемией всегда есть с собой бумажка, с информацией о своей болезни.', 'other', 0, '221211121'),
           ('221211121', 'Он пришёл в чувства. Что вы ему дадите?', 'other', 0, '2212111211 2212111212'),
           ('2212111211', 'Что-то, не содержащее сахар', 'other', 0, '22121112111'),
           ('22121112111', 'Нужно было дать сахаросодержащий продукт. Но в целом, вы смогли оказать первую помощь человеку', 'good', 5, ''),
           ('2212111212', 'Привести в чувства и дать сладкое до приезда скорой.', 'other', 5, '22121112121'),
           ('22121112121', 'Вы все сделали правильно, вы оказали первую доврачебную медицинскую помощь', 'good', 5, '')]

cursor.executemany('INSERT INTO script VALUES (?,?,?,?,?);', records)

print('{} rows inserted'.format(cursor.rowcount))
db.commit()
db.close()

records = [(0),
           # раздел 1
           (1),
           # сценарий *название*
           (11),
           (111),
           # вариант 1
           (1111),
           # вариант 2
           (1112)]
