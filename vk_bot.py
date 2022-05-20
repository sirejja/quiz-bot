import logging
import os

import vk_api as vk
from dotenv import load_dotenv
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkEventType, VkLongPoll
from vk_api.utils import get_random_id

from redis_controller import (delete_user_cache, get_question_data,
                              get_redis_connection, set_question_data)
from setup_logger import setup_logger
from questions_utils import check_answer, format_answer, get_random_question, load_data

logger = logging.getLogger(__name__)


def send_message(chat_id, vk_api, message):
    keyboard = init_keyboard()
    vk_api.messages.send(
        peer_id=123456,
        user_id=chat_id,
        message=message,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
    )


def handle_new_question_request(event, vk_api):
    chat_id = event.user_id
    delete_user_cache(redis_conn, chat_id)
    question = get_random_question(questions)
    set_question_data(redis_conn, chat_id, question)
    logger.info(f'{question},{chat_id}')
    send_message(
        chat_id,
        vk_api,
        question.get('question')
    )


def handle_solution_attempt(event, vk_api):
    chat_id = event.user_id
    question_data = get_question_data(redis_conn, chat_id)

    if not question_data:
        send_message(
            chat_id,
            vk_api,
            'Нажми на кнопку "Новый вопрос" ;)'
        )
        return

    if check_answer(event.text, question_data['answer']) >= 95:
        send_message(
            chat_id,
            vk_api,
            f'Правильно! Поздравляю!\n'
            f'{format_answer(question_data)}\n'
            f'Для следующего вопроса нажми «Новый вопрос».'
        )
        delete_user_cache(redis_conn, chat_id)
        return
    send_message(
            chat_id,
            vk_api,
            'Неправильно… Попробуешь ещё раз?'
        )


def giveup(event, vk_api):
    chat_id = event.user_id
    question_data = get_question_data(redis_conn, chat_id)
    if not question_data:
        send_message(
            chat_id,
            vk_api,
            'Нажми на кнопку "Новый вопрос" ;)'
        )
        return
    send_message(
        chat_id,
        vk_api,
        f'{format_answer(question_data)}'
    )
    delete_user_cache(redis_conn, chat_id)


def init_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('Мой счёт', color=VkKeyboardColor.PRIMARY)
    return keyboard


def send_score(event, vk_api):
    chat_id = event.user_id
    send_message(
        chat_id,
        vk_api,
        'Пока что просто красивая кнопка'
    )


if __name__ == "__main__":
    load_dotenv()
    
    setup_logger(os.environ['TG_LOGS_TOKEN'], os.environ['TG_CHAT_ID'])
    logger.info('Starting VK quiz bot')
    
    global questions
    global redis_conn

    questions = load_data('questions/questions.json')

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
                handle_new_question_request(event, vk_api)
            elif event.text == "Сдаться":
                giveup(event, vk_api)
            elif event.text == "Мой счёт":
                send_score(event, vk_api)
            else:
                handle_solution_attempt(event, vk_api)
