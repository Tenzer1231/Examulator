# app/views.py
# -*- coding: utf-8 -*-
import os
from flask import Blueprint, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.utils import secure_filename
from app import db
from app.models import Student, Teacher, Subject, Test, TestOption, TestAssignment, TestResult

bp = Blueprint('main', __name__)


#################################
# Главная страница и авторизация
#################################

@bp.route('/')
def index():
    return "Привет! Это базовое приложение системы тестирования на Flask."


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
    return '''
        <h3>Авторизация</h3>
        <form method="post">
            <label>Тип пользователя:</label>
            <select name="user_type" id="user_type">
                <option value="student">Студент</option>
                <option value="teacher">Преподаватель</option>
            </select><br><br>
            <div id="student_fields">
                Номер студенческого билета: <input type="text" name="student_id"><br>
            </div>
            <div id="teacher_fields" style="display:none;">
                Логин: <input type="text" name="username"><br>
                Пароль: <input type="password" name="password"><br>
            </div>
            <input type="submit" value="Войти">
        </form>
        <script>
            const select = document.getElementById('user_type');
            const studentFields = document.getElementById('student_fields');
            const teacherFields = document.getElementById('teacher_fields');
            select.addEventListener('change', function() {
                if (this.value === 'student') {
                    studentFields.style.display = 'block';
                    teacherFields.style.display = 'none';
                } else {
                    studentFields.style.display = 'none';
                    teacherFields.style.display = 'block';
                }
            });
        </script>
    '''


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из системы")
    return redirect(url_for('main.login'))


@bp.route('/dashboard')
@login_required
def dashboard():
    if hasattr(current_user, 'student_id'):
        return f'''
            <h3>Личный кабинет студента: {current_user.full_name}</h3>
            <a href="/student/tests">Просмотреть тесты</a><br>
            <a href="/logout">Выйти</a>
        '''
    else:
        return f'''
            <h3>Личный кабинет преподавателя: {current_user.full_name}</h3>
            <a href="/teacher/create_test">Создать тест</a><br>
            <a href="/teacher/assign_test">Назначить тест</a><br>
            <a href="/teacher/test_results">Просмотреть результаты тестов</a><br>
            <a href="/logout">Выйти</a>
        '''


#################################
# Функционал преподавателя
#################################

# Создание теста с вариантами ответов и указанием правильных вариантов
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
        options_text = request.form.get('options')  # Варианты, разделённые переносами строк
        correct_options = request.form.get('correct_options')  # Номера правильных вариантов через запятую
        if not (subject_id and title and duration):
            flash("Заполните обязательные поля: предмет, название теста, продолжительность.")
            return redirect(url_for('main.create_test'))
        try:
            duration = int(duration)
        except ValueError:
            flash("Продолжительность должна быть числом.")
            return redirect(url_for('main.create_test'))
        new_test = Test(subject_id=subject_id, title=title, description=description, duration=duration)
        db.session.add(new_test)
        db.session.commit()
        if options_text:
            options = options_text.strip().split('\n')
            correct_indices = []
            if correct_options:
                try:
                    correct_indices = [int(x.strip()) for x in correct_options.split(',') if x.strip().isdigit()]
                except Exception:
                    flash("Неправильный формат правильных вариантов.")
                    return redirect(url_for('main.create_test'))
            for idx, opt in enumerate(options, start=1):
                opt = opt.strip()
                if opt:
                    is_correct = idx in correct_indices
                    test_option = TestOption(test_id=new_test.id, option_text=opt, is_correct=is_correct)
                    db.session.add(test_option)
            db.session.commit()
        flash("Тест успешно создан!")
        return redirect(url_for('main.dashboard'))

    subjects = Subject.query.all()
    subjects_options = ''.join([f'<option value="{sub.id}">{sub.name}</option>' for sub in subjects])
    return f'''
        <h3>Создание теста</h3>
        <form method="post">
            Предмет: <select name="subject_id">{subjects_options}</select><br>
            Название теста: <input type="text" name="title"><br>
            Описание: <textarea name="description"></textarea><br>
            Продолжительность (в минутах): <input type="number" name="duration"><br>
            Варианты ответа (по одному варианту в строке):<br>
            <textarea name="options"></textarea><br>
            Номера правильных вариантов (через запятую, например: 1,3):<br>
            <input type="text" name="correct_options"><br>
            <input type="submit" value="Создать тест">
        </form>
        <a href="/dashboard">Назад в кабинет</a>
    '''


# Назначение теста студенту
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
    tests_options = ''.join([f'<option value="{test.id}">{test.title}</option>' for test in tests])
    students_options = ''.join([f'<option value="{stu.id}">{stu.full_name}</option>' for stu in students])

    return f'''
         <h3>Назначение теста студенту</h3>
         <form method="post">
             Тест: <select name="test_id">{tests_options}</select><br>
             Студент: <select name="student_id">{students_options}</select><br>
             <input type="submit" value="Назначить тест">
         </form>
         <a href="/dashboard">Назад в кабинет</a>
    '''


