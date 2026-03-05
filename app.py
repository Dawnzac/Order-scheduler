import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from celery import Celery
from config import config
import logging

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
celery_app = None

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config_name=None):
    """Application factory"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # Create Celery app first
    create_celery_app(app)
    init_celery(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    logger.info(f'🚀 Flask app initialized with config: {config_name}')
    
    return app


def init_celery(app):
    """Initialize Celery with Flask app"""
    global celery_app
    
    if celery_app is None:
        return
    
    class ContextTask(celery_app.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery_app.Task = ContextTask
    
    logger.info('📦 Celery initialized')


def create_celery_app(app=None):
    """Create Celery app"""
    global celery_app
    
    if app is None:
        app = Flask(__name__)
        app.config.from_object(config['development'])
    
    # Use new-style Celery config names if present
    broker = app.config.get('BROKER_URL') or app.config.get('broker_url')
    backend = app.config.get('RESULT_BACKEND') or app.config.get('result_backend')
    include_modules = app.config.get('IMPORTS') or app.config.get('imports') or ['tasks']

    celery_app = Celery(
        app.import_name,
        broker=broker or 'redis://localhost:6379/0',
        backend=backend or 'redis://localhost:6379/0',
        include=include_modules
    )

    # Convert Flask config (uppercase keys) to Celery config (lowercase keys)
    celery_config = {}
    key_map = {
        'BROKER_URL': 'broker_url',
        'RESULT_BACKEND': 'result_backend',
        'TASK_SERIALIZER': 'task_serializer',
        'ACCEPT_CONTENT': 'accept_content',
        'RESULT_SERIALIZER': 'result_serializer',
        'TIMEZONE': 'timezone',
        'ENABLE_UTC': 'enable_utc',
        'WORKER_POOL': 'worker_pool',
        'TASK_ALWAYS_EAGER': 'task_always_eager',
        'IMPORTS': 'imports',
        'BEAT_SCHEDULE': 'beat_schedule',
    }
    
    for flask_key, celery_key in key_map.items():
        if flask_key in app.config:
            celery_config[celery_key] = app.config[flask_key]
            logger.debug(f'Mapped {flask_key} -> {celery_key}')
    
    celery_app.conf.update(celery_config)
    
    # Log beat schedule loading
    if 'beat_schedule' in celery_config:
        logger.info(f'✅ Beat schedule loaded: {list(celery_config["beat_schedule"].keys())}')
    else:
        logger.warning('⚠️ No beat schedule found in config')
    
    logger.info('✅ Celery app created')
    return celery_app


def register_blueprints(app):
    """Register all blueprints"""
    from routes.auth_routes import auth_bp
    from routes.order_routes import orders_bp
    from routes.log_routes import logs_bp
    from flask import send_from_directory
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(logs_bp)
    
    # Serve frontend
    @app.route('/', methods=['GET'])
    def index():
        return send_from_directory('public', 'index.html')
    
    @app.route('/<path:filename>', methods=['GET'])
    def serve_static(filename):
        if filename and '.' in filename:
            return send_from_directory('public', filename)
        return send_from_directory('public', 'index.html')
    
    # Health check
    @app.route('/health', methods=['GET'])
    def health():
        return {'status': 'OK'}, 200
    
    logger.info('✅ Blueprints registered')
