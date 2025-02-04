# app/views.py
# -*- coding: utf-8 -*-
import os
from datetime import datetime
from flask import session
from flask import (
    Blueprint, request, redirect, url_for, flash, render_template, current_app, send_from_directory
)
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.utils import secure_filename
from app import db
from app.models import (
    Student, Teacher, Subject, Test, TestOption, TestAssignment, TestResult,
    Question, QuestionOption, QuestionResult
)

bp = Blueprint('main', __name__)

#################################
# Главная страница и авторизация
#################################

@bp.route('/')
def index():
    return render_template("index.html")

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_type = request.form.get('user_type')
        if user_type == 'student':
            student_id = request.form.get('student_id')
            if not student_id:
                flash('Введите номер студенческого билета')
                return redirect(url_for('main.login'))
            user = Student.query.filter_by(student_id=student_id).first()
        else:
            username = request.form.get('username')
            password = request.form.get('password')
            if not username or not password:
                flash('Введите логин и пароль')
                return redirect(url_for('main.login'))
            user = Teacher.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            flash('Вы успешно вошли!')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Неверные данные')
            return redirect(url_for('main.login'))
    return render_template("login.html")

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из системы")
    return redirect(url_for('main.login'))

@bp.route('/dashboard')
@login_required
def dashboard():
    if hasattr(current_user, 'username'):
        tests = Test.query.all()
        return render_template("dashboard.html", tests=tests)
    else:
        return render_template("dashboard.html")

#################################
# Функционал преподавателя
#################################

@bp.route('/teacher/create_test', methods=['GET', 'POST'])
@login_required
def create_test():
    if not hasattr(current_user, 'username'):
        flash("Только преподаватели могут создавать тесты.")
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        subject_id = request.form.get('subject_id')
        title = request.form.get('title')
        description = request.form.get('description')
        duration = request.form.get('duration')
        test_type = request.form.get('test_type')
        if not (subject_id and title and duration and test_type):
            flash("Заполните обязательные поля: предмет, название теста, продолжительность и режим теста.")
            return redirect(url_for('main.create_test'))
        try:
            duration = int(duration)
        except ValueError:
            flash("Продолжительность должна быть числом.")
            return redirect(url_for('main.create_test'))
        new_test = Test(
            subject_id=subject_id,
            title=title,
            description=description,
            duration=duration,
            test_type=test_type
        )
        db.session.add(new_test)
        db.session.commit()
        flash("Тест успешно создан!")
        return redirect(url_for('main.add_questions', test_id=new_test.id))
    subjects = Subject.query.all()
    return render_template("create_test.html", subjects=subjects)

@bp.route('/teacher/add_questions/<int:test_id>', methods=['GET', 'POST'])
@login_required
def add_questions(test_id):
    if not hasattr(current_user, 'username'):
        flash("Только преподаватели могут добавлять вопросы.")
        return redirect(url_for('main.index'))
    test = Test.query.get(test_id)
    if not test:
        flash("Тест не найден.")
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        question_text = request.form.get('question_text')
        uploaded_file = request.files.get('question_image')
        image_path = None
        if uploaded_file and uploaded_file.filename != "":
            filename = secure_filename(uploaded_file.filename)
            upload_folder = current_app.config.get('UPLOAD_FOLDER')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            image_path = os.path.join(upload_folder, filename)
            uploaded_file.save(image_path)
            image_path = filename
        if not question_text:
            flash("Введите текст вопроса.")
            return redirect(url_for('main.add_questions', test_id=test_id))
        new_question = Question(test_id=test_id, text=question_text, image_path=image_path)
        db.session.add(new_question)
        db.session.commit()
        options_text = request.form.get('options')
        correct_options = request.form.get('correct_options')
        if options_text:
            options = options_text.strip().split('\n')
            correct_indices = []
            if correct_options:
                try:
                    correct_indices = [int(x.strip()) for x in correct_options.split(',') if x.strip().isdigit()]
                except Exception:
                    flash("Неправильный формат правильных вариантов для вопроса.")
                    return redirect(url_for('main.add_questions', test_id=test_id))
            for idx, opt in enumerate(options, start=1):
                opt = opt.strip()
                if opt:
                    is_correct = idx in correct_indices
                    q_option = QuestionOption(question_id=new_question.id, option_text=opt, is_correct=is_correct)
                    db.session.add(q_option)
            db.session.commit()
        flash("Вопрос добавлен!")
        return redirect(url_for('main.add_questions', test_id=test_id))
    questions = test.questions
    return render_template("add_questions.html", test=test, questions=questions)

