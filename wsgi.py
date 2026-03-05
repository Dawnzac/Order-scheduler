"""
Flask application entry point
"""

import os
from app import create_app, celery_app
from utils.logger import log_info

app = create_app(os.environ.get('FLASK_ENV', 'development'))

celery = celery_app


if __name__ == '__main__':
    log_info("Starting Order Scheduler Server")
    app.run(debug=True, host='0.0.0.0', port=5000)
