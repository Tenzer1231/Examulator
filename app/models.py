# app/models.py
# -*- coding: utf-8 -*-
from app import db
from datetime import datetime
from flask_login import UserMixin

# Существующие модели студентов и преподавателей
class Student(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    group = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.String(50), unique=True, nullable=False)

    def get_id(self):
        return f"student-{self.id}"

    def __repr__(self):
        return f'<Student {self.full_name}>'

class Teacher(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def get_id(self):
        return f"teacher-{self.id}"

    def __repr__(self):
        return f'<Teacher {self.full_name}>'

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<Subject {self.name}>'

# Модель теста; добавлено поле test_type, которое может быть "choice" или "free_response"
class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    duration = db.Column(db.Integer, nullable=False)  # в минутах
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    image_path = db.Column(db.String(255))
    test_type = db.Column(db.String(20), nullable=False, default='choice')  # "choice" или "free_response"
    # Если тест многостраничный, вопросы добавляются через модель Question
    questions = db.relationship('Question', backref='test', lazy=True)

    def __repr__(self):
        return f'<Test {self.title}>'

# Модель для вопросов многостраничного теста
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(255))  # Опционально, если вопрос сопровождается изображением
    # Если вопрос с выбором ответа, варианты записываются в QuestionOption
    options = db.relationship('QuestionOption', backref='question', lazy=True)

    def __repr__(self):
        return f'<Question {self.id} for Test {self.test_id}>'

# Модель для вариантов ответа к вопросу
class QuestionOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    option_text = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<QuestionOption {self.option_text}>'

# Если требуется поддержка тестов с одним вопросом (старый режим), можно оставить модель TestOption
class TestOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)
    option_text = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<TestOption {self.option_text}>'

# Модель для назначения теста студенту
class TestAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    status = db.Column(db.String(20), default='not_taken')  # not_taken или taken
    start_time = db.Column(db.DateTime, nullable=True)  # время начала прохождения теста

    test = db.relationship('Test', backref='assignments', lazy=True)
    student = db.relationship('Student', backref='assignments', lazy=True)

    def __repr__(self):
        return f'<TestAssignment Test: {self.test_id}, Student: {self.student_id}>'

# Модель для результатов теста в режиме с одним вопросом (оставляем для backward compatibility)
class TestResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    selected_option_id = db.Column(db.Integer, db.ForeignKey('test_option.id'), nullable=True)
    answer_text = db.Column(db.Text)
    file_path = db.Column(db.String(255))
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)
    grade = db.Column(db.Integer)  # Оценка, выставляемая преподавателем
    comments = db.Column(db.Text)

    test = db.relationship('Test', backref='results', lazy=True)
    student = db.relationship('Student', backref='results', lazy=True)
    selected_option = db.relationship('TestOption', foreign_keys=[selected_option_id], lazy=True)

    def __repr__(self):
        return f'<TestResult Test: {self.test_id}, Student: {self.student_id}>'

# Новая модель для сохранения ответов на отдельные вопросы в многостраничном тесте
class QuestionResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    selected_option_id = db.Column(db.Integer, db.ForeignKey('question_option.id'), nullable=True)
    answer_text = db.Column(db.Text)
    file_path = db.Column(db.String(255))
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)
    # Оценка и комментарии для конкретного вопроса (если нужно)
    grade = db.Column(db.Integer)
    comments = db.Column(db.Text)

    question = db.relationship('Question', backref='results', lazy=True)
    student = db.relationship('Student', backref='question_results', lazy=True)
    selected_option = db.relationship('QuestionOption', foreign_keys=[selected_option_id], lazy=True)

    def __repr__(self):
        return f'<QuestionResult Question: {self.question_id}, Student: {self.student_id}>'
