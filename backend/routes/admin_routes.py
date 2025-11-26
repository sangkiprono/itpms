from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models import User, School, TeachingPracticeSession, db
from services.admin_service import validate_user_update, validate_school, validate_teaching_session

admin_bp = Blueprint('admin', __name__)

# Helper function to check admin privileges
def admin_required():
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or current_user.role != 'admin':
        return None
    
    return current_user

# User Management Routes
@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """Get all users"""
    current_user = admin_required()
    if not current_user:
        return jsonify({'error': 'Admin privileges required'}), 403
    
    # Optional query parameters for filtering
    role = request.args.get('role')
    is_active = request.args.get('is_active')
    
    query = User.query
    
    if role:
        query = query.filter(User.role == role)
    
    if is_active is not None:
        is_active_bool = is_active.lower() == 'true'
        query = query.filter(User.is_active == is_active_bool)
    
    users = query.all()
    return jsonify({'users': [user.to_dict() for user in users]}), 200


@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get a specific user"""
    current_user = admin_required()
    if not current_user:
        return jsonify({'error': 'Admin privileges required'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': user.to_dict()}), 200


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Update a user"""
    current_user = admin_required()
    if not current_user:
        return jsonify({'error': 'Admin privileges required'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # Validate the update data
    validation_result = validate_user_update(data)
    if validation_result['error']:
        return jsonify({'error': validation_result['message']}), 400
    
    # Update user attributes
    if 'email' in data:
        user.email = data['email']
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'is_active' in data:
        user.is_active = data['is_active']
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def deactivate_user(user_id):
    """Deactivate a user (soft delete)"""
    current_user = admin_required()
    if not current_user:
        return jsonify({'error': 'Admin privileges required'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Prevent deactivating self
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot deactivate your own account'}), 400
    
    user.is_active = False
    
    try:
        db.session.commit()
        return jsonify({'message': 'User deactivated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# School Management Routes
@admin_bp.route('/schools', methods=['GET'])
@jwt_required()
def get_schools():
    """Get all schools"""
    current_user = admin_required()
    if not current_user:
        return jsonify({'error': 'Admin privileges required'}), 403
    
    schools = School.query.all()
    return jsonify({'schools': [school.to_dict() for school in schools]}), 200


@admin_bp.route('/schools', methods=['POST'])
@jwt_required()
def create_school():
    """Create a new school"""
    current_user = admin_required()
    if not current_user:
        return jsonify({'error': 'Admin privileges required'}), 403
    
    data = request.get_json()
    
    # Validate the school data
    validation_result = validate_school(data)
    if validation_result['error']:
        return jsonify({'error': validation_result['message']}), 400
    
    # Create a new school
    new_school = School(
        name=data['name'],
        address=data['address'],
        city=data['city'],
        state=data['state'],
        contact_person=data.get('contact_person', ''),
        contact_email=data.get('contact_email', ''),
        contact_phone=data.get('contact_phone', '')
    )
    
    try:
        db.session.add(new_school)
        db.session.commit()
        return jsonify({
            'message': 'School created successfully',
            'school': new_school.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/schools/<int:school_id>', methods=['PUT'])
@jwt_required()
def update_school(school_id):
    """Update a school"""
    current_user = admin_required()
    if not current_user:
        return jsonify({'error': 'Admin privileges required'}), 403
    
    school = School.query.get(school_id)
    if not school:
        return jsonify({'error': 'School not found'}), 404
    
    data = request.get_json()
    
    # Update school attributes
    if 'name' in data:
        school.name = data['name']
    if 'address' in data:
        school.address = data['address']
    if 'city' in data:
        school.city = data['city']
    if 'state' in data:
        school.state = data['state']
    if 'contact_person' in data:
        school.contact_person = data['contact_person']
    if 'contact_email' in data:
        school.contact_email = data['contact_email']
    if 'contact_phone' in data:
        school.contact_phone = data['contact_phone']
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'School updated successfully',
            'school': school.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/schools/<int:school_id>', methods=['DELETE'])
@jwt_required()
def delete_school(school_id):
    """Delete a school"""
    current_user = admin_required()
    if not current_user:
        return jsonify({'error': 'Admin privileges required'}), 403
    
    school = School.query.get(school_id)
    if not school:
        return jsonify({'error': 'School not found'}), 404
    
    # Check if the school has assigned students
    if school.assigned_students.count() > 0:
        return jsonify({'error': 'Cannot delete school with assigned students'}), 400
    
    try:
        db.session.delete(school)
        db.session.commit()
        return jsonify({'message': 'School deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# Teaching Practice Session Management
@admin_bp.route('/sessions', methods=['GET'])
@jwt_required()
def get_sessions():
    """Get all teaching practice sessions"""
    current_user = admin_required()
    if not current_user:
        return jsonify({'error': 'Admin privileges required'}), 403
    
    sessions = TeachingPracticeSession.query.all()
    return jsonify({'sessions': [session.to_dict() for session in sessions]}), 200


@admin_bp.route('/sessions', methods=['POST'])
@jwt_required()
def create_session():
    """Create a new teaching practice session"""
    current_user = admin_required()
    if not current_user:
        return jsonify({'error': 'Admin privileges required'}), 403
    
    data = request.get_json()
    
    # Validate the session data
    validation_result = validate_teaching_session(data)
    if validation_result['error']:
        return jsonify({'error': validation_result['message']}), 400
    
    # Create a new session
    new_session = TeachingPracticeSession(
        title=data['title'],
        start_date=data['start_date'],
        end_date=data['end_date'],
        description=data.get('description', ''),
        status=data.get('status', 'upcoming')
    )
    
    try:
        db.session.add(new_session)
        db.session.commit()
        return jsonify({
            'message': 'Teaching practice session created successfully',
            'session': new_session.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# Student Assignment Management
@admin_bp.route('/assign-school', methods=['POST'])
@jwt_required()
def assign_school_to_student():
    """Assign a school to a student"""
    current_user = admin_required()
    if not current_user:
        return jsonify({'error': 'Admin privileges required'}), 403
    
    data = request.get_json()
    if not data or 'student_id' not in data or 'school_id' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    student = User.query.get(data['student_id'])
    if not student or student.role != 'student':
        return jsonify({'error': 'Student not found'}), 404
    
    school = School.query.get(data['school_id'])
    if not school:
        return jsonify({'error': 'School not found'}), 404
    
    # Check if the student is already assigned to this school
    if school in student.assigned_schools:
        return jsonify({'error': 'Student already assigned to this school'}), 400
    
    # Assign the school to the student
    student.assigned_schools.append(school)
    
    try:
        db.session.commit()
        return jsonify({'message': 'School assigned to student successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/assign-lecturer', methods=['POST'])
@jwt_required()
def assign_lecturer_to_student():
    """Assign a lecturer to a student"""
    current_user = admin_required()
    if not current_user:
        return jsonify({'error': 'Admin privileges required'}), 403
    
    data = request.get_json()
    if not data or 'student_id' not in data or 'lecturer_id' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    student = User.query.get(data['student_id'])
    if not student or student.role != 'student':
        return jsonify({'error': 'Student not found'}), 404
    
    lecturer = User.query.get(data['lecturer_id'])
    if not lecturer or lecturer.role != 'lecturer':
        return jsonify({'error': 'Lecturer not found'}), 404
    
    # Check if the lecturer is already assigned to this student
    if lecturer in student.supervisors:
        return jsonify({'error': 'Lecturer already assigned to this student'}), 400
    
    # Assign the lecturer to the student
    student.supervisors.append(lecturer)
    
    try:
        db.session.commit()
        return jsonify({'message': 'Lecturer assigned to student successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# Dashboard and Reports
@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_data():
    """Get dashboard data for admin"""
    current_user = admin_required()
    if not current_user:
        return jsonify({'error': 'Admin privileges required'}), 403
    
    # Count of users by role
    admin_count = User.query.filter_by(role='admin').count()
    lecturer_count = User.query.filter_by(role='lecturer').count()
    student_count = User.query.filter_by(role='student').count()
    
    # Count of schools
    school_count = School.query.count()
    
    # Active teaching practice sessions
    active_sessions = TeachingPracticeSession.query.filter_by(status='ongoing').count()
    
    return jsonify({
        'user_counts': {
            'admin': admin_count,
            'lecturer': lecturer_count,
            'student': student_count
        },
        'school_count': school_count,
        'active_sessions': active_sessions
    }), 200