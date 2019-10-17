from os.path import join, dirname as dn, abspath as ap
import configparser
import requests

from . import safetyrulesdev


class TelegramBot:
    def __init__(self, name):
        self.name = name
        # self.config_path = join(dn(dn(dn(dn(ap(__file__))))), '.ini')
        self.config_path = join(dn(ap(__file__)), 'cfg.ini')
        config = configparser.ConfigParser()
        config.read(self.config_path)
        try:
            self.owner_chat_id = config['telegram'][self.name + '_owner']
        except KeyError:
            self.owner_chat_id = None
        self.base_url = config['telegram']['default_api_url'] + \
            config['telegram'][self.name + '_token']

    def handle(self, event):
        if self.name == 'safetyrulesdev':
            try:
                safetyrulesdev.handle(self, event)
            except Exception:
                self.send_message_text(self.owner_chat_id, 'ERROR')
                print('err')
                return
        return

    def send_message_to_owner(self, text):
        if self.owner_chat_id is not None:
            params = {'chat_id': self.owner_chat_id, 'text': text}
            url = self.base_url + '/sendMessage'
            requests.get(url, params=params)
        return

    def send_message_text(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text}
        url = self.base_url + '/sendMessage'
        requests.get(url, params=params)
        return

    def send_custom_keyboard(self, chat_id, text, json):
        params = {'chat_id': chat_id, 'text': text, 'reply_markup': json}
        url = self.base_url + '/sendMessage'
        requests.post(url, params=params)
        return

    def write_owner_chat_id_to_config(self, chat_id):
        config = configparser.ConfigParser()
        config.read(self.config_path)
        config['telegram'][self.name + '_owner'] = str(chat_id)
        with open(self.config_path, 'w') as f:
            config.write(f)
        return
