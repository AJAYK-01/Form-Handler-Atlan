## Permission to local directory to store the database 

sudo chmod -R a+rwx,go-w ./Database_Data

## Sample commands i did to create data

curl -X POST http://localhost:5000/create-form \
    -H "Content-Type: application/json" \
    -d '{"title": "My Form", "questions": [{"question_text": "Do you like ice cream?", "question_type": "Yes/No"}, {"question_text": "What is your favorite flavor?", "question_type": "Text"}]}'


curl -X POST http://localhost:5000/submit-response \
    -H "Content-Type: application/json" \
    -d '{"form_id": 1, "email": "test@example.com", "answers": [{"question_id": 1, "answer_text": "Yes"}, {"question_id": 2, "answer_text": "Chocolate"}]}'


curl -X POST http://localhost:5000/create-form \
    -H "Content-Type: application/json" \
    -d '{"title": "BioData", "questions": [{"question_text": "What is your name?", "question_type": "text"}, {"question_text": "What is your age?", "question_type": "number"}]}'


curl -X POST http://localhost:5000/submit-response \
    -H "Content-Type: application/json" \
    -d '{"form_id": 2, "email": "akkk@test.com", "answers": [{"question_id": 1, "answer_text": "Rahul"}, {"question_id": 2, "answer_text": "22"}]}'


curl -X POST http://localhost:5000/submit-response \
    -H "Content-Type: application/json" \
    -d '{"form_id": 2, "email": "sgkt@test.com", "answers": [{"question_id": 1, "answer_text": "Sangeeth"}, {"question_id": 2, "answer_text": "55"}]}'


curl -X POST http://localhost:5000/create-form \
    -H "Content-Type: application/json" \
    -d '{"title": "SchoolData", "questions": [{"question_text": "What is your Full name?", "question_type": "text"}, {"question_text": "What is your DOB?", "question_type": "date"}]}'
