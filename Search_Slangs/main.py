from flask import Flask, request, jsonify
from sqlalchemy import text, create_engine

import os

app = Flask(__name__)

# Database connection
DATABASE_URL = os.environ.get('DATABASE_URL')
engine = create_engine(DATABASE_URL)

# Fetch slang words from txt file. Could be replaced with api or database in future
slang_words = []
with open('slangs.txt', 'r', encoding='utf-8') as slangs_text:
    for slang in slangs_text:
        # truncate the \n and convert to lowercase
        slang_words.append(slang[:-1].lower())


@app.route('/', methods=['POST'], strict_slashes=False)
def search_slangs():
    ''' 
        input city column id from client and check for slang words
        compares the responses with known slang words list
        outputs the slang words found in responses
    '''

    data = request.json  # Assuming JSON format
    form_id = data.get('form_id')
    text_question_id = data.get('text_question_id')
    city_question_id = data.get('city_question_id')
    city = data.get('city')

    # filters responses based on the city and then compares its responses
    query = text('''
                SELECT Answer.answer_text
                    FROM Answer
                    JOIN Response ON Answer.response_id = Response.id
                    JOIN Question ON Answer.question_id = Question.id
                    JOIN (
                        SELECT Response.id
                        FROM Response
                        JOIN Answer ON Response.id = Answer.response_id
                        JOIN Question ON Answer.question_id = Question.id
                        WHERE Question.id = :city_question_id AND Answer.answer_text = :city AND Response.form_id = :form_id
                    ) AS CityResponses ON CityResponses.id = Response.id
                    WHERE Question.id = :text_question_id AND Response.form_id = :form_id;
''')

    with engine.connect() as connection:
        responses = connection.execute(
            query, {'form_id': form_id, 'text_question_id': text_question_id,
                    'city_question_id': city_question_id, 'city': city}).fetchall()

        # Search for slangs in the text answers
        slangs = []
        try:
            for response in responses:
                slangs.extend(find_slangs(response[0].lower()))
            return jsonify(slangs=list(set(slangs)))

        except Exception as error:
            print(error, flush=True)
            return error


def find_slangs(txt):
    ''' Find slangs in the text '''
    print(txt, slang_words, flush=True)
    return [word for word in slang_words if word in txt]


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=os.environ.get('DEBUG'))
