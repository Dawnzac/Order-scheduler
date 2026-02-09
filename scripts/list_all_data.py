import sys
from pathlib import Path
import os

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app, db
from models import User, ScheduledOrder

app = create_app('development')

with app.app_context():
    # List all users
    print("=== ALL USERS ===")
    users = User.query.all()
    for user in users:
        print(f"ID: {user.id}, Email: {user.email}, Name: {user.name}")
    
    # List all orders
    print("\n=== ALL ORDERS ===")
    orders = ScheduledOrder.query.all()
    for order in orders:
        print(f"ID: {order.id}")
        print(f"  User ID: {order.user_id}")
        print(f"  Item ID: {order.item_id}")
        print(f"  Scheduled: {order.scheduled_time}")
        print(f"  Status: {order.status}")
        print()
