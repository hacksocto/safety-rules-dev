from bot.bot import TelegramBot
# TODO Для деплоя
# from .bot.bot import TelegramBot


def debug(event):
    """Отправляет сообщение на вход обработчика бота.
        Необходимо вставить токен в cfg.ini и событие в event"""
    TelegramBot('safetyrulesdev').handle(event)


# Дебаг происходит только если файл запускается напрямую
if __name__ == '__main__':
    event = {}
    debug(event)
