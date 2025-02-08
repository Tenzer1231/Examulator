# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from app import db
from app.models import Student, Teacher

auth_bp = Blueprint('auth', __name__)

login_manager = LoginManager()
login_manager.login_view = "auth.login"

@login_manager.user_loader
def load_user(user_id):
    """ Загружает пользователя по ID """
    if user_id.startswith("student-"):
        return Student.query.get(int(user_id.split("-")[1]))
    elif user_id.startswith("teacher-"):
        return Teacher.query.get(int(user_id.split("-")[1]))
    return None

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_type = request.form.get('user_type')

        if user_type == 'student':
            student_id = request.form.get('student_id')
            if not student_id:
                flash('Введите номер студенческого билета')
                return redirect(url_for('auth.login'))
            user = Student.query.filter_by(student_id=student_id).first()

        elif user_type == 'teacher':
            username = request.form.get('username')
            password = request.form.get('password')

            if not username or not password:
                flash('Введите логин и пароль')
                return redirect(url_for('auth.login'))

            user = Teacher.query.filter_by(username=username).first()

            if not user or not user.check_password(password):
                flash('Неверный логин или пароль')
                return redirect(url_for('auth.login'))

        if user:
            login_user(user)
            flash('Вы успешно вошли в систему!')
            return redirect(url_for('main.dashboard'))

    return render_template("login.html")

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы')
    return redirect(url_for('main.index'))
