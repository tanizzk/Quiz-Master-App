Quiz Master – Web Based Quiz Application
Author

Name: Tanishk S Nair
Roll Number: 23f3004469
Email: 23f3004469@ds.study.iitm.ac.in

Program: BS in Data Science and Applications
Institution: IIT Madras

Project Description

Quiz Master is a web-based quiz management system built using Python and Flask.

The application allows:

Administrators to create and manage subjects, chapters, quizzes, and questions.

Users to register, attempt quizzes, and track their scores.

The platform provides an interactive interface for quiz participation and performance analysis.

The project follows a modular web application structure with controllers, models, templates, and static resources organized separately.

Technology Stack
Backend

Python

Flask

Frontend

HTML

CSS

JavaScript

JavaScript is also used for:

Dark mode toggle

Interactive UI components

Chart visualization for score history

Database

SQLite

Database Schema

The application uses a relational database consisting of the following entities.

User

Stores registered user accounts.

Attributes

id

email

full_name

qualification

dob

password_hash

is_admin

Subject

Represents a category of quizzes.

Attributes

id

name

description

Chapter

Chapters belong to subjects and group quizzes by topic.

Attributes

id

subject_id

name

description

Quiz

A quiz associated with a chapter.

Attributes

id

chapter_id

title

date_of_quiz

duration_minutes

remarks

Question

Questions belonging to a particular quiz.

Attributes

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

Attributes

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

View user performance and quiz attempts

User Features

User registration and login

Browse subjects and chapters

Attempt quizzes

View quiz scores

View score history with charts

Installation and Setup
1 Clone the Repository
git clone https://github.com/tanizzk/Quiz-Master-App
cd Quiz-Master-App
2 Create Virtual Environment
python -m venv .venv
3 Activate Virtual Environment
Mac / Linux
source .venv/bin/activate
Windows
.venv\Scripts\activate
4 Install Dependencies
pip install -r requirements.txt
5 Run the Application
flask run

The application will run at:

http://127.0.0.1:5000
Project Structure
quiz_master/
│
├── app.py
├── models.py
├── controllers/
│
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── login.html
│   └── register.html
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── database.db
├── requirements.txt
└── README.md
Video Demo

(Add your demo video link here)

Example:

https://drive.google.com/your-demo-video-link
