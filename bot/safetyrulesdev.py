from os.path import dirname as dn, abspath as ap
import csv
from .bot import Bot


class IncomingEvent:
    def __init__(self, event):
        self.event = event
        self.chat_id = self.event['message']['chat']['id']
        self.bot = Bot('safetyrulesdev')

    def handle(self):
        self.text = self.event['message']['text']
        self.customer, records, fieldnames = self.find_records()
        self.send_debug_to_owners(records, self.event)

        trivia_state = (int(self.customer.get('trivia_state')))
        trivia_points = (int(self.customer.get('trivia_points')))

        if self.text[0] == '/':
            partedText = self.text.split(' ')

            if len(partedText) == 1 and \
               partedText[0] == '/start':
                key_text = '''{"keyboard":[[{"text":"/test"}]],
                               "resize_keyboard":true}'''
                text = 'Нажмите на кнопку, чтобы начать тест'
                self.bot.send_custom_keyboard(self.chat_id, text, key_text)
                return

            if len(partedText) == 2 and \
               partedText[0] == '/key' and partedText[1] == 'passwd':
                self.bot.write_owner_chat_id_to_config(self.chat_id)
                self.bot.send_message_text(self.chat_id, 'owner was linked!')
                self.customer.update({'is_owner': 1})
                self.records_update(self.customer, records, fieldnames)
                return

            if partedText[0] == '/on' and \
               int(self.customer.get('is_owner')) == 1:
                self.customer.update({'is_debug': 1})
                self.records_update(self.customer, records, fieldnames)
                return

            if partedText[0] == '/off' and \
               int(self.customer.get('is_owner')) == 1:
                self.customer.update({'is_debug': 0})
                self.records_update(self.customer, records, fieldnames)
                return

            if partedText[0] == '/test' and len(partedText) == 1:
                trivia_state = 0
                trivia_state = self.ask_trivia_question(trivia_state)
                self.customer.update({'trivia_state': trivia_state,
                                      'trivia_points': 0})
                self.records_update(self.customer, records, fieldnames)
                return

            msg = 'Неизвестная команда. Повторите, пожалуйста'
            self.bot.send_message_text(self.chat_id, msg)
            return

        if trivia_state > 0 and trivia_state < 10:
            self.customer = self.continue_trivia(trivia_state, trivia_points)
            self.records_update(self.customer, records, fieldnames)
            return

        if trivia_state == 10:
            self.customer = self.end_trivia(trivia_state, trivia_points)
            self.records_update(self.customer, records, fieldnames)
            return

        msg = 'Я вас не понял. Повторите, пожалуйста'
        self.bot.send_message_text(self.chat_id, msg)
        return

    def find_records(self):
        customersPath = dn(dn(ap(__file__))) + '/db/customers.csv'
        fieldnames = []
        records = []
        customer = None
        with open(customersPath, encoding='utf-8') as customers:
            reader = csv.DictReader(customers, delimiter=',')
            for record in reader:
                records.append(record)
                if self.chat_id == int(record.get('chat_id')):
                    customer = record.copy()
            fieldnames = reader.fieldnames
        if customer is None:
            customer = {'chat_id': self.chat_id,
                        'is_owner': 0, 'is_debug': 0, 'state': 0,
                        'trivia_points': 0, 'trivia_state': 0}
            records.append(customer)
        return customer, records, fieldnames

    def records_update(self, customer, records, fieldnames):
        customersPath = dn(dn(ap(__file__))) + '/db/customers.csv'
        with open(customersPath, 'w', encoding='utf-8', newline='') as output:
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            for record in records:
                if record.get('chat_id') == customer.get('chat_id'):
                    record.update(customer)
                writer.writerow(record)
        return

    def ask_trivia_question(self, state):
        state += 1
        triviaPath = dn(dn(ap(__file__))) + '/db/trivia_questions.csv'
        with open(triviaPath, encoding='utf-8-sig') as trivia:
            reader = csv.DictReader(trivia, delimiter=',')
            for question in reader:
                if int(question.get('id')) == state:
                    text = question.get('text').replace('\\n', '\n')
                    key_text = '''{"keyboard":[
                        [{"text":"1"},{"text":"2"}],
                        [{"text":"3"},{"text":"4"}]],
                        "resize_keyboard":true}'''
                    self.bot.send_custom_keyboard(self.chat_id, text, key_text)
                    return state

    def check_trivia_answer(self, state, answer):
        triviaPath = dn(dn(ap(__file__))) + '/db/trivia_questions.csv'
        with open(triviaPath, encoding='utf-8-sig') as trivia:
            reader = csv.DictReader(trivia, delimiter=',')
            for question in reader:
                if int(question.get('id')) == state:
                    if int(question.get('answer')) == answer:
                        self.bot.send_message_text(self.chat_id, 'Верно!')
                        return 1
                    else:
                        self.bot.send_message_text(self.chat_id, 'Неверно =(')
                        return 0

    def continue_trivia(self, state, points):
        try:
            answer = int(self.text)
        except Exception:
            self.bot.send_message_text(self.chat_id, 'Ответ вне диапазона')
            return self.customer
        if answer < 1 or answer > 4:
            self.bot.send_message_text(self.chat_id, 'Ответ вне диапазона')
            return self.customer
        points += self.check_trivia_answer(state, answer)
        state = self.ask_trivia_question(state)
        self.customer.update({'trivia_state': state,
                              'trivia_points': points})
        return self.customer

    def end_trivia(self, state, points):
        try:
            answer = int(self.text)
        except Exception:
            self.bot.send_message_text(self.chat_id, 'Ответ вне диапазона')
            return self.customer
        if answer < 1 or answer > 4:
            self.bot.send_message_text(self.chat_id, 'Ответ вне диапазона')
            return self.customer
        points += self.check_trivia_answer(state, answer)
        fin_text = 'Вы набрали ' + str(points) + ' очков. ' \
                   'Нажмите на /test, чтобы начать заново'
        key_text = '''{"keyboard":[[{"text":"/test"}]],
                       "resize_keyboard":true}'''
        self.bot.send_custom_keyboard(self.chat_id, fin_text, key_text)
        self.customer.update({'trivia_state': 0,
                              'trivia_points': 0})
        return self.customer

    def send_debug_to_owners(self, records, body):
        for record in records:
            if int(record.get('is_owner')) == 1 and \
               int(record.get('is_debug')) == 1:
                self.bot.send_message_text(record.get('chat_id'),
                                           'Body is \n' + str(body))
        return
