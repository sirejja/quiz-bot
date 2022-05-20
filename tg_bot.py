import logging
import os

from dotenv import load_dotenv
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import (CallbackContext, CommandHandler, ConversationHandler,
                          Filters, MessageHandler, Updater)

from redis_controller import (delete_user_cache, get_question_data,
                              get_redis_connection, set_question_data)
from setup_logger import setup_logger
from questions_utils import check_answer, format_answer, get_random_question, load_data

logger = logging.getLogger(__name__)
CHOOSING, TYPING_REPLY = range(2)


def build_menu(
    buttons,
    n_cols,
    header_buttons=None,
    footer_buttons=None
):
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
            KeyboardButton('Новый вопрос'),
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


def handle_new_question_request(
    update: Update,
    context: CallbackContext
):
    chat_id = update.effective_chat.id
    delete_user_cache(redis_conn, chat_id)

    question = get_random_question(questions)
    context.bot.send_message(
        chat_id=chat_id,
        text=question.get('question')
    )
    print(question.get('answer'))
    set_question_data(redis_conn, chat_id, question)
    logger.info(f'{question},{chat_id}')
    return TYPING_REPLY


def handle_solution_attempt(
    update: Update,
    context: CallbackContext
):
    chat_id = update.effective_chat.id
    question_data = get_question_data(redis_conn, chat_id)

    if not question_data:
        return CHOOSING

    if check_answer(update.message.text, question_data['answer']) >= 95:
        context.bot.send_message(
            chat_id=chat_id,
            text=f'Правильно! Поздравляю!\n'
                 f'{format_answer(question_data)}\n'
                 f'Для следующего вопроса нажми «Новый вопрос».'
        )
        delete_user_cache(redis_conn, chat_id)
        return CHOOSING

    context.bot.send_message(
        chat_id=chat_id,
        text='Неправильно… Попробуешь ещё раз?'
    )
    return TYPING_REPLY


def giveup(
    update: Update,
    context: CallbackContext
):
    chat_id = update.effective_chat.id
    question_data = get_question_data(redis_conn, chat_id)
    if not question_data:
        context.bot.send_message(
            chat_id=chat_id,
            text='Нажми на кнопку "Новый вопрос" ;)'
        )
        return CHOOSING
    context.bot.send_message(
        chat_id=chat_id,
        text=f'{format_answer(question_data)}'
    )
    delete_user_cache(redis_conn, chat_id)
    return CHOOSING


def send_score(
    update: Update,
    context: CallbackContext
):
    chat_id = update.effective_chat.id
    context.bot.send_message(
        chat_id=chat_id,
        text='Пока что просто красивая кнопка'
    )
    return CHOOSING


def main():
    load_dotenv()
    setup_logger(os.environ['TG_LOGS_TOKEN'], os.environ['TG_CHAT_ID'])
    logger.info('Starting TG quiz bot')

    global questions
    global redis_conn

    questions = load_data('questions/questions.json')

    redis_conn = get_redis_connection(
        os.environ['REDIS_HOST'],
        os.environ['REDIS_PORT'],
        os.environ['REDIS_PASSWORD']
    )

    updater = Updater(os.environ['TG_BOT_TOKEN'])
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            MessageHandler(
                Filters.regex('^Новый вопрос$'),
                handle_new_question_request
            ),
            MessageHandler(
                Filters.regex('^Сдаться$'),
                giveup
            ),
            MessageHandler(
                Filters.text,
                handle_solution_attempt,
                pass_user_data=True
            ),
            MessageHandler(
                Filters.regex('^Мой счет$'),
                send_score
            )
        ],  # type: ignore

        states={
            CHOOSING: [
                MessageHandler(
                    Filters.regex('^Новый вопрос$'),
                    handle_new_question_request
                ),
                MessageHandler(
                    Filters.regex('^Сдаться$'),
                    giveup
                ),
                MessageHandler(
                    Filters.regex('^Мой счёт$'),
                    send_score
                )
            ],
            TYPING_REPLY: [
                MessageHandler(
                    Filters.regex('^Сдаться$'),
                    giveup
                ),
                MessageHandler(
                    Filters.text,
                    handle_solution_attempt,
                    pass_user_data=True
                ),
                MessageHandler(
                    Filters.regex('^Мой счёт$'),
                    send_score
                )
            ],
        },  # type: ignore

        fallbacks=[
            MessageHandler(
                Filters.regex('^Сдаться$'),
                giveup
            ),
            MessageHandler(
                Filters.regex('^Мой счёт$'),
                send_score
            )
        ]  # type: ignore
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT
    updater.idle()


if __name__ == '__main__':
    main()
