# run.py
# -*- coding: utf-8 -*-
from app import create_app, db
from app.models import Student, Teacher, Subject, Test, TestAssignment, TestResult, TestOption

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

'''
1) Сделать хэширование паролей
2) Сделать редактироваине тестов
- Добавить ограничение на количество попыток (сейчас можно пересдавать бесконечно)
- Тест автоматически закрывается после таймера ❌ (JS-таймер есть, но сервер не проверяет!).
3) Групповое назначение тестов (сразу нескольким студентам). Добавить e-mail уведомления студентам (если Flask-Mail подключен).
4) Добавить автооценку тестов (если есть варианты ответов).
5) Добавить меню навигации (dashboard.html). и красоту
6) Добавить поле submission_time (чтобы видеть, когда тест был сдан).
- Связать TestAssignment с status (не начат / в процессе / сдан).
- Добавить поле max_attempts (сколько раз можно пересдавать).

'''
