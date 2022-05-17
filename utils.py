import json
import random
from fuzzywuzzy import fuzz


def load_data(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
    return data


def get_random_question(data):
    random_champ = random.choice(list(data.keys()))
    random_question = random.choice(data[random_champ])
    return random_question


def check_answer(user_answer, base_answer):
    return fuzz.WRatio(
            user_answer,
            base_answer
    )


def format_answer(question):
    if not question['comment']:
        return f'\n{question["answer"]}\n'
    return f'{question["answer"]}\n ({question["comment"]})\n'
