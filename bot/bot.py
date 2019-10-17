from os.path import join, dirname as dn, abspath as ap
import configparser
import requests


class Bot:
    def __init__(self, name):
        self.name = name
        self.configPath = join(dn(dn(dn(dn(ap(__file__))))), '.ini')
        config = configparser.ConfigParser()
        config.read(self.configPath)
        try:
            self.ownerChatId = config['telegram'][self.name + '_owner']
        except KeyError:
            self.ownerChatId = None
        self.baseUrl = config['telegram']['default_api_url'] + \
            config['telegram'][self.name + '_token']

    def send_message_text(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text}
        url = self.baseUrl + '/sendMessage'
        requests.get(url, params=params)
        return

    def send_message_to_owner(self, text):
        if self.ownerChatId is not None:
            params = {'chat_id': self.ownerChatId, 'text': text}
            url = self.baseUrl + '/sendMessage'
            requests.get(url, params=params)
        return

    def write_owner_chat_id_to_config(self, chatId):
        config = configparser.ConfigParser()
        config.read(self.configPath)
        config['telegram'][self.name + '_owner'] = str(chatId)
        with open(self.configPath, 'w') as f:
            config.write(f)
        return

    def send_custom_keyboard(self, chat_id, text, content):
        json = content
        params = {'chat_id': chat_id, 'text': text, 'reply_markup': json}
        url = self.baseUrl + '/sendMessage'
        requests.post(url, params=params)
        return