@bp.route('/teacher/assign_test', methods=['GET', 'POST'])
@login_required
def assign_test():
    if not hasattr(current_user, 'username'):
        flash("Только преподаватели могут назначать тесты.")
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        test_id = request.form.get('test_id')
        student_id = request.form.get('student_id')
        if not (test_id and student_id):
            flash("Выберите тест и студента.")
            return redirect(url_for('main.assign_test'))
        existing = TestAssignment.query.filter_by(test_id=test_id, student_id=student_id).first()
        if existing:
            flash("Этот тест уже назначен данному студенту.")
            return redirect(url_for('main.assign_test'))
        assignment = TestAssignment(test_id=test_id, student_id=student_id, status='not_taken')
        db.session.add(assignment)
        db.session.commit()
        flash("Тест успешно назначен!")
        return redirect(url_for('main.dashboard'))
    tests = Test.query.all()
    students = Student.query.all()
    return render_template("assign_test.html", tests=tests, students=students)


@bp.route('/teacher/test_results')
@login_required
def test_results():
    if not hasattr(current_user, 'username'):
        flash("Доступ разрешён только для преподавателей.")
        return redirect(url_for('main.index'))
    test_results = TestResult.query.all()
    multi_results_query = db.session.query(
        Question.test_id,
        Test.title.label("test_title"),
        QuestionResult.student_id,
        Student.full_name.label("student_name"),
        db.func.min(QuestionResult.grade).label("overall_grade"),
        db.func.group_concat(QuestionResult.comments, '; ').label("overall_comment")
    ).join(Question, Question.id == QuestionResult.question_id
           ).join(Test, Test.id == Question.test_id
                  ).join(Student, Student.id == QuestionResult.student_id
                         ).group_by(Question.test_id, QuestionResult.student_id).all()

    multi_results = []
    for r in multi_results_query:
        multi_results.append({
            'test_id': r.test_id,
            'test_title': r.test_title,
            'student_id': r.student_id,
            'student_name': r.student_name,
            'overall_grade': r.overall_grade,
            'overall_comment': r.overall_comment
        })

    return render_template("test_results.html", test_results=test_results, multi_results=multi_results)


@bp.route('/teacher/grade_result/<int:result_id>', methods=['GET', 'POST'])
@login_required
def grade_result(result_id):
    if not hasattr(current_user, 'username'):
        flash("Доступ разрешён только для преподавателей.")
        return redirect(url_for('main.index'))
    result = TestResult.query.get(result_id)
    if not result:
        flash("Результат не найден.")
        return redirect(url_for('main.test_results'))
    if request.method == 'POST':
        new_grade = request.form.get('grade')
        comment = request.form.get('comment')
        try:
            new_grade = int(new_grade)
        except ValueError:
            flash("Оценка должна быть числом.")
            return redirect(url_for('main.grade_result', result_id=result_id))
        result.grade = new_grade
        result.comments = comment
        db.session.commit()
        flash("Оценка и комментарий сохранены.")
        return redirect(url_for('main.test_results'))
    return render_template("grade_result.html", result=result)

#################################
# Функционал студента
#################################

@bp.route('/student/tests')
@login_required
def student_tests():
    if not hasattr(current_user, 'student_id'):
        flash("Доступ разрешён только для студентов.")
        return redirect(url_for('main.index'))
    assignments = TestAssignment.query.filter_by(student_id=current_user.id).all()
    return render_template("student_tests.html", assignments=assignments)

