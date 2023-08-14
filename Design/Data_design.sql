CREATE TABLE "Form" (
  "id" serial PRIMARY KEY,
  "title" varchar,
  "created_at" timestamp DEFAULT current_timestamp
);

CREATE TABLE "Question" (
  "id" serial PRIMARY KEY,
  "form_id" int REFERENCES "Form" ("id"),
  "question_text" varchar,
  "question_type" varchar
);

CREATE TABLE "Response" (
  "id" serial PRIMARY KEY,
  "form_id" int REFERENCES "Form" ("id"),
  "email" varchar,
  "phone" varchar,
  "submitted_at" timestamp DEFAULT current_timestamp
);

CREATE TABLE "Answer" (
  "id" serial PRIMARY KEY,
  "response_id" int REFERENCES "Response" ("id"),
  "question_id" int REFERENCES "Question" ("id"),
  "answer_text" varchar,
  "updated_at" timestamp DEFAULT current_timestamp
);
