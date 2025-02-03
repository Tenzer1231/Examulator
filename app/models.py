# app/models.py
# -*- coding: utf-8 -*-
from app import db
from datetime import datetime
from flask_login import UserMixin


class Student(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    group = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.String(50), unique=True, nullable=False)

    def get_id(self):
        # Возвращаем id с префиксом "student-"
        return f"student-{self.id}"

    def __repr__(self):
        return f'<Student {self.full_name}>'


class Teacher(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def get_id(self):
        # Возвращаем id с префиксом "teacher-"
        return f"teacher-{self.id}"

    def __repr__(self):
        return f'<Teacher {self.full_name}>'


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<Subject {self.name}>'


class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    duration = db.Column(db.Integer, nullable=False)  # Продолжительность теста в минутах
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)

    # Связь с вариантами ответов для теста
    options = db.relationship('TestOption', backref='test', lazy=True)

    def __repr__(self):
        return f'<Test {self.title}>'


class TestOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)
    option_text = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<TestOption {self.option_text}>'


class TestAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    status = db.Column(db.String(20), default='not_taken')  # Возможные значения: not_taken, taken

    def __repr__(self):
        return f'<TestAssignment Test: {self.test_id}, Student: {self.student_id}>'


class TestResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    # Если тест проходит с вариантами, сохраняется выбранный вариант; иначе – текстовый ответ
    selected_option_id = db.Column(db.Integer, db.ForeignKey('test_option.id'), nullable=True)
    answer_text = db.Column(db.Text)  # Текстовый ответ (если нет вариантов)
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)
    grade = db.Column(db.Integer)
    comments = db.Column(db.Text)

    def __repr__(self):
        return f'<TestResult Test: {self.test_id}, Student: {self.student_id}>'
