# -*- coding: utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    Migrate(app, db)  # Инициализация Flask-Migrate

    from app.views import bp as main_bp
    from app.auth import auth_bp  # 👈 Добавляем auth_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')  # 👈 Теперь login – это /auth/login

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'  # 👈 Исправляем здесь
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        """ Загружает пользователя по ID """
        try:
            user_type, id_str = user_id.split('-', 1)
            uid = int(id_str)
        except Exception:
            return None

        if user_type == 'student':
            from app.models import Student
            return Student.query.get(uid)
        elif user_type == 'teacher':
            from app.models import Teacher
            return Teacher.query.get(uid)
        return None

    return app
