import os
import json
import re


def match_data(data):
    regex = r"""
    (?:Вопрос\s(\d*)):\n(.*(?:\n(?!Ответ:$).*)*)\n(?:Ответ:\n(.*(?:\n(?!.*:$).*)*))\n
    (?:Комментарий:\n)?((?!Автор:\n)(?!Зачет:\n)(?!Источник:\n).*(?:\n(?!.*:$).*)*)?(?!Тур:\n)
    """
    matches = re.findall(regex, data, re.VERBOSE | re.MULTILINE)
    return matches


def get_questions_answers_from_files():
    questions_filepath = os.path.dirname(
        os.path.abspath(__file__)
    ) + '/questions_data'
    processed_questions = {}

    for filename in os.listdir(questions_filepath):
        with open(
            os.path.join(questions_filepath, filename), 'r', encoding='KOI8-R'
        ) as file:
            text = file.read()
            title = text.split('\n')[1]
            processed_questions[title] = []
            matched_data = match_data(text)
            for question in matched_data:
                processed_questions[title].append({
                    'question': question[1].replace('\n', ''),
                    'answer': question[2].replace('\n', ''),
                    'comment': question[3].replace('\n', '')
                })
    return processed_questions


def main():
    questions = get_questions_answers_from_files()
    with open('questions/questions.json', 'w', encoding='utf-8') as file:
        json.dump(questions, file, ensure_ascii=False)


if __name__ == "__main__":
    main()
