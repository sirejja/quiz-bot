import argparse
import json
import logging
import os

import vk_api as vk
from dotenv import load_dotenv
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkEventType, VkLongPoll
from vk_api.utils import get_random_id
from questions.questions_data_processing import argparser, get_questions_answers_from_files

from questions_utils import (check_answer, format_answer, get_random_question,
                             load_data)
from redis_controller import get_redis_connection
from setup_logger import setup_logger

logger = logging.getLogger(__name__)


def send_message(event, vk_api, message):
    keyboard = init_keyboard()
    vk_api.messages.send(
        peer_id=event.peer_id,
        user_id=event.user_id,
        message=message,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
    )


def handle_new_question_request(redis_conn, event, vk_api, questions):
    user_id = f'vk-{event.user_id}'
    redis_conn.delete(user_id)
    question = get_random_question(questions)
    redis_conn.set(
        user_id,
        json.dumps(question)
    )
    logger.info(f'{question},{user_id}')
    send_message(
        event,
        vk_api,
        question.get('question')
    )


def handle_solution_attempt(redis_conn, event, vk_api):
    user_id = f'vk-{event.user_id}'
    question_data = json.loads(
        str(
            redis_conn.get(
                user_id
            ),
            encoding='utf-8'
        )
    )

    if not question_data:
        send_message(
            event,
            vk_api,
            'Нажми на кнопку "Новый вопрос" ;)'
        )
        return

    if check_answer(event.text, question_data['answer']) >= 95:
        send_message(
            event,
            vk_api,
            f'Правильно! Поздравляю!\n'
            f'{format_answer(question_data)}\n'
            f'Для следующего вопроса нажми «Новый вопрос».'
        )
        redis_conn.delete(user_id)
        return
    send_message(
            event,
            vk_api,
            'Неправильно… Попробуешь ещё раз?'
        )


def giveup(redis_conn, event, vk_api):
    user_id = f'vk-{event.user_id}'
    try:
        question_data = json.loads(
            str(
                redis_conn.get(
                    user_id
                ),
                encoding='utf-8'
            )
        )
    except TypeError:
        send_message(
            event,
            vk_api,
            'Нажми на кнопку "Новый вопрос" ;)'
        )
        return

    if not question_data:
        send_message(
            event,
            vk_api,
            'Нажми на кнопку "Новый вопрос" ;)'
        )
        return

    send_message(
        event,
        vk_api,
        format_answer(question_data)
    )
    redis_conn.delete(user_id)


def init_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('Мой счёт', color=VkKeyboardColor.PRIMARY)
    return keyboard


def send_score(redis_conn, event, vk_api):
    send_message(
        event,
        vk_api,
        'Пока что просто красивая кнопка'
    )


if __name__ == "__main__":
    load_dotenv()

    setup_logger(os.environ['TG_LOGS_TOKEN'], os.environ['TG_CHAT_ID'])
    logger.info('Starting VK quiz bot')

    _, files_encoding, questions_filespath = argparser(description='VK bot startup')

    questions = get_questions_answers_from_files(
        files_encoding=files_encoding,
        questions_filespath=questions_filespath
    )

    redis_conn = get_redis_connection(
        os.environ['REDIS_HOST'],
        os.environ['REDIS_PORT'],
        os.environ['REDIS_PASSWORD']
    )

    vk_session = vk.VkApi(token=os.environ['VK_BOT_TOKEN'])
    vk_api = vk_session.get_api()

    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == "Новый вопрос":
                handle_new_question_request(
                    redis_conn, event, vk_api, questions
                )
            elif event.text == "Сдаться":
                giveup(redis_conn, event, vk_api)
            elif event.text == "Мой счёт":
                send_score(redis_conn, event, vk_api)
            else:
                handle_solution_attempt(redis_conn, event, vk_api)
