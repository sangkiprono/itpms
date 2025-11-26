from backend.models import User, School
import re
from datetime import datetime

def validate_user_update(data):
    """
    Validate user update data
    
    Args:
        data (dict): User update data
    
    Returns:
        dict: Validation result with error flag and message
    """
    if not data:
        return {'error': True, 'message': 'No data provided'}
    
    # Email validation
    if 'email' in data and data['email']:
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', data['email']):
            return {'error': True, 'message': 'Invalid email format'}
    
    # Empty fields validation
    if 'first_name' in data and not data['first_name']:
        return {'error': True, 'message': 'First name cannot be empty'}
    
    if 'last_name' in data and not data['last_name']:
        return {'error': True, 'message': 'Last name cannot be empty'}
    
    return {'error': False, 'message': 'Data is valid'}


def validate_school(data):
    """
    Validate school data
    
    Args:
        data (dict): School data
    
    Returns:
        dict: Validation result with error flag and message
    """
    if not data:
        return {'error': True, 'message': 'No data provided'}
    
    required_fields = ['name', 'address', 'city', 'state']
    for field in required_fields:
        if field not in data or not data[field]:
            return {'error': True, 'message': f'{field} is required'}
    
    # Name validation (check if exists)
    if School.query.filter_by(name=data['name']).first():
        return {'error': True, 'message': 'School with this name already exists'}
    
    # Email validation if provided
    if 'contact_email' in data and data['contact_email']:
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', data['contact_email']):
            return {'error': True, 'message': 'Invalid contact email format'}
    
    # Phone validation if provided
    if 'contact_phone' in data and data['contact_phone']:
        if not re.match(r'^\+?[0-9]{10,15}$', data['contact_phone']):
            return {'error': True, 'message': 'Invalid phone number format'}
    
    return {'error': False, 'message': 'Data is valid'}


def validate_teaching_session(data):
    """
    Validate teaching practice session data
    
    Args:
        data (dict): Teaching practice session data
    
    Returns:
        dict: Validation result with error flag and message
    """
    if not data:
        return {'error': True, 'message': 'No data provided'}
    
    required_fields = ['title', 'start_date', 'end_date']
    for field in required_fields:
        if field not in data or not data[field]:
            return {'error': True, 'message': f'{field} is required'}
    
    # Convert string dates to datetime if needed
    if isinstance(data['start_date'], str):
        try:
            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
        except ValueError:
            return {'error': True, 'message': 'Invalid start date format, use YYYY-MM-DD'}
    else:
        start_date = data['start_date']
    
    if isinstance(data['end_date'], str):
        try:
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')
        except ValueError:
            return {'error': True, 'message': 'Invalid end date format, use YYYY-MM-DD'}
    else:
        end_date = data['end_date']
    
    # Date validation
    if end_date <= start_date:
        return {'error': True, 'message': 'End date must be after start date'}
    
    # Status validation if provided
    if 'status' in data:
        valid_statuses = ['upcoming', 'ongoing', 'completed']
        if data['status'] not in valid_statuses:
            return {'error': True, 'message': f'Status must be one of: {", ".join(valid_statuses)}'}
    
    return {'error': False, 'message': 'Data is valid'}