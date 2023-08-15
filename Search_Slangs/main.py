from flask import Flask, request, jsonify
from sqlalchemy import text, create_engine
from requests import Session

import os

app = Flask(__name__)

# helps identify the microservice during logging
session = Session()
session.headers.update({'X-Docker-Domain': 'search_slangs'})
LOGGER_URL = os.environ.get('LOGGER_URL')

# Database connection
DATABASE_URL = os.environ.get('DATABASE_URL')
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

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

    try:
        data = request.json
        form_id = data['form_id']
        text_question_id = data['text_question_id']
        city_question_id = data['city_question_id']
        city = data['city']

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

            for response in responses:
                slangs.extend(find_slangs(response[0].lower()))

            # Log successful search
            log_data = {'message': 'Slang Search done'}
            session.post(f'{LOGGER_URL}/log', json=log_data)

            return jsonify(slangs=list(set(slangs)))

    except Exception as error:
        # Log Error
        log_data = {'message': str(error), 'level': 'error'}
        session.post(f'{LOGGER_URL}/log', json=log_data)

        return jsonify(message='Error occurred: check logs for details'), 500


def find_slangs(txt):
    ''' Find slangs in the text '''
    return [word for word in slang_words if word in txt]


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=os.environ.get('DEBUG'))
