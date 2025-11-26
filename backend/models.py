from backend.app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Association tables for many-to-many relationships
student_school = db.Table('student_school',
    db.Column('student_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('school_id', db.Integer, db.ForeignKey('school.id'), primary_key=True)
)

lecturer_student = db.Table('lecturer_student',
    db.Column('lecturer_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('student_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class User(db.Model):
    """User model representing all system users (Admin, Lecturer, Student)."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'lecturer', 'student'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Role-specific relationships
    # For students
    assigned_schools = db.relationship('School', secondary=student_school, backref=db.backref('assigned_students', lazy='dynamic'))
    supervisors = db.relationship('User', secondary=lecturer_student, 
                                 primaryjoin=id==lecturer_student.c.student_id,
                                 secondaryjoin=id==lecturer_student.c.lecturer_id,
                                 backref=db.backref('supervised_students', lazy='dynamic'))
    
    # Student reports
    reports = db.relationship('Report', backref='student', lazy='dynamic', 
                             foreign_keys='Report.student_id')
    
    # Lecturer evaluations
    evaluations_given = db.relationship('Evaluation', backref='lecturer', lazy='dynamic',
                                       foreign_keys='Evaluation.lecturer_id')
    
    # Methods
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<User {self.username}>'


class School(db.Model):
    """Schools where students are placed for teaching practice."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    contact_person = db.Column(db.String(100))
    contact_email = db.Column(db.String(120))
    contact_phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'contact_person': self.contact_person,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone
        }

    def __repr__(self):
        return f'<School {self.name}>'


class Report(db.Model):
    """Reports submitted by students during teaching practice."""
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    report_type = db.Column(db.String(50))  # e.g., 'daily', 'weekly', 'lesson_plan'
    file_path = db.Column(db.String(255))  # Path to uploaded file
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='submitted')  # e.g., 'submitted', 'reviewed'
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'title': self.title,
            'content': self.content,
            'report_type': self.report_type,
            'file_path': self.file_path,
            'submission_date': self.submission_date.isoformat() if self.submission_date else None,
            'status': self.status
        }

    def __repr__(self):
        return f'<Report {self.title}>'


class Evaluation(db.Model):
    """Evaluations submitted by lecturers for students."""
    id = db.Column(db.Integer, primary_key=True)
    lecturer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    visit_date = db.Column(db.DateTime, nullable=False)
    teaching_skills = db.Column(db.Integer)  # Scale 1-10
    classroom_management = db.Column(db.Integer)  # Scale 1-10
    lesson_preparation = db.Column(db.Integer)  # Scale 1-10
    professionalism = db.Column(db.Integer)  # Scale 1-10
    comments = db.Column(db.Text)
    overall_grade = db.Column(db.String(2))  # e.g., 'A', 'B+', 'C'
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with the evaluated student
    student = db.relationship('User', foreign_keys=[student_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'lecturer_id': self.lecturer_id,
            'student_id': self.student_id,
            'visit_date': self.visit_date.isoformat() if self.visit_date else None,
            'teaching_skills': self.teaching_skills,
            'classroom_management': self.classroom_management,
            'lesson_preparation': self.lesson_preparation,
            'professionalism': self.professionalism,
            'comments': self.comments,
            'overall_grade': self.overall_grade,
            'submission_date': self.submission_date.isoformat() if self.submission_date else None
        }

    def __repr__(self):
        return f'<Evaluation {self.id}>'


class TeachingPracticeSession(db.Model):
    """Teaching practice sessions/periods."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='upcoming')  # 'upcoming', 'ongoing', 'completed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'description': self.description,
            'status': self.status
        }

    def __repr__(self):
        return f'<TeachingPracticeSession {self.title}>'


class Notification(db.Model):
    """System notifications for users."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('notifications', lazy='dynamic'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Notification {self.title}>'