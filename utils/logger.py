import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def log_info(message):
    logger.info(f"[INFO] {datetime.utcnow().isoformat()} - {message}")


def log_error(message, error=None):
    if error:
        logger.error(f"[ERROR] {datetime.utcnow().isoformat()} - {message}: {str(error)}")
    else:
        logger.error(f"[ERROR] {datetime.utcnow().isoformat()} - {message}")


def log_warning(message):
    logger.warning(f"[WARN] {datetime.utcnow().isoformat()} - {message}")


def log_debug(message):
    import os
    if os.environ.get('FLASK_ENV') == 'development':
        logger.debug(f"[DEBUG] {datetime.utcnow().isoformat()} - {message}")
