import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'bruuuuuuu-uuuu-uuuu')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET', 'its-a-keyyy-yyy')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    
    # Redis
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0')
    
    # Celery Configuration
    BROKER_URL = os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0')
    RESULT_BACKEND = os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0')
    TASK_SERIALIZER = 'json'
    ACCEPT_CONTENT = ['json']
    RESULT_SERIALIZER = 'json'
    TIMEZONE = 'UTC'
    ENABLE_UTC = True
    WORKER_POOL = 'solo'
    TASK_ALWAYS_EAGER = False
    IMPORTS = ('tasks',)
    
    # Celery Beat Schedule - run order processing every 60 seconds
    BEAT_SCHEDULE = {
        'process-pending-orders': {
            'task': 'tasks.process_pending_orders',
            'schedule': timedelta(seconds=60),
        },
    }
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///turinix.db'
    )
    
    # Notification
    NOTIFICATION_TYPE = os.environ.get('NOTIFICATION_TYPE', 'email') #Options - " console / email "
    SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
    SMTP_USER = os.environ.get('SMTP_USER', 'rykerx066@gmail.com')
    SMTP_PASS = os.environ.get('SMTP_PASS', 'ytgn mwre vmna lpyr')


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