# Просмотр результатов тестов преподавателем
@bp.route('/teacher/test_results')
@login_required
def test_results():
    if not hasattr(current_user, 'username'):
        flash("Доступ разрешён только преподавателям.")
        return redirect(url_for('main.index'))

    results = TestResult.query.all()
    html = "<h3>Результаты тестов</h3>"
    for res in results:
        student = Student.query.get(res.student_id)
        test = Test.query.get(res.test_id)
        if res.selected_option_id:
            opt = TestOption.query.get(res.selected_option_id)
            option_text = f"Выбранный вариант: {opt.option_text}" if opt else ""
        else:
            option_text = f"Ответ: {res.answer_text}"
        file_info = f", Файл: {res.file_path}" if res.file_path else ""
        grade_text = f", Оценка: {res.grade}" if res.grade is not None else ""
        html += f'<div>Студент: {student.full_name}, Тест: {test.title}, {option_text}{file_info}{grade_text}</div>'
    html += '<br><a href="/dashboard">Назад в кабинет</a>'
    return html


#################################
# Функционал студента
#################################

# Просмотр списка тестов, назначенных студенту
@bp.route('/student/tests')
@login_required
def student_tests():
    if not hasattr(current_user, 'student_id'):
        flash("Доступ разрешён только для студентов.")
        return redirect(url_for('main.index'))

    assignments = TestAssignment.query.filter_by(student_id=current_user.id).all()
    html = "<h3>Ваши тесты</h3>"
    for assign in assignments:
        test = Test.query.get(assign.test_id)
        html += f'<div><a href="/student/test/{test.id}">{test.title}</a> - Статус: {assign.status}</div>'
    html += '<br><a href="/dashboard">Назад к кабинету</a>'
    return html


# Прохождение теста студентом с возможностью загрузки файлов
@bp.route('/student/test/<int:test_id>', methods=['GET', 'POST'])
@login_required
def take_test(test_id):
    if not hasattr(current_user, 'student_id'):
        flash("Доступ разрешён только для студентов.")
        return redirect(url_for('main.index'))

    assignment = TestAssignment.query.filter_by(test_id=test_id, student_id=current_user.id).first()
    if not assignment:
        flash("Тест не назначен для вас.")
        return redirect(url_for('main.student_tests'))

    # Если тест уже пройден, запретим повторное прохождение
    if assignment.status == 'taken':
        flash("Вы уже прошли этот тест.")
        return redirect(url_for('main.student_tests'))

    test = Test.query.get(test_id)
    options = TestOption.query.filter_by(test_id=test_id).all()

    if request.method == 'POST':
        # Обработка загрузки файла
        uploaded_file = request.files.get('uploaded_file')
        file_path = None
        if uploaded_file and uploaded_file.filename != "":
            from werkzeug.utils import secure_filename
            filename = secure_filename(uploaded_file.filename)
            upload_folder = current_app.config.get('UPLOAD_FOLDER')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            file_path = os.path.join(upload_folder, filename)
            uploaded_file.save(file_path)
            # Для хранения в базе можно сохранить только имя файла:
            file_path = filename

        # Если тест имеет варианты ответа
        if options:
            selected_option = request.form.get('selected_option')
            if not selected_option:
                flash("Выберите вариант ответа.")
                return redirect(url_for('main.take_test', test_id=test_id))
            option = TestOption.query.get(int(selected_option))
            grade = 100 if option and option.is_correct else 0
            result = TestResult(
                test_id=test_id,
                student_id=current_user.id,
                selected_option_id=int(selected_option),
                file_path=file_path,
                grade=grade
            )
        else:
            # Если вариантов ответа нет — ожидается текстовый ответ
            answer = request.form.get('answer')
            if not answer:
                flash("Введите ваш ответ.")
                return redirect(url_for('main.take_test', test_id=test_id))
            result = TestResult(
                test_id=test_id,
                student_id=current_user.id,
                answer_text=answer,
                file_path=file_path
            )
        assignment.status = 'taken'
        db.session.add(result)
        db.session.commit()
        flash("Тест отправлен!")
        return redirect(url_for('main.student_tests'))

    # Формирование HTML-формы для GET-запроса
    if options:
        options_html = ''.join([f'<input type="radio" name="selected_option" value="{opt.id}">{opt.option_text}<br>' for opt in options])
        form_fields = options_html
    else:
        form_fields = 'Ваш ответ: <textarea name="answer"></textarea><br>'

    file_field = 'Загрузить файл (если требуется): <input type="file" name="uploaded_file"><br>'

    form_html = f'''
         <h3>{test.title}</h3>
         <p>{test.description}</p>
         <form method="post" enctype="multipart/form-data">
             {form_fields}
             {file_field}
             <input type="submit" value="Отправить тест">
         </form>
    '''

    # Добавляем блок таймера, который начнет отсчет после полной загрузки DOM
    timer_script = f"""
        <div id="timer" style="font-weight:bold; font-size:20px;"></div>
        <script>
            document.addEventListener("DOMContentLoaded", function() {{
                var totalTime = {test.duration} * 60;
                var timerElement = document.getElementById("timer");
                var interval = setInterval(function() {{
                    var minutes = Math.floor(totalTime / 60);
                    var seconds = totalTime % 60;
                    timerElement.innerHTML = "Осталось времени: " + minutes + " м " + seconds + " с";
                    if(totalTime <= 0) {{
                        clearInterval(interval);
                        alert("Время истекло!");
                        document.querySelector("form").submit();
                    }}
                    totalTime--;
                }}, 1000);
            }});
        </script>
    """
    form_html += timer_script
    form_html += '<br><a href="/student/tests">Назад к тестам</a>'
    return form_html

