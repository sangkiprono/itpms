from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models import User, Report, Evaluation, db
from services.student_service import validate_report
import os
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime

student_bp = Blueprint('student', __name__)

# Helper function to check student privileges
def student_required():
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or current_user.role != 'student':
        return None
    
    return current_user

# Helper function to check if file extension is allowed
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

# Get assigned schools
@student_bp.route('/schools', methods=['GET'])
@jwt_required()
def get_assigned_schools():
    """Get schools assigned to the student"""
    current_user = student_required()
    if not current_user:
        return jsonify({'error': 'Student privileges required'}), 403
    
    schools = current_user.assigned_schools
    
    return jsonify({
        'schools': [school.to_dict() for school in schools]
    }), 200

# Get assigned lecturers
@student_bp.route('/supervisors', methods=['GET'])
@jwt_required()
def get_supervisors():
    """Get lecturers supervising the student"""
    current_user = student_required()
    if not current_user:
        return jsonify({'error': 'Student privileges required'}), 403
    
    supervisors = current_user.supervisors
    
    return jsonify({
        'supervisors': [supervisor.to_dict() for supervisor in supervisors]
    }), 200

# Submit a report
@student_bp.route('/reports', methods=['POST'])
@jwt_required()
def submit_report():
    """Submit a new report"""
    current_user = student_required()
    if not current_user:
        return jsonify({'error': 'Student privileges required'}), 403
    
    # Check if the request contains form data or JSON
    if request.content_type and 'multipart/form-data' in request.content_type:
        # Handle form data with file upload
        title = request.form.get('title')
        content = request.form.get('content')
        report_type = request.form.get('report_type')
        
        # Validate data
        data = {'title': title, 'content': content, 'report_type': report_type}
        validation_result = validate_report(data)
        if validation_result['error']:
            return jsonify({'error': validation_result['message']}), 400
        
        file_path = None
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                # Generate a unique filename
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                
                # Ensure upload folder exists
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                # Save the file
                file.save(file_path)
    else:
        # Handle JSON data
        data = request.get_json()
        
        # Validate the report data
        validation_result = validate_report(data)
        if validation_result['error']:
            return jsonify({'error': validation_result['message']}), 400
        
        title = data['title']
        content = data['content']
        report_type = data['report_type']
        file_path = None
    
    # Create a new report
    new_report = Report(
        student_id=current_user.id,
        title=title,
        content=content,
        report_type=report_type,
        file_path=file_path
    )
    
    try:
        db.session.add(new_report)
        db.session.commit()
        return jsonify({
            'message': 'Report submitted successfully',
            'report': new_report.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Get student's reports
@student_bp.route('/reports', methods=['GET'])
@jwt_required()
def get_reports():
    """Get reports submitted by the student"""
    current_user = student_required()
    if not current_user:
        return jsonify({'error': 'Student privileges required'}), 403
    
    # Optional filter by report_type
    report_type = request.args.get('report_type')
    
    query = Report.query.filter_by(student_id=current_user.id)
    
    if report_type:
        query = query.filter_by(report_type=report_type)
    
    reports = query.order_by(Report.submission_date.desc()).all()
    
    return jsonify({
        'reports': [report.to_dict() for report in reports]
    }), 200

# Get evaluations for the student
@student_bp.route('/evaluations', methods=['GET'])
@jwt_required()
def get_evaluations():
    """Get evaluations submitted for the student"""
    current_user = student_required()
    if not current_user:
        return jsonify({'error': 'Student privileges required'}), 403
    
    evaluations = Evaluation.query.filter_by(student_id=current_user.id).all()
    
    # Include lecturer information for each evaluation
    evaluation_data = []
    for evaluation in evaluations:
        eval_dict = evaluation.to_dict()
        lecturer = User.query.get(evaluation.lecturer_id)
        eval_dict['lecturer'] = {
            'id': lecturer.id,
            'first_name': lecturer.first_name,
            'last_name': lecturer.last_name
        }
        evaluation_data.append(eval_dict)
    
    return jsonify({
        'evaluations': evaluation_data
    }), 200

# Update a report
@student_bp.route('/reports/<int:report_id>', methods=['PUT'])
@jwt_required()
def update_report(report_id):
    """Update an existing report"""
    current_user = student_required()
    if not current_user:
        return jsonify({'error': 'Student privileges required'}), 403
    
    report = Report.query.get(report_id)
    if not report or report.student_id != current_user.id:
        return jsonify({'error': 'Report not found or not created by you'}), 404
    
    # Check if the request contains form data or JSON
    if request.content_type and 'multipart/form-data' in request.content_type:
        # Handle form data with file upload
        if 'title' in request.form:
            report.title = request.form.get('title')
        if 'content' in request.form:
            report.content = request.form.get('content')
        if 'report_type' in request.form:
            report.report_type = request.form.get('report_type')
        
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                # Remove old file if it exists
                if report.file_path and os.path.exists(report.file_path):
                    os.remove(report.file_path)
                
                # Generate a unique filename
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                
                # Ensure upload folder exists
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                # Save the file
                file.save(file_path)
                report.file_path = file_path
    else:
        # Handle JSON data
        data = request.get_json()
        
        if 'title' in data:
            report.title = data['title']
        if 'content' in data:
            report.content = data['content']
        if 'report_type' in data:
            report.report_type = data['report_type']
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Report updated successfully',
            'report': report.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Dashboard data for student
@student_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_data():
    """Get dashboard data for student"""
    current_user = student_required()
    if not current_user:
        return jsonify({'error': 'Student privileges required'}), 403
    
    # Count of reports by type
    report_counts = {}
    report_types = db.session.query(Report.report_type).filter_by(student_id=current_user.id).distinct().all()
    for report_type in report_types:
        count = Report.query.filter_by(student_id=current_user.id, report_type=report_type[0]).count()
        report_counts[report_type[0]] = count
    
    # Recent evaluations (last 5)
    recent_evaluations = Evaluation.query.filter_by(student_id=current_user.id)\
        .order_by(Evaluation.submission_date.desc())\
        .limit(5)\
        .all()
    
    # Get supervisor names
    supervisors = [f"{supervisor.first_name} {supervisor.last_name}" for supervisor in current_user.supervisors]
    
    # Get school names
    schools = [school.name for school in current_user.assigned_schools]
    
    return jsonify({
        'report_counts': report_counts,
        'recent_evaluations': [evaluation.to_dict() for evaluation in recent_evaluations],
        'supervisors': supervisors,
        'schools': schools
    }), 200