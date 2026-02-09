from app import db
from datetime import datetime, timezone
import uuid
from enum import Enum

class User(db.Model):
    """User model"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    orders = db.relationship('ScheduledOrder', backref='user', lazy=True, cascade='all, delete-orphan')
    logs = db.relationship('OrderLog', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class OrderStatus(Enum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'


class RecurrenceType(Enum):
    ONCE = 'once'
    MINUTELY = 'minutely'
    DAILY = 'daily'
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'


class ScheduledOrder(db.Model):
    """Scheduled order model"""
    __tablename__ = 'scheduled_orders'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    item_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    scheduled_time = db.Column(db.DateTime, nullable=False)
    recurrence_type = db.Column(db.String(20), default=RecurrenceType.ONCE.value)
    recurrence_end = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default=OrderStatus.PENDING.value)
    task_id = db.Column(db.String(255), nullable=True)  # Celery task ID
    last_executed_at = db.Column(db.DateTime, nullable=True)
    next_execution_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    logs = db.relationship('OrderLog', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'item_id': self.item_id,
            'quantity': self.quantity,
            'scheduled_time': self.scheduled_time.isoformat(),
            'recurrence_type': self.recurrence_type,
            'recurrence_end': self.recurrence_end.isoformat() if self.recurrence_end else None,
            'status': self.status,
            'task_id': self.task_id,
            'last_executed_at': self.last_executed_at.isoformat() if self.last_executed_at else None,
            'next_execution_at': self.next_execution_at.isoformat() if self.next_execution_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class OrderLog(db.Model):
    """Order execution log model"""
    __tablename__ = 'order_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    order_id = db.Column(db.String(36), db.ForeignKey('scheduled_orders.id'), nullable=False, index=True)
    item_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    details = db.Column(db.JSON, default={})
    executed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'order_id': self.order_id,
            'item_id': self.item_id,
            'quantity': self.quantity,
            'status': self.status,
            'details': self.details,
            'executed_at': self.executed_at.isoformat()
        }
