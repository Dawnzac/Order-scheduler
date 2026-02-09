import re
from datetime import datetime

def validate_email(email):
    pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """Validate password (minimum 6 characters)"""
    return password and len(password) >= 6


def validate_scheduled_order(data):
    errors = []
    
    if not data.get('item_id'):
        errors.append('item_id is required')
    
    if not data.get('quantity') or data.get('quantity') < 1:
        errors.append('quantity must be at least 1')
    
    if not data.get('scheduled_time'):
        errors.append('scheduled_time is required')
    else:
        try:
            scheduled_time = datetime.fromisoformat(data['scheduled_time'].replace('Z', '+00:00'))
            if scheduled_time <= datetime.utcnow():
                errors.append('scheduled_time must be in the future')
        except (ValueError, AttributeError):
            errors.append('Invalid scheduled_time format')
    
    if data.get('recurrence_end'):
        try:
            recurrence_end = datetime.fromisoformat(data['recurrence_end'].replace('Z', '+00:00'))
            scheduled_time = datetime.fromisoformat(data['scheduled_time'].replace('Z', '+00:00'))
            if recurrence_end <= scheduled_time:
                errors.append('recurrence_end must be after scheduled_time')
        except (ValueError, AttributeError):
            errors.append('Invalid recurrence_end format')
    
    return {'is_valid': len(errors) == 0, 'errors': errors}
