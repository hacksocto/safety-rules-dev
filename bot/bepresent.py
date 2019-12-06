# Для построения путей относительно файла
from os.path import dirname as dn, abspath as ap
import csv  # Для работы с csv файлами
import sqlite3


def db_select(request):
    db_path = dn(dn(ap(__file__))) + '/data/db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    return cursor.execute(request).fetchall()


def db_update(request):
    db_path = dn(dn(ap(__file__))) + '/data/db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(request)
    conn.commit()
    conn.close()
    return


def records_read(chat_id):
    customer = {'chat_id': chat_id, 'is_admin': 0, 'is_debug': 0,
                'state': '', 'points': 0, 'test_points': 0, 'test_state': 0}

    request = """SELECT is_admin, is_debug, state, points, test_points, test_state
                 FROM customer
                 WHERE chat_id={}""".format(chat_id)
    try:
        response = db_select(request)[0]
        customer.update({'is_admin': response[0], 'is_debug': response[1],
                         'state': response[2], 'points': response[3],
                         'test_points': response[4],
                         'test_state': response[5]})
    except IndexError:
        request = """INSERT INTO customer
                     VALUES ({}, 0, 0, '', 0, 0, 0)""".format(chat_id)
        db_update(request)
    return customer


def send_debug_to_admins(event, bot):
    """Проверяет флаги 'is_admin', 'is_debug' и отправляет
        тело входящего запроса, если оба флага 1"""
    msg = 'Body is \n' + str(event)
    request = """SELECT chat_id
                 FROM customer
                 WHERE is_admin = 1 AND is_debug = 1"""
    response = db_select(request)

    for owner in response:
        bot.send_message_text(owner[0], msg)
    return


def records_update(customer):
    request = """UPDATE customer
                 SET is_admin={}, is_debug={}, state='{}',
                 points={}, test_points={}, test_state={}
                 WHERE chat_id={}""".format(customer.get('is_admin'),
                                            customer.get('is_debug'),
                                            customer.get('state'),
                                            customer.get('points'),
                                            customer.get('test_points'),
                                            customer.get('test_state'),
                                            customer.get('chat_id'))
    db_update(request)
    return


def test_ask_question(state, chat_id, bot):
    """Отправляет вопрос из файла"""
    # Инкрементация нужна, т.к. до этого проводилась
    # проверка ответа по предыдущему состоянию
    state += 1
    # Поиск пути относительно файла
    path = dn(dn(ap(__file__))) + '/data/test_questions.csv'
    with open(path, encoding='utf-8-sig') as test:
        reader = csv.DictReader(test, delimiter=',')
        # Поиск по вопросам
        for question in reader:
            if int(question.get('id')) == state:
                # Сохраняет исходное форматирование текста
                text = question.get('text').replace('\\n', '\n')
                key_text = '''{"keyboard":[
                    [{"text":"1"},{"text":"2"}],
                    [{"text":"3"},{"text":"4"}]],
                    "resize_keyboard":true}'''
                bot.send_custom_keyboard(chat_id, text, key_text)
                return state


def test_continuation(customer, state, points, text, chat_id, bot):
    """Проверка ответа на вопрос и отправка нового"""
    # Проверка, отправил ли пользователь число
    try:
        answer = int(text)
    except Exception:
        bot.send_message_text(chat_id, 'Ответ вне диапазона')
        return customer

    # Проверка ответа на диапазон
    if answer < 1 or answer > 4:
        bot.send_message_text(chat_id, 'Ответ вне диапазона')
        return customer

    # Увеличение счета
    points += test_check_answer(state, answer, chat_id, bot)
    # Отправка нового вопроса
    state = test_ask_question(state, chat_id, bot)
    # Запись изменений о пользователе
    customer.update({'test_state': state,
                     'test_points': points})
    return customer


