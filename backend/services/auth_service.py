# auth_service.py
from flask import jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from backend.models import User, db

def validate_login(username, password):
    """
    Validate user login credentials using username
    """
    user = User.query.filter_by(username=username).first()
    
    # Use the check_password method instead of directly accessing password attribute
    if user and user.check_password(password):
        return True, user
    return False, None

def validate_registration(email, password, username):
    """
    Validate and register a new user
    """
    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return False, "Email already registered"
    
    # Also check if username already exists
    existing_username = User.query.filter_by(username=username).first()
    if existing_username:
        return False, "Username already taken"
    
    # Create new user - don't set password in constructor
    new_user = User(
        email=email,
        username=username
    )
    
    # Set password using the method
    new_user.set_password(password)
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return True, new_user
    except Exception as e:
        db.session.rollback()
        return False, str(e)