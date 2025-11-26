from backend.models import User
import re

def validate_login(data):
    """
    Validate login data
    
    Args:
        data (dict): Login data containing username and password
    
    Returns:
        dict: Validation result with error flag and message
    """
    if not data:
        return {'error': True, 'message': 'No data provided'}
    
    if 'username' not in data or not data['username']:
        return {'error': True, 'message': 'Username is required'}
    
    if 'password' not in data or not data['password']:
        return {'error': True, 'message': 'Password is required'}
    
    return {'error': False, 'message': 'Data is valid'}

def validate_registration(data):
    """
    Validate user registration data
    
    Args:
        data (dict): Registration data
    
    Returns:
        dict: Validation result with error flag and message
    """
    if not data:
        return {'error': True, 'message': 'No data provided'}
    
    required_fields = ['username', 'password', 'email', 'first_name', 'last_name', 'role']
    for field in required_fields:
        if field not in data or not data[field]:
            return {'error': True, 'message': f'{field} is required'}
    
    # Username validation
    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', data['username']):
        return {'error': True, 'message': 'Username must be 3-20 characters and contain only letters, numbers, and underscores'}
    
    # Check if username already exists
    if User.query.filter_by(username=data['username']).first():
        return {'error': True, 'message': 'Username already exists'}
    
    # Email validation
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', data['email']):
        return {'error': True, 'message': 'Invalid email format'}
    
    # Check if email already exists
    if User.query.filter_by(email=data['email']).first():
        return {'error': True, 'message': 'Email already exists'}
    
    # Password validation
    if len(data['password']) < 6:
        return {'error': True, 'message': 'Password must be at least 6 characters long'}
    
    # Role validation
    valid_roles = ['admin', 'lecturer', 'student']
    if data['role'] not in valid_roles:
        return {'error': True, 'message': f'Role must be one of: {", ".join(valid_roles)}'}
        
    return {'error': False, 'message': 'Data is valid'}