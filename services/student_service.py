def validate_report(data):
    """
    Validate report data submitted by students
    
    Args:
        data (dict): Report data
    
    Returns:
        dict: Validation result with error flag and message
    """
    if not data:
        return {'error': True, 'message': 'No data provided'}
    
    required_fields = ['title', 'content', 'report_type']
    for field in required_fields:
        if field not in data or not data[field]:
            return {'error': True, 'message': f'{field} is required'}
    
    # Title length validation
    if len(data['title']) < 5 or len(data['title']) > 100:
        return {'error': True, 'message': 'Title must be between 5 and 100 characters'}
    
    # Content length validation
    if len(data['content']) < 10:
        return {'error': True, 'message': 'Content must be at least 10 characters'}
    
    # Report type validation
    valid_types = ['daily', 'weekly', 'lesson_plan', 'reflection', 'final']
    if data['report_type'] not in valid_types:
        return {'error': True, 'message': f'Report type must be one of: {", ".join(valid_types)}'}
    
    return {'error': False, 'message': 'Data is valid'}