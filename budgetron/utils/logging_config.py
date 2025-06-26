import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging(app=None):
    log_dir = os.path.join(os.getcwd(), 'logs')
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, 'app.log')

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # File logging configuration
    file_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024 * 5, backupCount=3)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # Console logging configuration
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.DEBUG)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)

    if app:
        app.logger.handlers = []
        app.logger.propagate = False
        app.logger.setLevel(logging.DEBUG)
        app.logger.addHandler(file_handler)
        app.logger.addHandler(stream_handler)