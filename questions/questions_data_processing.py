import argparse
import os
import json
import re


def argparser(description='Questions and answers parsing from files'):
    parser = argparse.ArgumentParser(
        description=description
    )
    parser.add_argument(
        '-e', '--encoding', help='Files encoding', default='KOI8-R'
    )
    parser.add_argument(
        '-q',
        '--questpath',
        help='Path to ',
        default='questions/questions_data'
    )
    parser.add_argument(
        '-d',
        '--destpath',
        help='Path to questions to be parsed',
        default='questions/questions.json'
    )
    args = parser.parse_args()
    return args.destpath, args.encoding, args.questpath


def match_data(data):
    regex = r"""
    (?:Вопрос\s(\d*)):\n(.*(?:\n(?!Ответ:$).*)*)\n(?:Ответ:\n(.*(?:\n(?!.*:$).*)*))\n
    (?:Комментарий:\n)?((?!Автор:\n)(?!Зачет:\n)(?!Источник:\n).*(?:\n(?!.*:$).*)*)?(?!Тур:\n)
    """
    matches = re.findall(regex, data, re.VERBOSE | re.MULTILINE)
    return matches


def get_questions_answers_from_files(
    files_encoding='KOI8-R',
    questions_filespath='questions/questions_data'
):
    processed_questions = []

    for filename in os.listdir(questions_filespath):
        with open(
            file=os.path.join(questions_filespath, filename),
            mode='r',
            encoding=files_encoding
        ) as file:
            text = file.read()
            matched_data = match_data(text)
            for question in matched_data:
                processed_questions.append({
                    'question': question[1].replace('\n', ''),
                    'answer': question[2].replace('\n', ''),
                    'comment': question[3].replace('\n', '')
                })
    return processed_questions


def main():

    destination_filepath, files_encoding, questions_filespath = argparser()

    questions = get_questions_answers_from_files(
        files_encoding=files_encoding,
        questions_filespath=questions_filespath
    )
    with open(destination_filepath, 'w', encoding='utf-8') as file:
        json.dump(questions, file, ensure_ascii=False)


if __name__ == "__main__":
    main()
