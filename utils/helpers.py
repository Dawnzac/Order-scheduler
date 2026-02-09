from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta


def calculate_next_execution_time(current_time, recurrence_type):
    if recurrence_type == 'minutely':
        return current_time + timedelta(minutes=1)
    if recurrence_type == 'daily':
        return current_time + timedelta(days=1)
    elif recurrence_type == 'weekly':
        return current_time + timedelta(weeks=1)
    elif recurrence_type == 'monthly':
        return current_time + relativedelta(months=1)
    return None


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
