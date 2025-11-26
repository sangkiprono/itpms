Teaching Practice Management System

A comprehensive platform for managing and evaluating teaching practice experiences for educational institutions.

 Features

- Multi-User Roles: Admin, Lecturer, and Student interfaces
- School Management: Register and manage schools for teaching practice placements
- Student Assignment: Assign students to schools and supervisors
- Report Submission: Students can submit daily, weekly, and final reports
- Evaluation System: Lecturers can evaluate student performance
- Progress Tracking: Monitor student progress throughout teaching practice
- Feedback Mechanism: Provide structured feedback to students

 Project Structure

The project follows a modern web architecture:
- Backend: Flask API with SQLAlchemy ORM
- Frontend: HTML, CSS, JavaScript with Bootstrap

 Requirements

- Python 3.8 or higher
- Node.js (optional, for development tools)
- SQL Database (SQLite for development, PostgreSQL recommended for production)

 Installation

 1. Clone the repository

```bash
git clone https://github.com/yourusername/teaching-practice-system.git
cd teaching-practice-system
```

 2. Set up a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

 3. Install dependencies

```bash
pip install -r requirements.txt
```

 4. Set up environment variables

Create a `.env` file in the project root with the following variables:

```
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret_key
DATABASE_URL=sqlite:///teaching_practice.db
```

For production, update these values accordingly.

 5. Initialize the database

```bash
flask db init
flask db migrate
flask db upgrade
```

 6. Run the application

```bash
flask run
```

The application will be available at http://localhost:5000

 Default Users (after seeding the database)

- Admin:
  - Username: admin
  - Password: admin123

- Lecturer:
  - Username: lecturer
  - Password: lecturer123

- Student:
  - Username: student
  - Password: student123

 API Documentation

The API provides the following endpoints:

 Authentication

- `POST /api/auth/login`: User login
- `POST /api/auth/register`: Register new user (admin only)
- `GET /api/auth/me`: Get current user details
- `PUT /api/auth/change-password`: Change password

 Admin Endpoints

- `/api/admin/users`: Manage users
- `/api/admin/schools`: Manage schools
- `/api/admin/sessions`: Manage teaching practice sessions
- `/api/admin/dashboard`: Get admin dashboard data

 Lecturer Endpoints

- `/api/lecturer/students`: Get assigned students
- `/api/lecturer/evaluations`: Submit and manage evaluations
- `/api/lecturer/dashboard`: Get lecturer dashboard data

Student Endpoints

- `/api/student/schools`: Get assigned schools
- `/api/student/supervisors`: Get assigned supervisors
- `/api/student/reports`: Submit and manage reports
- `/api/student/evaluations`: View evaluations
- `/api/student/dashboard`: Get student dashboard data
Frontend Pages

Admin Interface

- Dashboard
- Manage Users
- Manage Schools
- Assignments
- Reports

Lecturer Interface

- Dashboard
- My Students
- Evaluations
- Student Reports

Student Interface

- Dashboard
- My Reports
- Evaluations & Feedback
- Lesson Plans

Development

Backend

The backend is built with Flask and follows a modular approach:
- Models: Database models using SQLAlchemy
- Routes: API endpoints for each user role
- Services: Business logic layer
- Utils: Helper functions and utilities

Frontend

The frontend uses vanilla JavaScript with Bootstrap for styling:
- Assets: CSS, JavaScript, and images
- HTML pages for each user role
- JavaScript modules for API communication and UI manipulation

Deployment

For production deployment:

1. Update environment variables for production
2. Use a production-ready database (PostgreSQL recommended)
3. Set up WSGI server (Gunicorn, uWSGI)
4. Configure reverse proxy (Nginx, Apache)
5. Enable HTTPS

License

This project is licensed under the MIT License - see the LICENSE file for details.

Acknowledgements

- Bootstrap for the UI components
- Flask for the backend framework
- SQLAlchemy for the ORM