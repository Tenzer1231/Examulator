# run.py
# -*- coding: utf-8 -*-
from app import create_app, db
from app.models import Student, Teacher, Subject, Test, TestAssignment, TestResult, TestOption, Faculty, Group

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

