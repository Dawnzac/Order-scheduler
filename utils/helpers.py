from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta


def calculate_next_execution_time(current_time, recurrence_type, recurrence_pattern=None):
    """Calculate next execution time based on recurrence type and pattern"""
    
    if recurrence_type == 'minutely':
        return current_time + timedelta(minutes=1)
    
    elif recurrence_type == 'daily':
        return current_time + timedelta(days=1)
    
    elif recurrence_type == 'weekly':
        # If pattern exists, jump to next occurrence of selected weekday
        if recurrence_pattern and 'days' in recurrence_pattern:
            selected_days = sorted(recurrence_pattern['days'])
            next_time = current_time + timedelta(days=1)
            
            # Keep searching until we find a matching day
            while next_time.weekday() not in selected_days:
                next_time += timedelta(days=1)
            
            return next_time
        else:
            # No pattern: just add 7 days
            return current_time + timedelta(weeks=1)
    
    elif recurrence_type == 'monthly':
        # If pattern exists, jump to next occurrence of selected day of month
        if recurrence_pattern and 'days' in recurrence_pattern:
            selected_days = sorted(recurrence_pattern['days'])
            next_time = current_time + timedelta(days=1)
            
            # Keep searching until we find a matching day of month
            max_iterations = 365  # Prevent infinite loops
            iterations = 0
            while next_time.day not in selected_days and iterations < max_iterations:
                next_time += timedelta(days=1)
                iterations += 1
            
            return next_time
        else:
            # No pattern: add 1 month
            return current_time + relativedelta(months=1)
    
    return None


def should_execute_order(order):
    """Check if an order should execute today based on its recurrence pattern"""
    today = datetime.now(timezone.utc)
    
    # For non-recurring orders, check if we've reached the scheduled time
    if not order.recurrence_type or order.recurrence_type == 'once':
        return order.scheduled_time.date() == today.date()
    
    # For weekly orders with pattern
    if order.recurrence_type == 'weekly':
        if order.recurrence_pattern and 'days' in order.recurrence_pattern:
            return today.weekday() in order.recurrence_pattern['days']
        return True  # Execute every week if no pattern
    
    # For monthly orders with pattern
    if order.recurrence_type == 'monthly':
        if order.recurrence_pattern and 'days' in order.recurrence_pattern:
            return today.day in order.recurrence_pattern['days']
        return True  # Execute every month if no pattern
    
    # For daily/minutely, always execute
    return True


def is_within_recurrence_window(execution_time, recurrence_end):
    if not recurrence_end:
        return True
    return execution_time <= recurrence_end



def format_execution_time(date):
    """Format datetime to readable string"""
    if date is None:
        return None
    if isinstance(date, str):
        date = datetime.fromisoformat(date.replace('Z', '+00:00'))
    if date.tzinfo is None:
        date = date.replace(tzinfo=timezone.utc)
    return date.isoformat()


MOCK_ITEMS = [
    {'id': 1, 'name': 'Pizza Margherita', 'price': 12.99, 'quantity': 1},
    {'id': 2, 'name': 'Burger Deluxe', 'price': 9.99, 'quantity': 1},
    {'id': 3, 'name': 'Pasta Carbonara', 'price': 11.49, 'quantity': 1},
    {'id': 4, 'name': 'Salad Fresh', 'price': 7.99, 'quantity': 1}
]
