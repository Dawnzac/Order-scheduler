from datetime import datetime, timedelta
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app, db
from models import User, ScheduledOrder, OrderStatus

app = create_app('development')

with app.app_context():
   
    user = User.query.first()
    if not user:
        user = User(email='test@example.com', name='Test User', password_hash='test123')
        db.session.add(user)
        db.session.commit()
        print('Created test user:', user.id)
    else:
        print('Using existing user:', user.id)

    # Create a scheduled order 2 minutes from now
    scheduled_time = datetime.now() + timedelta(minutes=2)
    order = ScheduledOrder(
        user_id=user.id,
        item_id=1,
        quantity=1,
        scheduled_time=scheduled_time,
        recurrence_type='once',
        status=OrderStatus.PENDING.value
    )
    db.session.add(order)
    db.session.commit()
    print('Created test order:', order.id)
    print('Scheduled time (local):', order.scheduled_time)
