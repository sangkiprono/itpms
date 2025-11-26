import os
from datetime import datetime
from flask import current_app
import uuid
from werkzeug.utils import secure_filename

def allowed_file(filename):
    """
    Check if the file extension is allowed
    
    Args:
        filename (str): The name of the file
        
    Returns:
        bool: True if the extension is allowed, False otherwise
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_file(file, folder='uploads'):
    """
    Save a file to the specified folder
    
    Args:
        file: The file object from request.files
        folder (str): The folder to save the file in (default: 'uploads')
        
    Returns:
        str: The path to the saved file, or None if saving failed
    """
    if file and allowed_file(file.filename):
        # Generate a unique filename to prevent overwrites
        original_filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{original_filename}"
        
        # Create the full path
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, unique_filename)
        
        # Save the file
        try:
            file.save(file_path)
            return file_path
        except Exception as e:
            current_app.logger.error(f"Error saving file: {str(e)}")
            return None
    
    return None

def format_date(date_obj):
    """
    Format a date object as a string
    
    Args:
        date_obj (datetime): The date to format
        
    Returns:
        str: The formatted date string
    """
    if isinstance(date_obj, datetime):
        return date_obj.strftime('%Y-%m-%d')
    return str(date_obj)

def calculate_overall_rating(evaluation):
    """
    Calculate the overall numeric rating from an evaluation
    
    Args:
        evaluation (dict): The evaluation data
        
    Returns:
        float: The overall rating
    """
    ratings = [
        evaluation.get('teaching_skills', 0),
        evaluation.get('classroom_management', 0),
        evaluation.get('lesson_preparation', 0),
        evaluation.get('professionalism', 0)
    ]
    
    # Calculate average, avoid division by zero
    return sum(ratings) / len(ratings) if ratings else 0

def grade_to_numeric(grade):
    """
    Convert letter grade to numeric value
    
    Args:
        grade (str): The letter grade (e.g., 'A+', 'B-')
        
    Returns:
        float: The numeric value
    """
    grade_map = {
        'A+': 4.0, 'A': 4.0, 'A-': 3.7,
        'B+': 3.3, 'B': 3.0, 'B-': 2.7,
        'C+': 2.3, 'C': 2.0, 'C-': 1.7,
        'D+': 1.3, 'D': 1.0, 'F': 0.0
    }
    
    return grade_map.get(grade, 0.0)