#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Этот скрипт заполняет базу данных начальными данными:
- Добавляет предметы (Subject)
- Добавляет преподавателя с базовыми логином и паролем
- Добавляет студентов с базовыми данными
- Добавляет тесты с вариантами ответов
"""

from app import create_app, db
from app.models import Student, Teacher, Subject, Test, TestOption

app = create_app()

with app.app_context():
    # Создаю таблицы, если они ещё не созданы
    db.create_all()

    # Добавляю предметы
    subject1 = Subject(name="Программирование")
    subject2 = Subject(name="Математика")
    db.session.add_all([subject1, subject2])
    db.session.commit()

    # Добавляю преподавателя
    teacher1 = Teacher(full_name="Петр Петров", username="petr", password="secret")
    db.session.add(teacher1)

    # Добавляю студентов
    student1 = Student(full_name="Иван Иванов", group="101", student_id="123456")
    student2 = Student(full_name="Сергей Сергеев", group="102", student_id="654321")
    db.session.add_all([student1, student2])
    db.session.commit()

    # Добавляю тест с вариантами ответов для предмета "Программирование"
    test1 = Test(
        subject_id=subject1.id,
        title="Основы Python",
        description="Какой из вариантов соответствует объявлению переменной в Python?",
        duration=10  # Продолжительность теста в минутах
    )
    db.session.add(test1)
    db.session.commit()

    # Добавляю варианты ответов для теста
    option1 = TestOption(test_id=test1.id, option_text="var a = 10;", is_correct=False)
    option2 = TestOption(test_id=test1.id, option_text="a = 10", is_correct=True)
    option3 = TestOption(test_id=test1.id, option_text="int a = 10;", is_correct=False)
    db.session.add_all([option1, option2, option3])
    db.session.commit()

    print("Базовые данные успешно добавлены!")
