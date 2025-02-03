# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_migrate import Migrate  # Импорт Flask-Migrate

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from app.views import bp as main_bp
    app.register_blueprint(main_bp)

    from flask_login import LoginManager
    login_manager = LoginManager()
    login_manager.login_view = 'main.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
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

    # Инициализирую Flask-Migrate
    migrate = Migrate(app, db)

    return app