def test_ending(customer, state, points, text, chat_id, bot):
    """Проверка ответа на вопрос, отправка конечного счета"""
    # Проверка, отправил ли пользователь число
    try:
        answer = int(text)
    except Exception:
        bot.send_message_text(chat_id, 'Ответ вне диапазона')
        return customer

    # Проверка ответа на диапазон
    if answer < 1 or answer > 4:
        bot.send_message_text(chat_id, 'Ответ вне диапазона')
        return customer

    # Увеличение счета
    points += test_check_answer(state, answer, chat_id, bot)
    msg = 'Вы набрали ' + str(points) + ' очков. ' \
          'Нажмите на /test, чтобы начать заново'
    key_text = '''{"keyboard":[[{"text":"/test"}]],
                  "resize_keyboard":true}'''
    bot.send_custom_keyboard(chat_id, msg, key_text)
    # Запись изменений о пользователе
    customer.update({'test_state': 0,
                     'test_points': 0})
    return(customer)


def test_check_answer(state, answer, chat_id, bot):
    """Проверка ответа на вопрос и отправка результата"""
    # Построение пути до файла
    path = dn(dn(ap(__file__))) + '/data/test_questions.csv'
    with open(path, encoding='utf-8-sig') as test:
        reader = csv.DictReader(test, delimiter=',')
        # Поиск по вопросам
        for question in reader:
            if int(question.get('id')) == state:
                if int(question.get('answer')) == answer:
                    bot.send_message_text(chat_id, 'Правильный ответ!')
                    return 1
                else:
                    bot.send_message_text(chat_id, 'Неправильный ответ =(')
                    return 0


def script_trigger(customer, chat_id, text, bot):
    state = customer.get('state')
    points = customer.get('points')
    if state != '0':
        request = """SELECT links
                    FROM script
                    WHERE ID='{}'""".format(state)
        response = db_select(request)[0]
        links = response[0].split(' ')
        try:
            state = links[int(text) - 1]
        except Exception:
            msg = 'Такого ответа нет. Попробуйте ввести другое вариант'
            bot.send_message_text(chat_id, msg)
            return customer
        customer.update({'state': state})

    single = True
    repeat = False
    while single:
        request = """SELECT *
                     FROM script
                     WHERE ID='{}'""".format(state)
        response = db_select(request)[0]
        node = {'ID': response[0], 'option': response[1],
                'type': response[2], 'points': response[3],
                'links': response[4].split(' ')}

        points += node.get('points')
        msg = node.get('option')
        if repeat:
            bot.send_message_text(chat_id, msg)
        repeat = True

        if node.get('type') != 'other':
            if node.get('type') == 'bad':
                points = 0
                msg = 'Плохая концовка. Вы набрали {} очков. ' + \
                      'Попробуйте заново /script'

            if node.get('type') == 'good':
                msg = 'Хорошая концовка. Вы набрали {} очков. ' + \
                      'Попробуйте другие сценарии /script'
            key_text = '''{"keyboard":[[{"text":"/script"}]],
                          "resize_keyboard":true}'''
            msg = msg.format(points)
            bot.send_custom_keyboard(chat_id, msg, key_text)

            customer.update({'points': points, 'state': ''})
            return customer

        request = """SELECT ID, option
                     FROM script
                     WHERE ID in ("""
        for link in node.get('links'):
            request = request + "'{}',".format(link)
        request = request[:-1] + ')'
        response = db_select(request)
        length = len(response)
        if length == 1:
            state = response[0][0]
            customer.update({'state': state})
        else:
            single = False

    key_text = button_constructor(length)
    msg = ''
    counter = 1
    for option in response:
        msg = msg + '{}. {}\n\n'.format(counter, option[1])
        counter = counter + 1
    bot.send_custom_keyboard(chat_id, msg, key_text)

    return customer


def button_constructor(length):
    """Создание кастомной клавиатуры (хак)"""
    # TODO нужно ли большее количество?
    dimensions = [[1, 1], [2, 1], [3, 1], [4, 1], [5, 1],
                  [3, 2], [4, 2], [4, 2], [3, 3], [5, 2]]
    rowsAmount = dimensions[length - 1][0]
    colsAmount = dimensions[length - 1][1]
    current = 1
    json = '{"keyboard":[['

    for row in range(colsAmount):
        for col in range(rowsAmount):
            json = json + '{"text": "' + str(current) + '"}, '
            current = current + 1
        if length == 7:
            rowsAmount = rowsAmount - 1
        json = json[:-2] + '], ['
    json = json[:-3] + '], "resize_keyboard":true}'
    return json


