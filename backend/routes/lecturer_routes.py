from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models import User, Evaluation, Report, db
from datetime import datetime
from services.lecturer_service import validate_evaluation
import os

lecturer_bp = Blueprint('lecturer', __name__)

# Helper function to check lecturer privileges
def lecturer_required():
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or current_user.role != 'lecturer':
        return None
    
    return current_user

# Get assigned students
@lecturer_bp.route('/students', methods=['GET'])
@jwt_required()
def get_assigned_students():
    """Get students assigned to the lecturer"""
    current_user = lecturer_required()
    if not current_user:
        return jsonify({'error': 'Lecturer privileges required'}), 403
    
    # Get all students supervised by this lecturer
    students = current_user.supervised_students.all()
    
    return jsonify({
        'students': [student.to_dict() for student in students]
    }), 200

# Get student details
@lecturer_bp.route('/students/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student_details(student_id):
    """Get details of a specific student"""
    current_user = lecturer_required()
    if not current_user:
        return jsonify({'error': 'Lecturer privileges required'}), 403
    
    # Verify the student is assigned to this lecturer
    student = User.query.get(student_id)
    if not student or student.role != 'student' or current_user not in student.supervisors:
        return jsonify({'error': 'Student not found or not assigned to you'}), 404
    
    # Get student's assigned schools
    schools = [school.to_dict() for school in student.assigned_schools]
    
    # Get student's reports
    reports = [report.to_dict() for report in student.reports]
    
    # Get evaluations for this student by this lecturer
    evaluations = Evaluation.query.filter_by(
        lecturer_id=current_user.id, 
        student_id=student.id
    ).all()
    evaluations = [evaluation.to_dict() for evaluation in evaluations]
    
    return jsonify({
        'student': student.to_dict(),
        'schools': schools,
        'reports': reports,
        'evaluations': evaluations
    }), 200

# Submit evaluation
@lecturer_bp.route('/evaluations', methods=['POST'])
@jwt_required()
def submit_evaluation():
    """Submit an evaluation for a student"""
    current_user = lecturer_required()
    if not current_user:
        return jsonify({'error': 'Lecturer privileges required'}), 403
    
    data = request.get_json()
    
    # Validate the evaluation data
    validation_result = validate_evaluation(data)
    if validation_result['error']:
        return jsonify({'error': validation_result['message']}), 400
    
    # Verify the student is assigned to this lecturer
    student = User.query.get(data['student_id'])
    if not student or student.role != 'student' or current_user not in student.supervisors:
        return jsonify({'error': 'Student not found or not assigned to you'}), 404
    
    # Create a new evaluation
    new_evaluation = Evaluation(
        lecturer_id=current_user.id,
        student_id=data['student_id'],
        visit_date=datetime.strptime(data['visit_date'], '%Y-%m-%d') if isinstance(data['visit_date'], str) else data['visit_date'],
        teaching_skills=data['teaching_skills'],
        classroom_management=data['classroom_management'],
        lesson_preparation=data['lesson_preparation'],
        professionalism=data['professionalism'],
        comments=data.get('comments', ''),
        overall_grade=data['overall_grade']
    )
    
    try:
        db.session.add(new_evaluation)
        db.session.commit()
        return jsonify({
            'message': 'Evaluation submitted successfully',
            'evaluation': new_evaluation.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Get evaluations submitted by the lecturer
@lecturer_bp.route('/evaluations', methods=['GET'])
@jwt_required()
def get_evaluations():
    """Get evaluations submitted by the lecturer"""
    current_user = lecturer_required()
    if not current_user:
        return jsonify({'error': 'Lecturer privileges required'}), 403
    
    # Optional filter by student_id
    student_id = request.args.get('student_id')
    
    query = Evaluation.query.filter_by(lecturer_id=current_user.id)
    
    if student_id:
        query = query.filter_by(student_id=student_id)
    
    evaluations = query.all()
    
    return jsonify({
        'evaluations': [evaluation.to_dict() for evaluation in evaluations]
    }), 200

# Update an evaluation
@lecturer_bp.route('/evaluations/<int:evaluation_id>', methods=['PUT'])
@jwt_required()
def update_evaluation(evaluation_id):
    """Update an existing evaluation"""
    current_user = lecturer_required()
    if not current_user:
        return jsonify({'error': 'Lecturer privileges required'}), 403
    
    evaluation = Evaluation.query.get(evaluation_id)
    if not evaluation or evaluation.lecturer_id != current_user.id:
        return jsonify({'error': 'Evaluation not found or not created by you'}), 404
    
    data = request.get_json()
    
    # Update evaluation attributes
    if 'teaching_skills' in data:
        evaluation.teaching_skills = data['teaching_skills']
    if 'classroom_management' in data:
        evaluation.classroom_management = data['classroom_management']
    if 'lesson_preparation' in data:
        evaluation.lesson_preparation = data['lesson_preparation']
    if 'professionalism' in data:
        evaluation.professionalism = data['professionalism']
    if 'comments' in data:
        evaluation.comments = data['comments']
    if 'overall_grade' in data:
        evaluation.overall_grade = data['overall_grade']
    if 'visit_date' in data:
        evaluation.visit_date = datetime.strptime(data['visit_date'], '%Y-%m-%d') if isinstance(data['visit_date'], str) else data['visit_date']
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Evaluation updated successfully',
            'evaluation': evaluation.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# View student reports
@lecturer_bp.route('/student-reports/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student_reports(student_id):
    """Get reports submitted by a specific student"""
    current_user = lecturer_required()
    if not current_user:
        return jsonify({'error': 'Lecturer privileges required'}), 403
    
    # Verify the student is assigned to this lecturer
    student = User.query.get(student_id)
    if not student or student.role != 'student' or current_user not in student.supervisors:
        return jsonify({'error': 'Student not found or not assigned to you'}), 404
    
    reports = Report.query.filter_by(student_id=student_id).all()
    
    return jsonify({
        'reports': [report.to_dict() for report in reports]
    }), 200

# Dashboard data for lecturer
@lecturer_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_data():
    """Get dashboard data for lecturer"""
    current_user = lecturer_required()
    if not current_user:
        return jsonify({'error': 'Lecturer privileges required'}), 403
    
    # Count of assigned students
    student_count = current_user.supervised_students.count()
    
    # Recent evaluations (last 5)
    recent_evaluations = Evaluation.query.filter_by(lecturer_id=current_user.id)\
        .order_by(Evaluation.submission_date.desc())\
        .limit(5)\
        .all()
    
    # Recent reports from supervised students (last 5)
    student_ids = [student.id for student in current_user.supervised_students]
    recent_reports = Report.query.filter(Report.student_id.in_(student_ids))\
        .order_by(Report.submission_date.desc())\
        .limit(5)\
        .all()
    
    return jsonify({
        'student_count': student_count,
        'recent_evaluations': [evaluation.to_dict() for evaluation in recent_evaluations],
        'recent_reports': [report.to_dict() for report in recent_reports]
    }), 200