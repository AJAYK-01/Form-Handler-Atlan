CREATE TABLE "Form" (
  "id" int PRIMARY KEY AUTO_INCREMENT,
  "title" varchar,
  "created_at" timestamp default current_timestamp
);

CREATE TABLE "Question" (
  "id" int PRIMARY KEY AUTO_INCREMENT,
  "form_id" int,
  "question_text" varchar,
  "question_type" varchar
);

CREATE TABLE "Response" (
  "id" int PRIMARY KEY AUTO_INCREMENT,
  "form_id" int,
  "email" varchar,
  "submitted_at" timestamp
);

CREATE TABLE "Answer" (
  "id" int PRIMARY KEY AUTO_INCREMENT,
  "response_id" int,
  "question_id" int,
  "answer_text" varchar,
  "updated_at" timestamp
);

ALTER TABLE "Question" ADD FOREIGN KEY ("form_id") REFERENCES "Form" ("id");

ALTER TABLE "Response" ADD FOREIGN KEY ("form_id") REFERENCES "Form" ("id");

ALTER TABLE "Answer" ADD FOREIGN KEY ("response_id") REFERENCES "Response" ("id");

ALTER TABLE "Answer" ADD FOREIGN KEY ("question_id") REFERENCES "Question" ("id");
