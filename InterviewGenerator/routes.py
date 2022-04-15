from flask import Blueprint
from flask import Flask, g, request, render_template, flash, redirect, url_for,session, logging, send_file, jsonify, make_response
from flask_login import login_required, logout_user, current_user, login_user
from functools import wraps
import jwt
import datetime

from forms import QuestionsCreateForm, QuestionSetCreateForm, LoginForm, AddUserForm, SignupForm
from models import db, Question, QuestionSet, QuestionsSets, User, Interview, QuestionMark
helper = Blueprint('helper', __name__)

SECRET_KEY = b'murmurmur'


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if request.args.get('token'):
            token = request.args.get('token')

        if not token:
            return jsonify({'message': 'a valid token is missing'})
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except:
            return jsonify({'message': 'token is invalid'})

        return f(token, *args, **kwargs)

    return decorator


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_admin == False:
            flash("You are not allowed to view this page since you're not admin")
            return redirect(url_for('helper.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


def recruiter_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if (current_user.is_recruiter == False) and (current_user.is_admin == False):
            flash("You are not allowed to view this page since you're not recruiter")
            return redirect(url_for('helper.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


def expert_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if (current_user.is_expert == False) and (current_user.is_admin == False):
            flash("You are not allowed to view this page since you're not expert")
            return redirect(url_for('helper.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


@helper.route('/')
@helper.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@helper.route('/questions/all', methods=['GET', 'POST'])
@login_required
def show_questions():
    questions = Question.query.all()
    sets = QuestionSet.query.all()
    sets_themes = dict()
    for s in QuestionSet.query.all():
        set_q = s.questions
        themes = []
        for q in set_q:
            themes.append(q.theme)
        themes = list(set(themes))
        sets_themes[str(s.id)] = themes
    return render_template('all_questions.html', questions=questions, sets=sets, sets_themes=sets_themes)


@helper.route('/questions/all/full', methods=['GET', 'POST'])
@login_required
def show_questions_full():
    themes = []
    for theme in Question.query.with_entities(Question.theme).distinct().all():
        themes.extend(theme)
    if request.method == 'POST':
        selected_theme = request.form['theme']
        selected_mark = request.form['mark']

        if selected_theme and selected_mark:
            questions = Question.query.with_entities(Question.id).filter(Question.theme == selected_theme, Question.mark == selected_mark).all()
            return jsonify({'redirect': url_for('helper.show_questions_full', themes=themes, questions=questions, selected_theme=selected_theme, selected_mark=selected_mark)})
        elif selected_theme:
            questions = Question.query.with_entities(Question.id).filter(Question.theme == selected_theme).all()
            return jsonify({'redirect': url_for('helper.show_questions_full', themes=themes, questions=questions,
                                    selected_theme=selected_theme)})
        elif selected_mark:
            questions = Question.query.with_entities(Question.id).filter(Question.mark == selected_mark).all()
            return jsonify({'redirect': url_for('helper.show_questions_full', themes=themes, questions=questions,
                                                selected_mark=selected_mark)})
    data = request.args
    if data:
        selected_theme = request.args.getlist('selected_theme')
        selected_mark = request.args.getlist('selected_mark')
        questions = request.args.getlist('questions')
        ids = [s.replace('(', '').replace(')', '').replace(',', '') for s in questions]
        themes = request.args.getlist('themes')
        questions = Question.query.filter(Question.id.in_(ids)).all()
        if selected_theme and selected_mark:
            selected_theme = selected_theme[0]
            selected_mark = selected_mark[0]
            return render_template('all_questions_full.html', themes=themes, questions=questions, selected_theme=selected_theme, selected_mark=selected_mark)
        elif selected_theme:
            selected_theme = selected_theme[0]
            return render_template('all_questions_full.html', themes=themes, questions=questions,
                                   selected_theme=selected_theme)
        elif selected_mark:
            selected_mark = selected_mark[0]
            return render_template('all_questions_full.html', themes=themes, questions=questions,
                                   selected_mark=selected_mark)
    questions = Question.query.all()
    return render_template('all_questions_full.html', themes=themes, questions=questions)


@helper.route('/create_question', methods=['GET', 'POST'])
@login_required
@expert_required
def create_question():
    form = QuestionsCreateForm(request.form)
    if request.method == 'POST':
        if form.validate():
            theme = form.theme.data
            essence = form.essence.data
            answer = form.answer.data
            mark = form.mark.data
            question = Question(theme, essence, answer, mark)
            db.session.add(question)
            db.session.commit()
            return redirect('/questions/all/full')
    return render_template('create_question.html', form=form)


@helper.route('/questions/all/<int:id>/update', methods=['GET', 'POST'])
@login_required
@expert_required
def update_question(id):
    form = QuestionsCreateForm(request.form)
    question = Question.query.filter_by(id=id).first()
    if request.method == 'POST':
        if form.validate():
            theme = form.theme.data
            essence = form.essence.data
            answer = form.answer.data
            mark = form.mark.data
            question = Question.query.filter_by(id=id).first()
            question.theme = theme
            question.essence = essence
            question.answer = answer
            old_mark = question.mark
            question.mark = mark

            scores_w_q = QuestionMark.query.filter_by(question_id=question.id).all()
            for s in scores_w_q:
                i = Interview.query.filter_by(id=s.interview_id).first()
                if i.max_score:
                    i.max_score = i.max_score - old_mark + mark
                    obj_s = s
                    obj_mark = s.mark
                    obj_s.mark = round((s.mark*mark)/old_mark)
                    i.score = i.score - obj_mark + obj_s.mark
                    db.session.commit()
            db.session.commit()
            return redirect('/questions/all/full')
    return render_template('update_question.html', form=form, question=question)


@helper.route('/questions/all/<int:id>/delete', methods=['GET', 'POST'])
@login_required
@expert_required
def delete_question(id):
    question = Question.query.filter_by(id=id).first()
    if request.method == 'POST':
        if question:
            delete_m = QuestionMark.__table__.delete().where(QuestionMark.question_id == id)
            db.session.execute(delete_m)
            db.session.commit()
            db.session.delete(question)
            db.session.commit()
            flash('Delete was successfull')
            return redirect('/questions/all/full')
        flash('Unable to delete')

    return render_template('delete.html')


@helper.route('/sets/all/full', methods=['GET', 'POST'])
@login_required
def show_sets_full():
    levels = []
    for level in QuestionSet.query.with_entities(QuestionSet.level).distinct().all():
        levels.extend(level)

    selected_level = request.args.get('level')

    if selected_level:
        sets = QuestionSet.query.filter(QuestionSet.level == selected_level).all()
        return render_template('all_sets_full.html', levels=levels, sets=sets, selected_level=selected_level)
    else:
        selected_level = request.args.get('selected_level', None, type=str)
        if selected_level:
            sets = QuestionSet.query.filter(QuestionSet.level == selected_level).all()
            return render_template('all_sets_full.html', levels=levels, sets=sets,
                                   selected_level=selected_level)
    sets = QuestionSet.query.all()

    return render_template('all_sets_full.html', levels=levels, sets=sets)


@helper.route('/create_question_set')
@login_required
def create_set():
    form = QuestionSetCreateForm(request.form)
    form.questions.query = db.session.query(Question).order_by(Question.essence)
    questions = Question.query.all()
    return render_template('create_set.html', form=form, questions=questions)


@helper.route("/add_set", methods=["GET", "POST"])
@login_required
@expert_required
def add_set():
    if request.method == 'POST':
        name = request.form['name']
        level = request.form['level']
        questions_id = request.form['hidden_questions']
        questions_id = list(questions_id.split(","))
        questions = [Question.query.filter_by(id=ex_id).first() for ex_id in questions_id]
        set = QuestionSet(name=name, questions=questions, level=level)
        db.session.add(set)
        db.session.commit()
        msg = 'New record created successfully'
    return jsonify("OK")


@helper.route('/sets/all/<int:id>/update', methods=['GET', 'POST'])
@login_required
@expert_required
def update_set(id):
    form = QuestionSetCreateForm(request.form)
    form.questions.query = db.session.query(Question).order_by(Question.essence)
    set = QuestionSet.query.filter_by(id=id).first()
    questions_id = []
    for q in set.questions:
        questions_id.append(q.id)
    return render_template('set_update.html', form=form, set=set, questions_id=questions_id)


@helper.route("/update_set/<int:id>", methods=["GET", "POST"])
@login_required
@expert_required
def update_set_post(id):
    if request.method == 'POST':
        name = request.form['name']
        level = request.form['level']
        questions_id = request.form['hidden_questions']
        questions_id = list(questions_id.split(","))
        questions = [Question.query.filter_by(id=ex_id).first() for ex_id in questions_id]
        set = QuestionSet.query.filter_by(id=id).first()
        set.name = name
        set.level = level
        set.questions = questions
        db.session.commit()
    return jsonify("OK")


@helper.route('/sets/all/<int:id>/delete', methods=['GET', 'POST'])
@login_required
@expert_required
def delete_set(id):
    set = QuestionSet.query.filter_by(id=id).first()
    if request.method == 'POST':
        if set:
            db.session.delete(set)
            db.session.commit()
            flash('Delete was successfull')
            return redirect('/sets/all/full')
        flash('Unable to delete')

    return render_template('delete_set.html')


@helper.route('/create_interview')
@login_required
@recruiter_required
def create_interview():
    experts = User.query.filter_by(is_expert=True).all()
    return render_template('create_interview.html', experts=experts)


@helper.route("/add_interview", methods=["POST","GET"])
@login_required
@recruiter_required
def add_interview():
    if request.method == 'POST':
        assignee = request.form['assignee']
        position = request.form['position']
        experts_id = request.form['hidden_experts']
        experts_id = list(experts_id.split(","))
        experts = [User.query.filter_by(id=ex_id).first() for ex_id in experts_id]
        interview = Interview(assignee=assignee, position=position, experts=experts)
        interview.recruiter_id = current_user.id
        db.session.add(interview)
        db.session.commit()
        msg = 'New record created successfully'
    return jsonify("OK")


@helper.route("/interviews/<int:id>/add_questions", methods=["POST","GET"])
@login_required
@expert_required
def interview_add_questions(id):
    sets = QuestionSet.query.all()
    questions = Question.query.all()
    interview = Interview.query.filter_by(id=id).first()
    questions_id = []
    for q in interview.questions:
        questions_id.append(q.id)
    sets_id = []
    for s in interview.sets:
        sets_id.append(s.id)
    return render_template('add_to_interview.html', sets=sets, questions=questions, questions_id=questions_id, sets_id=sets_id, interview=interview)


@helper.route("/ajax_interview_add_questions/<int:id>", methods=["POST","GET"])
@login_required
@expert_required
def ajax_add_to_interview(id):
    if request.method == 'POST':
        interview = Interview.query.filter_by(id=id).first()
        sets_id = request.form['hidden_sets']
        if len(sets_id) > 0:
            sets_id = list(sets_id.split(","))
            sets = [QuestionSet.query.filter_by(id=ex_id).first() for ex_id in sets_id]
            interview.sets = sets
        questions_id = request.form['hidden_questions']
        if len(questions_id) > 0:
            questions_id = list(questions_id.split(","))
            questions = [Question.query.filter_by(id=ex_id).first() for ex_id in questions_id]
            interview.questions = questions
        db.session.commit()
        msg = 'New record created successfully'
    return jsonify("OK")


@helper.route('/interviews')
@login_required
def interviews_view():
    if current_user.is_admin or current_user.is_recruiter:
        interviews = Interview.query.all()
    elif current_user.is_expert:
        interviews = Interview.query.filter(Interview.experts.contains(current_user)).filter_by(is_conducted=False).all()
    return render_template('interviews.html', interviews=interviews)


@helper.route('/interviews/archive')
@login_required
def interviews_archive_view():
    interviews = Interview.query.filter(Interview.experts.contains(current_user)).filter_by(is_conducted=True).all()
    return render_template('archive.html', interviews=interviews)


@helper.route('/interviews/<int:id>')
@login_required
def interview_detail(id):
    interview = Interview.query.filter_by(id=id).first()
    return render_template('interview_detail.html', interview=interview)


@helper.route('/interviews/<int:id>/change_status')
@login_required
@recruiter_required
def interview_change_status(id):
    interview = Interview.query.filter_by(id=id).first()
    if interview.is_conducted:
        interview.is_conducted = False
    else:
        interview.is_conducted = True
    db.session.commit()
    return redirect('/interviews')


@helper.route('/interviews/score/<id>')
@login_required
@expert_required
def interview_score(id):
    interview = Interview.query.filter_by(id=id).first()
    questions =[]
    for s in interview.sets:
        q = s.questions
        questions.extend(q)
    questions.extend(interview.questions)
    questions = list(set(questions))
    questions.sort(key=lambda x: (x.mark, x.essence), reverse=False)
    scores = dict()
    for q in questions:
        s = QuestionMark.query.filter_by(question_id=q.id, expert_id=current_user.id, interview_id=interview.id).first()
        if s:
            scores[str(int(q.id))] = s.mark
    return render_template('interview_score.html', interview=interview, questions=questions, scores=scores)


@helper.route('/interview/score/data', methods=['GET', 'POST'])
@login_required
@expert_required
def interview_score_data():
    if request.method == "POST":
        data = request.form
        if data:
            dot = data['dotid'].split('_')
            question_id = dot[1]
            question = Question.query.filter_by(id=question_id).first()
            interview = Interview.query.filter_by(id=data['interview_id']).first()
            mark = QuestionMark.query.filter_by(question_id=question_id, interview_id=interview.id, expert_id=current_user.id).first()
            if mark:
                interview.score = int(data['mark']) + int(interview.score) - int(mark.mark)
                mark.mark = int(data['mark'])
            else:
                question_mark = QuestionMark(question_id=question_id, interview_id=interview.id, expert_id=current_user.id, mark=data['mark'])
                if interview.max_score:
                    interview.score = int(interview.score) + int(question_mark.mark)
                else:
                    interview.score = int(question_mark.mark)
                if interview.max_score:
                    interview.max_score = int(interview.max_score) + int(question.mark)
                else:
                    interview.max_score = int(question.mark)
                db.session.add(question_mark)
            db.session.commit()
            return jsonify('Score: ' + str(interview.score) + " / " + str(interview.max_score))


@helper.route('/results', methods=['GET', 'POST'])
@login_required
def results():
    interviews = Interview.query.filter_by(is_conducted=True).all()
    return render_template('results.html', interviews=interviews)


@helper.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('helper.dashboard'))

    form = LoginForm(request.form)
    if form.validate():
        user = User.query.filter_by(email=form.email.data).first()
        try:
            if user and user.check_password(password=form.password.data):
                if user.is_active:
                    login_user(user)
                    next_page = request.args.get('next')
                    return redirect(next_page or url_for('helper.dashboard'))
                flash('User is not active')
            else:
                flash('Invalid username/password combination')
            return redirect(url_for('helper.login'))
        except:
            flash('Your authorization went wrong. Contact administrator.')
            return redirect(url_for('helper.login'))
    return render_template(
        'login.html',
        form=form,
    )


@helper.route('/add_user', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    form = AddUserForm(request.form)
    if form.validate():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user is None:
            user = User(
                name=form.name.data,
                surname=form.surname.data,
                email=form.email.data,
                is_admin=False,
                is_active=False
            )
            if form.role.data == 'recruiter':
                user.is_recruiter = True
            if form.role.data == 'expert':
                user.is_expert = True
            db.session.add(user)
            db.session.commit()
            token = jwt.encode(
                {'public_id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=10)},
                SECRET_KEY, "HS256")
            token_url = url_for('helper.signup', token=token, _external=True)
            html = render_template('register_email.html', token_url=token_url)
            subject = "InterviewGenerator invitation"
            from email_controller import send_email
            send_email(user.email, subject, html)
            return redirect(url_for('helper.dashboard'))
        flash('A user already exists with that email address.')
    return render_template(
        'create_user.html',
        form=form,
    )


@helper.route('/signup', methods=['GET', 'POST'])
@token_required
def signup(token):
    data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    form = SignupForm(request.form)
    user = User.query.filter_by(id=data['public_id']).first()
    if user.is_active:
        flash('A user with this email is already active with set password')
    else:
        if form.validate():
            user.set_password(form.password.data)
            user.is_active = True
            db.session.commit()
            login_user(user)
            return redirect(url_for('helper.dashboard'))
    return render_template(
        'signup.html',
        form=form,
        user=user,
        token=token
    )


@helper.route('/users', methods=['GET', 'POST'])
@login_required
@admin_required
def view_users():
    users = User.query.all()
    return render_template(
        'users_list.html',
        users=users
    )


@helper.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('helper.login'))


