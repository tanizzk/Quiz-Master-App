from functools import wraps

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)


from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)


from sqlalchemy.orm import joinedload

from config import Config
from forms import (
    ChapterForm,
    LoginForm,
    QuestionForm,
    QuizForm,
    RegistrationForm,
    SubjectForm,
)


from models import (
    Chapter,
    ConfiguredDatabase,
    Question,
    Score,
    Subject,
    Quiz,
    User,
    db,
)

from flask_wtf.csrf import CSRFError


login_manager = LoginManager()
login_manager.login_view = "login"

PRELOGIN_QUIZ = [
    {
        "statement": "Which database powers Quiz Master?",
        "options": ["SQLite", "PostgreSQL", "MongoDB", "MySQL"],
    },
    {
        "statement": "Admins can configure which of the following?",
        "options": ["Subjects", "Chapters", "Quizzes", "All of the above"],
    },
    {
        "statement": "What framework handles templating?",
        "options": ["Jinja2", "Blade", "EJS", "Thymeleaf"],
    },
    {
        "statement": "How are quiz scores stored?",
        "options": ["Scores table", "Logs file", "LocalStorage", "Session only"],
    },
    {
        "statement": "What happens when a user finishes a quiz?",
        "options": [
            "Score row is recorded",
            "Email is sent",
            "Quiz is deleted",
            "Nothing",
        ],
    },
]


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    ConfiguredDatabase.init_app(app)
    login_manager.init_app(app)
    with app.app_context():
        ConfiguredDatabase.create_all()
        User.ensure_admin()

    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    def admin_required(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            if not current_user.is_authenticated or not current_user.is_admin:
                flash("Quiz Master access is required.", "warning")
                return redirect(url_for("login"))
            return view(*args, **kwargs)

        return wrapped_view



    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        subjects = Subject.query.order_by(Subject.name).all()
        upcoming_quizzes = (
            Quiz.query.order_by(Quiz.date_of_quiz.asc(), Quiz.title)
            .limit(4)
            .all()
        )
        return render_template(
            "index.html",
            subjects=subjects,
            upcoming_quizzes=upcoming_quizzes,
            sample_quiz=PRELOGIN_QUIZ,
        )



    @app.route("/register", methods=["GET", "POST"])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for("index"))
        form = RegistrationForm()
        if form.validate_on_submit():
            existing = User.query.filter_by(email=form.email.data).first()
            if existing:
                flash("Email already registered.", "danger")
            else:
                user = User(
                    email=form.email.data.lower(),
                    full_name=form.full_name.data,
                    qualification=form.qualification.data,
                    dob=form.dob.data,
                    is_admin=False,
                )
                user.password = form.password.data
                db.session.add(user)
                db.session.commit()
                flash("Registration successful. Please log in.", "success")
                return redirect(url_for("login"))
        return render_template("register.html", form=form)



    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))

        form = LoginForm()

        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data.lower()).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                flash("Welcome back!", "success")
                return redirect(request.args.get("next") or url_for("dashboard"))
            else:
                flash("Invalid credentials.", "danger")
        else:
            if request.method == "POST":
                flash("Please ensure the email is valid and all fields are completed.", "warning")

        return render_template("login.html", form=form)



    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("You have been logged out.", "info")
        return redirect(url_for("login"))



    @app.route("/dashboard") 
    @login_required
    def dashboard():
        if current_user.is_admin:
            return redirect(url_for("admin_dashboard"))
        return redirect(url_for("user_dashboard"))




    @app.route("/user/dashboard")
    @login_required
    def user_dashboard():
        if current_user.is_admin:
            return redirect(url_for("admin_dashboard"))
        scores = (
            Score.query.options(joinedload(Score.quiz))
            .filter_by(user_id=current_user.id)
            .order_by(Score.timestamp.desc())
            .limit(12)
            .all()
        )
        history = [score.to_dict() for score in scores]
        chart_data = {
            "labels": [s["quiz"] for s in history[::-1]],
            "scores": [s["score"] for s in history[::-1]],
            "max": [s["max_score"] for s in history[::-1]],
        }
        available_quizzes = (
            Quiz.query.options(joinedload(Quiz.chapter).joinedload(Chapter.subject))
            .order_by(Quiz.date_of_quiz.asc())
            .limit(8)
            .all()
        )
        return render_template(
            "user/dashboard.html",
            history=history,
            chart_data=chart_data,
            available_quizzes=available_quizzes,
        )



    @app.route("/admin/dashboard")
    @admin_required
    def admin_dashboard():
        subject_count = Subject.query.count()
        chapter_count = Chapter.query.count()
        quiz_count = Quiz.query.count()
        user_count = User.query.filter_by(is_admin=False).count()
        recent_scores = (
            Score.query.options(
                joinedload(Score.quiz),
                joinedload(Score.user),
            )
            .order_by(Score.timestamp.desc())
            .limit(5)
            .all()
        )
        chart_data = {
            "labels": ["Subjects", "Chapters", "Quizzes", "Users"],
            "counts": [subject_count, chapter_count, quiz_count, user_count],
        }
        return render_template(
            "admin/dashboard.html",
            subject_count=subject_count,
            chapter_count=chapter_count,
            quiz_count=quiz_count,
            user_count=user_count,
            recent_scores=recent_scores,
            chart_data=chart_data,
        )



    @app.route("/admin/subjects", methods=["GET", "POST"])
    @admin_required
    def admin_subjects():
        form = SubjectForm()
        if form.validate_on_submit():
            subject = Subject(
                name=form.name.data,
                description=form.description.data,
            )
            db.session.add(subject)
            db.session.commit()
            flash("Subject saved.", "success")
            return redirect(url_for("admin_subjects"))
        search = request.args.get("q")
        query = Subject.query
        if search:
            query = query.filter(Subject.name.ilike(f"%{search}%"))
        subjects = query.order_by(Subject.name).all()
        return render_template("admin/subjects.html", form=form, subjects=subjects)




    @app.route("/admin/subjects/<int:subject_id>/edit", methods=["GET", "POST"])
    @admin_required
    def edit_subject(subject_id):
        subject = Subject.query.get_or_404(subject_id)
        form = SubjectForm(obj=subject)
        if form.validate_on_submit():
            subject.name = form.name.data
            subject.description = form.description.data
            db.session.commit()
            flash("Subject updated.", "success")
            return redirect(url_for("admin_subjects"))
        return render_template("admin/subject_form.html", form=form, subject=subject)



    @app.route("/admin/subjects/<int:subject_id>/delete", methods=["POST"])
    @admin_required
    def delete_subject(subject_id):
        subject = Subject.query.get_or_404(subject_id)
        db.session.delete(subject)
        db.session.commit()
        flash("Subject deleted.", "info")
        return redirect(url_for("admin_subjects"))




    @app.route("/admin/chapters", methods=["GET", "POST"])
    @admin_required
    def admin_chapters():
        form = ChapterForm()

        form.subject_id.choices = [
            (s.id, s.name) for s in Subject.query.order_by(Subject.name)
        ]

        if form.validate_on_submit():
            chapter = Chapter(
                subject_id=form.subject_id.data,
                name=form.name.data,
                description=form.description.data,
            )

            db.session.add(chapter)
            db.session.commit()

            flash("Chapter saved.", "success")
            return redirect(url_for("admin_chapters"))

        elif request.method == "POST":
            flash("Please select a subject and provide a chapter name.", "warning")

        chapters = (
            Chapter.query.options(joinedload(Chapter.subject))
            .order_by(Chapter.name)
            .all()
        )

        return render_template("admin/chapters.html", form=form, chapters=chapters)



    @app.route("/admin/chapters/<int:chapter_id>/edit", methods=["GET", "POST"])
    @admin_required
    def edit_chapter(chapter_id):
        chapter = Chapter.query.get_or_404(chapter_id)
        form = ChapterForm(obj=chapter)
        form.subject_id.choices = [
            (s.id, s.name) for s in Subject.query.order_by(Subject.name)
        ]
        if form.validate_on_submit():
            chapter.subject_id = form.subject_id.data
            chapter.name = form.name.data
            chapter.description = form.description.data
            db.session.commit()
            flash("Chapter updated.", "success")
            return redirect(url_for("admin_chapters"))
        return render_template("admin/chapter_form.html", form=form, chapter=chapter)



    @app.route("/admin/chapters/<int:chapter_id>/delete", methods=["POST"])
    @admin_required
    def delete_chapter(chapter_id):
        chapter = Chapter.query.get_or_404(chapter_id)
        db.session.delete(chapter)
        db.session.commit()
        flash("Chapter deleted.", "info")
        return redirect(url_for("admin_chapters"))



    @app.route("/admin/quizzes", methods=["GET", "POST"])
    @admin_required
    def admin_quizzes():
        form = QuizForm()
        form.chapter_id.choices = [
            (c.id, f"{c.subject.name} :: {c.name}")
            for c in Chapter.query.options(joinedload(Chapter.subject)).order_by(Chapter.name)
        ]
        if form.validate_on_submit():
            quiz = Quiz(
                chapter_id=form.chapter_id.data,
                title=form.title.data,
                date_of_quiz=form.date_of_quiz.data,
                duration_minutes=form.duration_minutes.data,
                remarks=form.remarks.data,
            )
            db.session.add(quiz)
            db.session.commit()
            flash("Quiz saved.", "success")
            return redirect(url_for("admin_quizzes"))
        quizzes = (
            Quiz.query.options(joinedload(Quiz.chapter).joinedload(Chapter.subject))
            .order_by(Quiz.date_of_quiz.desc(), Quiz.title)
            .all()
        )
        return render_template("admin/quizzes.html", form=form, quizzes=quizzes)



    @app.route("/admin/quizzes/<int:quiz_id>/edit", methods=["GET", "POST"])
    @admin_required
    def edit_quiz(quiz_id):
        quiz = Quiz.query.get_or_404(quiz_id)
        form = QuizForm(obj=quiz)
        form.chapter_id.choices = [
            (c.id, f"{c.subject.name} :: {c.name}")
            for c in Chapter.query.options(joinedload(Chapter.subject)).order_by(Chapter.name)
        ]
        if form.validate_on_submit():
            quiz.chapter_id = form.chapter_id.data
            quiz.title = form.title.data
            quiz.date_of_quiz = form.date_of_quiz.data
            quiz.duration_minutes = form.duration_minutes.data
            quiz.remarks = form.remarks.data
            db.session.commit()
            flash("Quiz updated.", "success")
            return redirect(url_for("admin_quizzes"))
        return render_template("admin/quiz_form.html", form=form, quiz=quiz)



    @app.route("/admin/quizzes/<int:quiz_id>/delete", methods=["POST"])
    @admin_required
    def delete_quiz(quiz_id):
        quiz = Quiz.query.get_or_404(quiz_id)
        db.session.delete(quiz)
        db.session.commit()
        flash("Quiz deleted.", "info")
        return redirect(url_for("admin_quizzes"))



    @app.route("/admin/quizzes/<int:quiz_id>/questions", methods=["GET", "POST"])
    @admin_required
    def manage_questions(quiz_id):
        quiz = Quiz.query.options(joinedload(Quiz.questions)).get_or_404(quiz_id)
        quiz.questions.sort(key=lambda question: question.id or 0)
        form = QuestionForm()
        if form.validate_on_submit():
            question = Question(
                quiz_id=quiz.id,
                statement=form.statement.data,
                option_a=form.option_a.data,
                option_b=form.option_b.data,
                option_c=form.option_c.data,
                option_d=form.option_d.data,
                correct_option=form.correct_option.data,
            )
            db.session.add(question)
            db.session.commit()
            flash("Question added.", "success")
            return redirect(url_for("manage_questions", quiz_id=quiz.id))
        return render_template("admin/questions.html", quiz=quiz, form=form)



    @app.route("/admin/questions/<int:question_id>/delete", methods=["POST"])
    @admin_required
    def delete_question(question_id):
        question = Question.query.get_or_404(question_id)
        quiz_id = question.quiz_id
        db.session.delete(question)
        db.session.commit()
        flash("Question removed.", "info")
        return redirect(url_for("manage_questions", quiz_id=quiz_id))



    @app.route("/subjects/<int:subject_id>/chapters")
    def subject_chapters(subject_id):
        subject = Subject.query.options(joinedload(Subject.chapters)).get_or_404(subject_id)
        subject.chapters.sort(key=lambda chapter: chapter.name or "")
        return render_template("subjects.html", subject=subject)



    @app.route("/chapters/<int:chapter_id>/quizzes")
    def chapter_quizzes(chapter_id):
        chapter = Chapter.query.options(joinedload(Chapter.quizzes)).get_or_404(chapter_id)
        chapter.quizzes.sort(key=lambda quiz: quiz.title or "")
        return render_template("chapter_quizzes.html", chapter=chapter)



    @app.route("/quiz/<int:quiz_id>", methods=["GET", "POST"])
    @login_required
    def take_quiz(quiz_id):
        quiz = Quiz.query.options(joinedload(Quiz.questions)).get_or_404(quiz_id)
        if request.method == "POST":
            answers = {}
            correct = 0
            for question in quiz.questions:
                selection = request.form.get(f"question_{question.id}")
                if selection == question.correct_option:
                    correct += 1
                answers[question.id] = selection
            score = Score(
                quiz_id=quiz.id,
                user_id=current_user.id,
                total_scored=correct,
                max_score=len(quiz.questions),
            )
            db.session.add(score)
            db.session.commit()
            flash(f"Quiz submitted: {correct}/{len(quiz.questions)}", "success")
            return redirect(url_for("user_dashboard"))
        return render_template("quiz.html", quiz=quiz)



    @app.route("/api/subjects")
    def api_subjects():
        subjects = [subject.to_dict() for subject in Subject.query.order_by(Subject.name)]
        return jsonify(subjects)


    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return f"CSRF Error: {e.description}", 403

    return app
if __name__ == "__main__":
    create_app().run(debug=True)
