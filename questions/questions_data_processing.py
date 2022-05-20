import argparse
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


def get_questions_answers_from_files(files_encoding='KOI8-R'):
    questions_filepath = os.path.dirname(
        os.path.abspath(__file__)
    ) + '/questions_data'
    processed_questions = {}

    for filename in os.listdir(questions_filepath):
        with open(
            file=os.path.join(questions_filepath, filename),
            mode='r',
            encoding=files_encoding
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

    parser = argparse.ArgumentParser(
        description='Парсинг вопросов и ответов для квиза из файла'
    )
    parser.add_argument('-e', '--encoding', help='Кодировка файлов')
    parser.add_argument('-d', '--destpath', help='Путь к разобранному файлу')
    args = parser.parse_args()
    destination_filepath = 'questions/questions.json' if not args.destpath \
        else args.destpath
    files_encoding = 'KOI8-R' if not args.encoding else args.encoding

    questions = get_questions_answers_from_files(files_encoding=files_encoding)
    with open(destination_filepath, 'w', encoding='utf-8') as file:
        json.dump(questions, file, ensure_ascii=False)


if __name__ == "__main__":
    main()
