import logging
import os
import traceback
from random import randint

import redis
from dotenv import load_dotenv
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import (CallbackContext, CommandHandler, Filters,
                          MessageHandler, Updater)

from questions.questions_data_processing import \
    get_questions_answers_from_files


# Enable logging
logger = logging.getLogger(__name__)


def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


def start(
    update: Update,
    context: CallbackContext
):

    reply_buttons = [
            KeyboardButton('Новый вопрос', callback_data='/new_q'),
            KeyboardButton('Сдаться'),
            KeyboardButton('Мой счёт')
    ]

    reply_markup = ReplyKeyboardMarkup(
        build_menu(
            buttons=reply_buttons,
            n_cols=2
        )
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Привет, я бот для викторин!',
        reply_markup=reply_markup
    )


def buttons_handler(
    update: Update,
    context: CallbackContext
):
    if 'Новый вопрос' in update.message.text:
        question = get_questions_answers_from_files()[
            randint(0, 15)
        ]['question']

        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=question
        )
        context.bot_data['redis_connection'].set(
            update.effective_chat.id,
            question
        )
        print(context.bot_data['redis_connection'].get(update.effective_chat.id))


def help(
    update: Update,
    context: CallbackContext
):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Help!'
    )


def echo(
    update: Update,
    context: CallbackContext
):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=update.message.text
    )


def error(
    update,
    error
):
    """Log Errors caused by Updates."""
    print(traceback.format_exc())
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    load_dotenv()

    redis_pool = redis.ConnectionPool(
        host=os.environ['REDIS_HOST'],
        port=os.environ['REDIS_PORT'],
        password=os.environ['REDIS_PASSWORD']
    )
    redis_connection = redis.Redis(connection_pool=redis_pool)

    # bot = Bot(os.environ['TG_BOT_TOKEN'])
    updater = Updater(os.environ['TG_BOT_TOKEN'])
    dp = updater.dispatcher

    dp.bot_data['redis_connection'] = redis_connection
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    dp.add_handler(
        MessageHandler(
            Filters.text & (~Filters.command),
            buttons_handler
        )
    )

    dp.add_handler(
        MessageHandler(
            Filters.text & (~Filters.command),
            echo
        )
    )

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT
    updater.idle()


if __name__ == '__main__':
    main()
