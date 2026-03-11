from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    IntegerField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.fields import EmailField
from wtforms.validators import (
    DataRequired,
    EqualTo,
    Length,
    NumberRange,
    Optional,
    ValidationError,
)

from email_validator import EmailNotValidError, validate_email


def flexible_email(form, field):
    if not field.data:
        raise ValidationError("Email is required.")
    try:
        validate_email(field.data, check_deliverability=False)
    except EmailNotValidError as exc:
        domain = field.data.split("@")[-1] if "@" in field.data else ""
        if domain.endswith(".local"):
            return
        raise ValidationError(str(exc))

class RegistrationForm(FlaskForm):
    email = EmailField("Email", validators=[flexible_email])
    full_name = StringField("Full Name", validators=[DataRequired(), Length(max=120)])
    qualification = StringField("Qualification", validators=[Optional(), Length(max=120)])
    dob = DateField("Date of Birth", validators=[Optional()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match")],
    )
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[flexible_email])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")

class SubjectForm(FlaskForm):
    name = StringField("Subject Name", validators=[DataRequired(), Length(max=140)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=1000)])
    submit = SubmitField("Save Subject")

class ChapterForm(FlaskForm):
    subject_id = SelectField("Subject", coerce=int, validators=[DataRequired()])
    name = StringField("Chapter Name", validators=[DataRequired(), Length(max=140)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=1000)])
    submit = SubmitField("Save Chapter")

class QuizForm(FlaskForm):
    chapter_id = SelectField("Chapter", coerce=int, validators=[DataRequired()])
    title = StringField("Quiz Title", validators=[DataRequired(), Length(max=140)])
    date_of_quiz = DateField("Date of Quiz", validators=[Optional()])
    duration_minutes = IntegerField(
        "Duration (minutes)", validators=[Optional(), NumberRange(min=1, max=300)]
    )
    remarks = TextAreaField("Remarks", validators=[Optional(), Length(max=500)])
    submit = SubmitField("Save Quiz")

class QuestionForm(FlaskForm):
    statement = TextAreaField("Question", validators=[DataRequired()])
    option_a = StringField("Option A", validators=[DataRequired(), Length(max=255)])
    option_b = StringField("Option B", validators=[DataRequired(), Length(max=255)])
    option_c = StringField("Option C", validators=[Optional(), Length(max=255)])
    option_d = StringField("Option D", validators=[Optional(), Length(max=255)])
    correct_option = SelectField(
        "Correct Option",
        choices=[("a", "Option A"), ("b", "Option B"), ("c", "Option C"), ("d", "Option D")],
        validators=[DataRequired()],
    )
    submit = SubmitField("Add Question")
