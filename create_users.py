# create_users.py
from backend.app import create_app, db
from backend.models import User

def create_users():
    app = create_app()
    with app.app_context():
        # Create lecturer
        lecturer = User.query.filter_by(username='lecturer').first()
        if not lecturer:
            lecturer = User(
                username='lecturer',
                email='lecturer@example.com',
                first_name='Lead',
                last_name='Lecturer',
                role='lecturer',
                is_active=True
            )
            lecturer.set_password('lecturer123')
            db.session.add(lecturer)
            print("Lecturer user created successfully!")
        else:
            print("Lecturer user already exists!")
            
        # Create student
        student = User.query.filter_by(username='student').first()
        if not student:
            student = User(
                username='student',
                email='student@example.com',
                first_name='Sample',
                last_name='Student',
                role='student',
                is_active=True
            )
            student.set_password('student123')
            db.session.add(student)
            print("Student user created successfully!")
        else:
            print("Student user already exists!")
            
        db.session.commit()

if __name__ == '__main__':
    create_users()