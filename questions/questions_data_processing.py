import os


def chunk_list_by_size(processing_list, num_elems_in_list):
    for chunk in range(0, len(processing_list), num_elems_in_list):
        each_chunk = processing_list[chunk: num_elems_in_list + chunk]

        if len(each_chunk) < num_elems_in_list:
            each_chunk = each_chunk + [None for y in range(num_elems_in_list - len(each_chunk))]
        yield each_chunk


def get_questions_answers_from_files():
    questions_filepath = os.path.dirname(
        os.path.abspath(__file__)
    ) + '/questions_data'
    processed_questions = {}

    for filename in os.listdir(questions_filepath):
        prepared_for_pairing = []
        with open(os.path.join(questions_filepath, filename), 'r', encoding='KOI8-R') as file:
            text = file.read()

        for text_line in text.split('\n\n'):
            if not (
                text_line.startswith('Вопрос') or text_line.startswith('Ответ')
            ):
                continue
            prepared_for_pairing.append(text_line.split('\n', 1)[1])

        title = text.split('\n')[1]
        # processed_questions[title] = []
        processed_questions = []
        for question, answer in chunk_list_by_size(prepared_for_pairing, 2):
            # processed_questions[title].append({'question': question, 'answer': answer})
            processed_questions.append({'question': question.replace('\n', ' '), 'answer': answer})
        # TODO remove break
        break
    return processed_questions


def main():
    get_questions_answers_from_files()


if __name__ == "__main__":
    main()
