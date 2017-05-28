import logging

from .compat import dictConfig


def setup_loghandlers(level=None):
    # Setup logging for sms_engine if not already configured
    logger = logging.getLogger('sms_engine')
    if not logger.handlers:
        dictConfig({
            "version": 1,
            "disable_existing_loggers": False,

            "formatters": {
                "sms_engine": {
                    "format": "[%(levelname)s]%(asctime)s PID %(process)d: %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            },

            "handlers": {
                "sms_engine": {
                    "level": "DEBUG",
                    "class": "logging.StreamHandler",
                    "formatter": "sms_engine"
                },
            },

            "loggers": {
                "sms_engine": {
                    "handlers": ["sms_engine"],
                    "level": level or "DEBUG"
                }
            }
        })
    return logger