# Маршрут для прохождения теста в старом режиме (один вопрос)
@bp.route('/student/take_test/<int:test_id>', methods=['GET', 'POST'])
@login_required
def take_test(test_id):
    if not hasattr(current_user, 'student_id'):
        flash("Доступ разрешён только для студентов.")
        return redirect(url_for('main.index'))
    assignment = TestAssignment.query.filter_by(test_id=test_id, student_id=current_user.id).first()
    if not assignment:
        flash("Тест не назначен для вас.")
        return redirect(url_for('main.student_tests'))
    if assignment.status == 'taken':
        flash("Вы уже прошли этот тест.")
        return redirect(url_for('main.student_tests'))
    test = Test.query.get(test_id)
    if test.test_type != 'choice':
        flash("Этот тест предназначен для режима свободного ответа. Перейдите на многостраничный режим.")
        return redirect(url_for('main.student_tests'))
    options = TestOption.query.filter_by(test_id=test_id).all()
    if request.method == 'POST':
        uploaded_file = request.files.get('uploaded_file')
        file_path = None
        if uploaded_file and uploaded_file.filename != "":
            filename = secure_filename(uploaded_file.filename)
            upload_folder = current_app.config.get('UPLOAD_FOLDER')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            file_path = os.path.join(upload_folder, filename)
            uploaded_file.save(file_path)
            file_path = filename
        selected_option = request.form.get('selected_option')
        if not selected_option:
            flash("Выберите вариант ответа.")
            return redirect(url_for('main.take_test', test_id=test_id))
        result = TestResult(
            test_id=test_id,
            student_id=current_user.id,
            selected_option_id=int(selected_option),
            file_path=file_path,
            grade=None
        )
        assignment.status = 'taken'
        db.session.add(result)
        db.session.commit()
        flash("Тест отправлен! Преподаватель оценит ваш ответ позже.")
        return redirect(url_for('main.student_tests'))
    return render_template("take_test.html", test=test, options=options)

@bp.route('/student/take_test_multi/<int:test_id>/start', methods=['GET'])
@login_required
def start_test_multi(test_id):
    session['test_%d_answers' % test_id] = {}
    return redirect(url_for('main.take_test_multi', test_id=test_id, question_index=0))

@bp.route('/student/take_test_multi/<int:test_id>/<int:question_index>', methods=['GET', 'POST'])
@login_required
def take_test_multi(test_id, question_index):
    if not hasattr(current_user, 'student_id'):
        flash("Доступ разрешён только для студентов.")
        return redirect(url_for('main.index'))

    assignment = TestAssignment.query.filter_by(test_id=test_id, student_id=current_user.id).first()
    if not assignment:
        flash("Тест не назначен для вас.")
        return redirect(url_for('main.student_tests'))
    if assignment.status == 'taken':
        flash("Вы уже прошли этот тест.")
        return redirect(url_for('main.student_tests'))

    test = Test.query.get(test_id)
    questions = test.questions
    total_questions = len(questions)
    if total_questions == 0:
        if test.test_type != 'choice':
            default_question = Question(test_id=test.id, text="Введите ваш ответ:", image_path=None)
            db.session.add(default_question)
            db.session.commit()
            questions = test.questions
            total_questions = len(questions)
        else:
            flash("В тесте нет вопросов.")
            return redirect(url_for('main.student_tests'))
    if question_index < 0 or question_index >= total_questions:
        flash("Неверный номер вопроса.")
        return redirect(url_for('main.take_test_multi', test_id=test_id, question_index=0))

    if not assignment.start_time:
        assignment.start_time = datetime.utcnow()
        db.session.commit()
    elapsed = (datetime.utcnow() - assignment.start_time).total_seconds()
    if elapsed > test.duration * 60:
        flash("Время теста истекло!")
        assignment.status = 'taken'
        db.session.commit()
        return redirect(url_for('main.student_tests'))

    current_question = questions[question_index]

    if request.method == 'POST':
        uploaded_file = request.files.get('uploaded_file')
        file_path = None
        if uploaded_file and uploaded_file.filename != "":
            filename = secure_filename(uploaded_file.filename)
            upload_folder = current_app.config.get('UPLOAD_FOLDER')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            file_path = os.path.join(upload_folder, filename)
            uploaded_file.save(file_path)
            file_path = filename

        if test.test_type == 'choice':
            if current_question.options and len(current_question.options) > 0:
                answer = request.form.get('selected_option')
                if not answer:
                    flash("Выберите вариант ответа для вопроса " + str(question_index + 1) + ".")
                    return redirect(url_for('main.take_test_multi', test_id=test_id, question_index=question_index))
                session['test_%d_answers' % test_id][str(current_question.id)] = {
                    'selected_option_id': int(answer),
                    'file_path': file_path
                }
            else:
                flash("Для вопроса " + str(question_index + 1) + " не заданы варианты ответа.")
                return redirect(url_for('main.student_tests'))
        else:
            answer = request.form.get('answer')
            if not answer:
                flash("Введите ваш ответ для вопроса " + str(question_index + 1) + ".")
                return redirect(url_for('main.take_test_multi', test_id=test_id, question_index=question_index))
            session['test_%d_answers' % test_id][str(current_question.id)] = {
                'answer_text': answer,
                'file_path': file_path
            }
        next_index = question_index + 1
        if next_index < total_questions:
            return redirect(url_for('main.take_test_multi', test_id=test_id, question_index=next_index))
        else:
            answers = session.get('test_%d_answers' % test_id, {})
            for q in questions:
                ans = answers.get(str(q.id))
                if q.options and len(q.options) > 0:
                    if ans and 'selected_option_id' in ans:
                        q_result = QuestionResult(
                            question_id=q.id,
                            student_id=current_user.id,
                            selected_option_id=ans['selected_option_id'],
                            grade=None
                        )
                        if 'file_path' in ans:
                            q_result.file_path = ans['file_path']
                        db.session.add(q_result)
                else:
                    if ans and 'answer_text' in ans:
                        q_result = QuestionResult(
                            question_id=q.id,
                            student_id=current_user.id,
                            answer_text=ans['answer_text'],
                            grade=None
                        )
                        if 'file_path' in ans:
                            q_result.file_path = ans['file_path']
                        db.session.add(q_result)
            assignment.status = 'taken'
            db.session.commit()
            flash("Тест отправлен!")
            session.pop('test_%d_answers' % test_id, None)
            return redirect(url_for('main.student_tests'))

    return render_template("take_test_multi.html", test=test, question=current_question,
                           question_index=question_index, total_questions=total_questions)

