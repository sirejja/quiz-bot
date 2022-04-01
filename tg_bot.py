from email import message
import logging
import os
import traceback
from dotenv import load_dotenv
from random import randint
from telegram import Bot, KeyboardButton, Update, ReplyKeyboardMarkup
from telegram.ext import (
    CallbackContext, CommandHandler,
    Filters, MessageHandler, Updater
)
from questions.questions_data_processing import get_questions_answers_from_files


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

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
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=get_questions_answers_from_files()[randint(0,50)]['question']
        )



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
    load_dotenv()
    # Create the EventHandler and pass it your bot's token.
    # bot = Bot(os.environ['TG_BOT_TOKEN'])
    updater = Updater(os.environ['TG_BOT_TOKEN'])

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(
        MessageHandler(
            Filters.text & (~Filters.command),
            buttons_handler
        )
    )
    # on noncommand i.e message - echo the message on Telegram
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

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
