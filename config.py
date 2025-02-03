# config.py
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Используем SQLite для MVP, можно переключиться на MySQL
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your-secret-key'  # Замените на надёжное значение
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
