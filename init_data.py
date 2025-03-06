# -*- coding: utf-8 -*-
"""
Этот скрипт заполняет базу данных начальными данными:
- Добавляет предметы (Subject)
- Добавляет преподавателя с базовыми логином и паролем
- Добавляет факультеты и группы
- Добавляет студентов с базовыми данными
- Добавляет тест с режимом (choice/free_response)
- Добавляет несколько вопросов к тесту с вариантами ответа
- Добавляет назначение теста студенту (опционально)
"""

from app import create_app, db
from app.models import (
    Student, Teacher, Subject, Test, TestAssignment,
    Question, QuestionOption, Faculty, Group
)

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    # Добавляем предметы
    subject1 = Subject(name="Программирование")
    subject2 = Subject(name="Математика")
    db.session.add_all([subject1, subject2])
    db.session.commit()

    # Добавляем преподавателя
    teacher1 = Teacher(full_name="Петр Петров", username="petr")
    teacher1.set_password("secret")
    db.session.add(teacher1)
    db.session.commit()

    faculty_rpo = Faculty(name="Разработка ПО")
    faculty_design = Faculty(name="Дизайн")
    db.session.add_all([faculty_rpo, faculty_design])
    db.session.commit()

    groups = []
    for faculty in [faculty_rpo, faculty_design]:
        for course in range(1, 5):
            group = Group(name=f"{faculty.name} {course} курс", course=course, faculty_id=faculty.id)
            groups.append(group)

    db.session.add_all(groups)
    db.session.commit()

    students = [
        Student(full_name="Иван Иванов", student_id="123456", group_id=groups[0].id),
        Student(full_name="Сергей Сергеев", student_id="654321", group_id=groups[1].id),
        Student(full_name="Анна Смирнова", student_id="789012", group_id=groups[2].id),
        Student(full_name="Ольга Петрова", student_id="345678", group_id=groups[3].id)
    ]

    db.session.add_all(students)
    db.session.commit()

    # -------------------------------
    # Новая часть для создания теста, вопросов и назначения
    # -------------------------------

    test1 = Test(
        subject_id=subject1.id,
        title="Основы программирования",
        description="Тест на проверку базовых знаний программирования",
        duration=30,
        test_type="choice"
    )
    db.session.add(test1)
    db.session.commit()

    question1 = Question(test_id=test1.id, text="Какой оператор используется для вывода в Python?")
    db.session.add(question1)
    db.session.commit()

    option1_q1 = QuestionOption(question_id=question1.id, option_text="print()", is_correct=True)
    option2_q1 = QuestionOption(question_id=question1.id, option_text="echo", is_correct=False)
    option3_q1 = QuestionOption(question_id=question1.id, option_text="printf", is_correct=False)
    db.session.add_all([option1_q1, option2_q1, option3_q1])
    db.session.commit()

    question2 = Question(test_id=test1.id, text="Какой из следующих вариантов обозначает комментарий в Python?")
    db.session.add(question2)
    db.session.commit()

    option1_q2 = QuestionOption(question_id=question2.id, option_text="# Комментарий", is_correct=True)
    option2_q2 = QuestionOption(question_id=question2.id, option_text="// Комментарий", is_correct=False)
    option3_q2 = QuestionOption(question_id=question2.id, option_text="/* Комментарий */", is_correct=False)
    db.session.add_all([option1_q2, option2_q2, option3_q2])
    db.session.commit()

    assignment1 = TestAssignment(test_id=test1.id, student_id=students[0].id, status='not_taken')
    db.session.add(assignment1)
    db.session.commit()

    print("Базовые данные успешно добавлены!")
