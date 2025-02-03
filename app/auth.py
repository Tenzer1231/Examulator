# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from app import db
from app.models import Student, Teacher

auth_bp = Blueprint('auth', __name__)

login_manager = LoginManager()
login_manager.login_view = "auth.login"

# Для Flask-Login необходимо, чтобы пользователь имел атрибут id и реализовывал методы.
# Я добавлю базовую реализацию через методы модели.

@login_manager.user_loader
def load_user(user_id):
    # Здесь я могу искать сначала студента, затем преподавателя. Либо разделить системы авторизации.
    user = Student.query.get(user_id)
    if not user:
        user = Teacher.query.get(user_id)
    return user

# Пример маршрута для входа. Здесь я объединю авторизацию студентов и преподавателей для демонстрации.
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # На данном этапе я просто проверяю, по какому типу будет вход: студент или преподаватель.
        user_type = request.form.get('user_type')  # например, 'student' или 'teacher'
        if user_type == 'student':
            student_id = request.form.get('student_id')
            if not student_id:
                flash('Введите номер студенческого билета')
                return redirect(url_for('auth.login'))
            user = Student.query.filter_by(student_id=student_id).first()
        else:  # teacher
            username = request.form.get('username')
            password = request.form.get('password')
            if not username or not password:
                flash('Введите логин и пароль')
                return redirect(url_for('auth.login'))
            user = Teacher.query.filter_by(username=username, password=password).first()

        if user:
            login_user(user)
            flash('Вы успешно вошли в систему!')
            return redirect(url_for('main.index'))
        else:
            flash('Неверные данные')
            return redirect(url_for('auth.login'))
    return '''
        <h3>Авторизация</h3>
        <form method="post">
            <label>Тип пользователя:</label>
            <select name="user_type">
                <option value="student">Студент</option>
                <option value="teacher">Преподаватель</option>
            </select><br><br>
            <div id="student_fields">
                Номер студенческого билета: <input type="text" name="student_id"><br>
            </div>
            <div id="teacher_fields">
                Логин: <input type="text" name="username"><br>
                Пароль: <input type="password" name="password"><br>
            </div>
            <input type="submit" value="Войти">
        </form>
        <script>
          // Простой скрипт для переключения полей авторизации (можно улучшить)
          const select = document.querySelector('select[name="user_type"]');
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
          // Изначально показываю поля для студентов
          studentFields.style.display = 'block';
          teacherFields.style.display = 'none';
        </script>
    '''

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы')
    return redirect(url_for('main.index'))
