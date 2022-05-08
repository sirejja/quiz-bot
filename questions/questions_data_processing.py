import os
import json


def get_questions_answers_from_files():
    questions_filepath = os.path.dirname(
        os.path.abspath(__file__)
    ) + '/questions_data'
    processed_questions = {}
    print(len(os.listdir(questions_filepath)))
    count = 0
    for filename in os.listdir(questions_filepath):
        count += 1
        prepared_for_pairing = []

        with open(
            os.path.join(questions_filepath, filename), 'r', encoding='KOI8-R'
        ) as file:
            text = file.read()

        for text_line in text.split('\n\n'):
            if not (
                text_line.startswith('Вопрос') or text_line.startswith('Ответ') 
                or text_line.startswith('Комментарий')
            ):
                continue
            prepared_for_pairing.append(text_line.split('\n')[1])
        print(prepared_for_pairing)
        # title = text.split('\n')[1]
        # processed_questions[title] = []
        processed_questions = []
        for question in prepared_for_pairing:

            # processed_questions[title].append({'question': question, 'answer': answer})
            processed_questions.append({
                'question': question[0].replace('\n', ' '),
                'answer': question[1]
            })
        break
    print(count)
    return processed_questions


def main():
    a = get_questions_answers_from_files()
    print(len(a))
    with open('questions/dict.json', 'w', encoding='utf-8') as file:
        json.dump(a, file, ensure_ascii=False)


if __name__ == "__main__":
    main()
