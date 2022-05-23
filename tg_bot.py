import argparse
import json
import logging
import os

from dotenv import load_dotenv
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import (CallbackContext, CommandHandler, ConversationHandler,
                          Filters, MessageHandler, Updater)
from questions.questions_data_processing import argparser, get_questions_answers_from_files

from questions_utils import (check_answer, format_answer, get_random_question,
                             load_data)
from redis_controller import get_redis_connection
from setup_logger import setup_logger

logger = logging.getLogger(__name__)
CHOOSING, TYPING_REPLY = range(2)


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
        [
            reply_buttons[i:i + 2] for i in range(0, len(reply_buttons), 2)
        ]
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
    user_id = f'tg-{update.effective_chat.id}'

    context.bot_data['redis_conn'].delete(user_id)

    question = get_random_question(
        context.bot_data['questions']
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=question.get('question')
    )

    context.bot_data['redis_conn'].set(
        user_id,
        json.dumps(question)
    )
    logger.info(f'{question},{user_id}')
    return TYPING_REPLY


def handle_solution_attempt(
    update: Update,
    context: CallbackContext
):
    user_id = f'tg-{update.effective_chat.id}'
    question_data = json.loads(
        str(
            context.bot_data['redis_conn'].get(
                user_id
            ),
            encoding='utf-8'
        )
    )

    if not question_data:
        return CHOOSING

    if check_answer(update.message.text, question_data['answer']) >= 95:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Правильно! Поздравляю!\n'
                 f'{format_answer(question_data)}\n'
                 f'Для следующего вопроса нажми «Новый вопрос».'
        )
        context.bot_data['redis_conn'].delete(user_id)
        return CHOOSING

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Неправильно… Попробуешь ещё раз?'
    )
    return TYPING_REPLY


def giveup(
    update: Update,
    context: CallbackContext
):
    user_id = f'tg-{update.effective_chat.id}'
    try:
        question_data = json.loads(
            str(
                context.bot_data['redis_conn'].get(
                    user_id
                ),
                encoding='utf-8'
            )
        )
    except TypeError:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Нажми на кнопку "Новый вопрос" ;)'
        )
        return
    if not question_data:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Нажми на кнопку "Новый вопрос" ;)'
        )
        return CHOOSING
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'{format_answer(question_data)}'
    )
    context.bot_data['redis_conn'].delete(user_id)
    return CHOOSING


def send_score(
    update: Update,
    context: CallbackContext
):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Пока что просто красивая кнопка'
    )
    return CHOOSING


def main():
    load_dotenv()
    setup_logger(os.environ['TG_LOGS_TOKEN'], os.environ['TG_CHAT_ID'])
    logger.info('Starting TG quiz bot')

    _, files_encoding, questions_filespath = argparser(description='TG bot startup')

    questions = get_questions_answers_from_files(
        files_encoding=files_encoding,
        questions_filespath=questions_filespath
    )

    updater = Updater(os.environ['TG_BOT_TOKEN'])
    dispatcher = updater.dispatcher

    dispatcher.bot_data['redis_conn'] = get_redis_connection(
        os.environ['REDIS_HOST'],
        os.environ['REDIS_PORT'],
        os.environ['REDIS_PASSWORD']
    )
    dispatcher.bot_data['questions'] = questions

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
