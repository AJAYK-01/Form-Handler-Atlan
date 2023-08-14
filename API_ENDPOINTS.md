# API Gateway

The API Gateway is a microservice that acts as an entry point for all requests from the client. It forwards requests to the appropriate service and returns the response back to the client.

## Endpoints

The API Gateway exposes the following endpoints:

### `/create-form` (POST)

This endpoint forwards form creation data to the database handler.

**Example Request:**

- Endpoint: `POST http://localhost:5000/create-form`
- Request Body:
```json
{
  "title": "Personal Information",
  "questions": [
    {
      "question_text": "What is your name?",
      "question_type": "short_text"
    },
    {
      "question_text": "Where is your city?",
      "question_type": "short_text"
    },
    {
      "question_text": "Describe your city in 200 words?",
      "question_type": "long_text"
    },
    {
      "question_text": "What is your employment?",
      "question_type": "short_text"
    }
  ]
}
```
**Response:**
```json
{
  "message": "Form created successfully"
}
```

### `/get-form` (GET)

This endpoint fetches a form with a given form ID.

**Example Request:**

- Endpoint: `GET http://localhost:5000/get-form?form_id=2`
**Response:**
```json
{
  "form": {
    "created_at": "2023-08-14T10:46:20.507791",
    "id": 2,
    "questions": [
      {
        "id": 6,
        "question_text": "What is your name?",
        "question_type": "short_text"
      },
      {
        "id": 7,
        "question_text": "Where is your city?",
        "question_type": "short_text"
      },
      {
        "id": 8,
        "question_text": "Describe your city in 200 words?",
        "question_type": "long_text"
      },
      {
        "id": 9,
        "question_text": "What is your employment?",
        "question_type": "short_text"
      }
    ],
    "title": "Personal Information"
  }
}
```

### `/submit-form` (POST)

This endpoint forwards form submission data to the database handler. <br/> <br/>
It also sends a request to sms alert service to try sending an alert to user who submitted response based on "phone" parameter

**Example Request:**

- Endpoint: `POST http://localhost:5000/submit-form`
- Request Body:
```json
{
  "form_id": 2,
  "email": "jane@example.com",
  "phone": "+919876543210",
  "answers": [
    {
      "question_id": 6,
      "answer_text": "Jane"
    },
    {
      "question_id": 7,
      "answer_text": "Chennai"
    },
    {
      "question_id": 8,
      "answer_text": "Chennai is a city of contrasts. It is a city where you can find the most expensive houses in the world and also the largest slums. Chennai is a city of vada pav and cutting chai, of Bollywood and street food, of local trains and traffic jams. Chennai is a city of jugaad, masti, and dhinchak. Chennai is also known for its slang words such as ‘salna’ (as in curry), ‘bandha’ (brag), ‘Annaathe’ (elder brother), ‘Bejaar’ (boring), ‘Dabbu’ (money), ‘Galiju’ (dirty), etc. These slang words have become mainstream in daily conversations and add to the charm of the city."
    },
    {
      "question_id": 9,
      "answer_text": "Teacher"
    }
  ]
}
```
**Response:**
```json
{
  "message": "Response submit successfully and sms sent"
}
```

### `/validate-response` (POST)

This endpoint forwards form validation sql query to the database handler. Depending on criteria of user, frontend can create and send custom sql queries.

**Example Request:**
- Endpoint: `POST http://localhost:5000/validate-response`
- Request Body:
```json
{
  "form_id": 2,
  "validation_query": "SELECT * FROM response WHERE form_id = 2 AND email NOT LIKE '%@example.com'"
}
```
**Response:**
```json
{
  "valid": true
}
```
**Example Request:**
```json
{
  "form_id": 2,
  "validation_query": "SELECT * FROM response WHERE form_id = 2 AND email LIKE '%@example.com'"
}
```
**Response:**
```json
{
  "errors": [
    "Validation failed for form 2"
  ],
  "valid": false
}
```

### `/sheets-export` (POST)

This endpoint forwards form export data to the Google Sheets handler.

**Example Request :**

- Endpoint: `POST http://localhost:5000/sheets-export/`
- Request Body:
```json
{
  "form_id": 1,
  "email": "jane@example.com"
}
```
**Response:**
```json
{
  "message": "Spreadsheet created & shared with jane@example.com, link: https://docs.google.com/spreadsheets/d/15BmwWLadLbcyN3asdasfjwqrbkjbkaf1p2NX5U8XkZQ8ENorS8"
}
```

### `/sheets-export-all` (POST)

This endpoint forwards all forms export data to the Google Sheets handler.

**Example Request:**

- Endpoint: `POST http://localhost:5000/sheets-export-all/`
- Request Body:
```json
{
  "email": "jane@example.com"
}
```
**Response:**
```json
{
  "message": "Spreadsheet created & shared with jane@example.com, link: https://docs.google.com/spreadsheets/d/1DXSNxncbjkajkfbakL-BAwLLafC2Pok_xkka2VAwYSo54I"
}
```

### `/search-slangs` (POST)

This endpoint forwards slang search data to the database handler.<br/> <br/>
Compares response with a set of slang words stored in slang_words.txt, which can be replaced by an api or a database of slang words.


**Example Request:**

- Endpoint: `POST http://localhost:5000/search-slangs`
- Request Body:
```json
{
  "form_id": 2,
  "text_question_id": 8,
  "city_question_id": 7,
  "city": "Mumbai"
}
```
**Response:**
```json
{
  "slangs": [
    "dhinchak",
    "jugaad"
  ]
}
```