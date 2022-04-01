import logging
from telegram import Bot


_log_format = (
    "%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s)"
    ".%(funcName)s(%(lineno)d) - %(message)s"
)


class LogBotHandler(logging.Handler):
    def __init__(self, tg_bot, chat_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tg_bot = tg_bot
        self.chat_id = chat_id

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(
            chat_id=self.chat_id,
            text=log_entry
        )


def setup_logger(tg_token_logs, chat_id):

    logger = logging.getLogger()

    bot_handler = LogBotHandler(
        Bot(token=tg_token_logs),
        chat_id
    )
    bot_handler.setLevel(logging.DEBUG)
    bot_handler.setFormatter(logging.Formatter(_log_format))

    logger.addHandler(bot_handler)

    return logger