@bp.route('/download/<filename>')
@login_required
def download_file(filename):
    upload_folder = current_app.config.get('UPLOAD_FOLDER')
    return send_from_directory(upload_folder, filename, as_attachment=True)

@bp.route('/student/results')
@login_required
def student_results():
    if not hasattr(current_user, 'student_id'):
        flash("Доступ разрешён только для студентов.")
        return redirect(url_for('main.index'))
    test_results = TestResult.query.filter_by(student_id=current_user.id).all()
    question_results = QuestionResult.query.filter_by(student_id=current_user.id).all()
    return render_template("student_results.html", test_results=test_results, question_results=question_results)

@bp.route('/teacher/grade_question/<int:result_id>', methods=['GET', 'POST'])
@login_required
def grade_question(result_id):
    if not hasattr(current_user, 'username'):
        flash("Доступ разрешён только для преподавателей.")
        return redirect(url_for('main.index'))
    q_result = QuestionResult.query.get(result_id)
    if not q_result:
        flash("Результат не найден.")
        return redirect(url_for('main.test_results'))
    if request.method == 'POST':
        new_grade = request.form.get('grade')
        comment = request.form.get('comment')
        try:
            new_grade = int(new_grade)
        except ValueError:
            flash("Оценка должна быть числом.")
            return redirect(url_for('main.grade_question', result_id=result_id))
        q_result.grade = new_grade
        q_result.comments = comment
        db.session.commit()
        flash("Оценка и комментарий сохранены.")
        return redirect(url_for('main.test_results'))
    return render_template("grade_question.html", result=q_result)


@bp.route('/teacher/grade_test/<int:test_id>/<int:student_id>', methods=['GET', 'POST'])
@login_required
def grade_test(test_id, student_id):
    if not hasattr(current_user, 'username'):
        flash("Доступ разрешён только для преподавателей.")
        return redirect(url_for('main.index'))

    assignment = TestAssignment.query.filter_by(test_id=test_id, student_id=student_id).first()
    if not assignment or assignment.status != 'taken':
        flash("Тест ещё не сдан или результаты отсутствуют.")
        return redirect(url_for('main.test_results'))

    q_results = QuestionResult.query.join(Question).filter(
        Question.test_id == test_id,
        QuestionResult.student_id == student_id
    ).all()

    if request.method == 'POST':
        overall_grade = request.form.get('overall_grade')
        overall_comment = request.form.get('overall_comment')
        try:
            overall_grade = int(overall_grade)
        except ValueError:
            flash("Оценка должна быть числом.")
            return redirect(url_for('main.grade_test', test_id=test_id, student_id=student_id))
        for res in q_results:
            res.grade = overall_grade
            res.comments = overall_comment
        db.session.commit()
        flash("Оценка и комментарии сохранены.")
        return redirect(url_for('main.test_results'))

    test_obj = Test.query.get(test_id)
    student_obj = Student.query.get(student_id)
    return render_template("grade_test.html", test=test_obj, student=student_obj, q_results=q_results)