def handle(bot, event):
    """Обработка входящего сообщения"""
    chat_id = event['message']['chat']['id']
    text = event['message']['text']
    customer = records_read(chat_id)
    test_state = customer.get('test_state')
    test_points = customer.get('test_points')

    send_debug_to_admins(event, bot)
    if text[0] == '/':

        # Разбивает команду по пробелам
        divided_text = text.split(' ')

        """Приветственное сообщение"""
        if len(divided_text) == 1 and \
           divided_text[0] == '/start':
            # Запись изменений о пользователе
            customer.update({'test_state': 0,
                             'test_points': 0})
            records_update(customer)
            key_text = '''{"keyboard":[[{"text":"/script"}]],
                          "resize_keyboard":true}'''
            msg = 'Нажмите на кнопку /script, чтобы запустить сценарий'
            bot.send_custom_keyboard(chat_id, msg, key_text)
            return

        """Параметр start"""
        if len(divided_text) == 2 and \
           divided_text[0] == '/start':
            bot.send_message_text(chat_id, 'ECHO: ' + divided_text[1])
            # Запись изменений о пользователе
            customer.update({'test_state': 0,
                             'test_points': 0})
            records_update(customer)
            return

        """Запись пользователя в администраторы"""
        if len(divided_text) == 2 and \
           divided_text[0] == '/key' and \
           divided_text[1] == 'passwd':

            # TODO подчистить
            # bot.write_owner_chat_id_to_config(chat_id)
            bot.send_message_text(chat_id, 'Администратор опознан')
            # Запись изменений о пользователе
            customer.update({'is_admin': 1})
            records_update(customer)
            return

        """Включение режима отладки"""
        if len(divided_text) == 1 and \
           divided_text[0] == '/on' and \
           int(customer.get('is_admin')) == 1:

            bot.send_message_text(chat_id, 'Debug mode ON')
            # Запись изменений о пользователе
            customer.update({'is_debug': 1})
            records_update(customer)
            return

        """Выключение режима отладки"""
        if len(divided_text) == 1 and \
           divided_text[0] == '/off' and \
           int(customer.get('is_admin')) == 1:

            bot.send_message_text(chat_id, 'Debug mode OFF')
            # Запись изменений о пользователе
            customer.update({'is_debug': 0})
            records_update(customer)
            return

        """Запуск теста"""
        if len(divided_text) == 1 and \
           divided_text[0] == '/test':

            test_state = 0
            test_state = test_ask_question(test_state, chat_id, bot)
            # Запись изменений о пользователе
            customer.update({'test_state': test_state,
                             'test_points': 0})
            records_update(customer)
            return

        if len(divided_text) == 1 and \
           divided_text[0] == '/script':

            customer.update({'state': '0'})
            customer = script_trigger(customer, chat_id, text, bot)
            records_update(customer)
            return

        if len(divided_text) == 1 and \
           divided_text[0] == '/stop' and \
           customer.get('state') != '':

            msg = """Сценарий сброшен. Для того, чтобы
                     начать заново, отправьте /script"""
            key_text = """{"keyboard":[[{"text":"/script"}]],
                          "resize_keyboard":true}"""
            bot.send_custom_keyboard(chat_id, msg, key_text)

            customer.update({'state': ''})
            records_update(customer)
            return

        """Если ни одно ветвление не сработало"""
        msg = 'Неизвестная команда. Повторите, пожалуйста'
        bot.send_message_text(chat_id, msg)
        return

    """Запуск концовки теста"""
    if test_state == 10:
        customer = test_ending(customer, test_state, test_points,
                               text, chat_id, bot)
        records_update(customer)
        return

    """Продолжение теста"""
    if test_state > 0:

        customer = test_continuation(customer, test_state, test_points,
                                     text, chat_id, bot)
        records_update(customer)
        return

    if customer.get('state') != '':
        customer = script_trigger(customer, chat_id, text, bot)
        records_update(customer)
        return

    """Если ни одна из ветвей не сработала"""
    msg = 'Я вас не понял. Повторите, пожалуйста'
    bot.send_message_text(chat_id, msg)
    return
