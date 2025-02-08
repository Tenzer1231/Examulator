#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Этот скрипт заполняет базу данных начальными данными:
- Добавляет предметы (Subject)
- Добавляет преподавателя с базовыми логином и паролем
- Добавляет студентов с базовыми данными
- Добавляет тест с режимом (choice/free_response)
- Добавляет несколько вопросов к тесту с вариантами ответа
- Добавляет назначение теста студенту (опционально)
"""

from app import create_app, db
from app.models import (
    Student, Teacher, Subject, Test, TestAssignment,
    Question, QuestionOption
)

app = create_app()

with app.app_context():
    # Для чистого старта (удалите старую базу, если она есть)
    db.drop_all()
    db.create_all()

    # Добавляем предметы
    subject1 = Subject(name="Программирование")
    subject2 = Subject(name="Математика")
    db.session.add_all([subject1, subject2])
    db.session.commit()

    # Добавляем преподавателя
    teacher1 = Teacher(full_name="Петр Петров", username="petr")
    teacher1.set_password("secret")  # Используем хеширование пароля
    db.session.add(teacher1)
    db.session.commit()

    # Добавляем студентов
    student1 = Student(full_name="Иван Иванов", group="101", student_id="123456")
    student2 = Student(full_name="Сергей Сергеев", group="102", student_id="654321")
    db.session.add_all([student1, student2])
    db.session.commit()

    # Добавляем тест для предмета "Программирование"
    # Устанавливаем режим теста "choice" (с выбором ответа); если нужен свободный ответ, укажите "free_response"
    test1 = Test(
        subject_id=subject1.id,
        title="Основы Python",
        description="Ответьте на следующие вопросы по основам Python.",
        duration=10,  # продолжительность теста в минутах
        test_type="choice"
    )
    db.session.add(test1)
    db.session.commit()

    # Добавляем первый вопрос в тест
    question1 = Question(
        test_id=test1.id,
        text="Какой из вариантов соответствует объявлению переменной в Python?",
        image_path=None
    )
    db.session.add(question1)
    db.session.commit()

    # Добавляем варианты ответов для первого вопроса
    q1_opt1 = QuestionOption(question_id=question1.id, option_text="var a = 10;", is_correct=False)
    q1_opt2 = QuestionOption(question_id=question1.id, option_text="a = 10", is_correct=True)
    q1_opt3 = QuestionOption(question_id=question1.id, option_text="int a = 10;", is_correct=False)
    db.session.add_all([q1_opt1, q1_opt2, q1_opt3])
    db.session.commit()

    # Добавляем второй вопрос в тест (продолжаем создавать вопросы "непрерывно")
    question2 = Question(
        test_id=test1.id,
        text="Что выведет следующий код: print(2 + 2)?",
        image_path=None
    )
    db.session.add(question2)
    db.session.commit()

    # Добавляем варианты ответов для второго вопроса
    q2_opt1 = QuestionOption(question_id=question2.id, option_text="22", is_correct=False)
    q2_opt2 = QuestionOption(question_id=question2.id, option_text="4", is_correct=True)
    q2_opt3 = QuestionOption(question_id=question2.id, option_text="2 + 2", is_correct=False)
    db.session.add_all([q2_opt1, q2_opt2, q2_opt3])
    db.session.commit()

    # (Опционально) Назначаем тест студенту
    assignment1 = TestAssignment(test_id=test1.id, student_id=student1.id, status='not_taken')
    db.session.add(assignment1)
    db.session.commit()

    print("Базовые данные успешно добавлены!")
