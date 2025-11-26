from datetime import datetime

def validate_evaluation(data):
    """
    Validate evaluation data submitted by lecturers
    
    Args:
        data (dict): Evaluation data
    
    Returns:
        dict: Validation result with error flag and message
    """
    if not data:
        return {'error': True, 'message': 'No data provided'}
    
    required_fields = [
        'student_id', 
        'visit_date', 
        'teaching_skills', 
        'classroom_management', 
        'lesson_preparation', 
        'professionalism', 
        'overall_grade'
    ]
    
    for field in required_fields:
        if field not in data:
            return {'error': True, 'message': f'{field} is required'}
    
    # Convert string date to datetime if needed
    if isinstance(data['visit_date'], str):
        try:
            visit_date = datetime.strptime(data['visit_date'], '%Y-%m-%d')
        except ValueError:
            return {'error': True, 'message': 'Invalid visit date format, use YYYY-MM-DD'}
    
    # Rating validation (1-10 scale)
    rating_fields = ['teaching_skills', 'classroom_management', 'lesson_preparation', 'professionalism']
    for field in rating_fields:
        try:
            rating = int(data[field])
            if rating < 1 or rating > 10:
                return {'error': True, 'message': f'{field} must be between 1 and 10'}
        except (ValueError, TypeError):
            return {'error': True, 'message': f'{field} must be a number'}
    
    # Grade validation
    valid_grades = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'F']
    if data['overall_grade'] not in valid_grades:
        return {'error': True, 'message': f'Overall grade must be one of: {", ".join(valid_grades)}'}
    
    return {'error': False, 'message': 'Data is valid'}