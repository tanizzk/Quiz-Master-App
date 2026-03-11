Quiz Master – Web Based Quiz Application

Author
Name : Tanishk S Nair
Roll Number : 23f3004469
email : 23f3004469@ds.study.iitm.ac.in
Institution : IIT Madras, BS in Data Science and Applications

Description
Quiz Master is a web-based quiz management system developed using Python and Flask. The application allows administrators to create and manage quizzes while users can register, attempt quizzes, and track their scores. The system provides an interactive interface for quiz participation and performance analysis.

The project follows a modular structure with controllers, models, templates, and static resources organized separately.

Technology Stack

Backend

Python

Flask

Frontend

HTML

CSS

JavaScript

Database

SQLite

Database Schema

User

Stores registered user accounts.

Attributes:

id

email

full_name

qualification

dob

password_hash

is_admin

Subject

Represents a category of quizzes.

Attributes:

id

name

description

Chapter

Chapters belong to subjects and group quizzes by topic.

Attributes:

id

subject_id

name

description

Quiz

A quiz associated with a chapter.

Attributes:

id

chapter_id

title

date_of_quiz

duration_minutes

remarks
Question

Questions belonging to a particular quiz.

Attributes:

id

quiz_id

statement

option_a

option_b

option_c

option_d

correct_option

Score

Stores results of quiz attempts by users.

Attributes:

id

quiz_id

user_id

total_scored

max_score

timestamp


Features
Admin Features

Admin login authentication

Create and manage subjects

Create and manage chapters

Add and edit quizzes

Add questions to quizzes

View user performance

User Features

User registration and login

Browse subjects and chapters

Attempt quizzes

View quiz scores



Installation and Setup
1. Clone or download the project
git clone <https://github.com/tanizzk/Quiz-Master-App>
cd quiz_master
2. Create virtual environment
python -m venv .venv
3. Activate virtual environment

Mac/Linux

source .venv/bin/activate

Windows

.venv\Scripts\activate
4. Install dependencies
pip install -r requirements.txt
5. Run the application
flask run

The application will run on:

http://127.0.0.1:5000

Video Demo