import logging
from flask import g, request

logger = logging.getLogger(__name__)


def log_event(action: str, user=None, level: str = "info", status: str = "success", details: dict = None):
    """
    Logs a structured event message with optional user, status, and extra details.
    """
    user = user or getattr(g, "user", None)
    username = getattr(user, "username", 'anonymous')

    log_msg = {
        'action': action,
        'method': request.method,
        'path': request.path,
        'username': username,
        'status': status,
        'details': details or {}
    }

    # Dynamic selection of log level
    log_func = getattr(logger, level, logger.info)
    log_func(log_msg)
