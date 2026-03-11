from datetime import datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

from config import Config

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(120))
    qualification = db.Column(db.String(120))
    dob = db.Column(db.Date)
    is_admin = db.Column(db.Boolean, default=False)
    scores = db.relationship("Score", backref="user", lazy=True)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def password(self):
        raise AttributeError("Password is write-only")

    @password.setter
    def password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    @classmethod
    def ensure_admin(cls):
        if not Config.ADMIN_EMAIL or not Config.ADMIN_PASSWORD:
            return
        admin = cls.query.filter_by(email=Config.ADMIN_EMAIL, is_admin=True).first()
        if admin:
            return
        admin = cls(
            email=Config.ADMIN_EMAIL,
            full_name="Quiz Master",
            is_admin=True,
        )
        admin.password = Config.ADMIN_PASSWORD
        db.session.add(admin)
        db.session.commit()

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140), nullable=False)
    description = db.Column(db.Text)
    chapters = db.relationship("Chapter", backref="subject", lazy=True)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "description": self.description}

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=False)
    name = db.Column(db.String(140), nullable=False)
    description = db.Column(db.Text)
    quizzes = db.relationship("Quiz", backref="chapter", lazy=True)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey("chapter.id"), nullable=False)
    title = db.Column(db.String(140), nullable=False)
    date_of_quiz = db.Column(db.Date)
    duration_minutes = db.Column(db.Integer)
    remarks = db.Column(db.Text)
    questions = db.relationship("Question", backref="quiz", lazy=True)
    scores = db.relationship("Score", backref="quiz", lazy=True)

    def duration_str(self):
        hours, minutes = divmod(self.duration_minutes or 0, 60)
        return f"{hours:02d}:{minutes:02d}"

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id"), nullable=False)
    statement = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255))
    option_d = db.Column(db.String(255))
    correct_option = db.Column(db.String(1), nullable=False)

    def option_label(self, key):
        return getattr(self, f"option_{key}", "")

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    total_scored = db.Column(db.Integer)
    max_score = db.Column(db.Integer)

    def to_dict(self):
        return {
            "id": self.id,
            "quiz": self.quiz.title,
            "score": self.total_scored,
            "max_score": self.max_score,
            "timestamp": self.timestamp.isoformat(),
        }

class ConfiguredDatabase:
    @staticmethod
    def init_app(app):
        db.init_app(app)

    @staticmethod
    def create_all():
        db.create_all()
