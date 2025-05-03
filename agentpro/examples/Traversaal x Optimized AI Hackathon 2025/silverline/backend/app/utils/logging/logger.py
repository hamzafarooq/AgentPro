import os
import logging
from config import CONFIG
from logging.config import dictConfig

# Ensure logs directory exists
LOG_DIRECTORY = "logs"
os.makedirs(LOG_DIRECTORY, exist_ok=True)

# Logging configuration
log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "app.utils.logging.log_handler.JsonFormatter",  # JSON logs for Grafana Loki
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "app.utils.logging.log_handler.CustomTimedRotatingFileHandler",
            "formatter": "json",
            "filename": os.path.join(LOG_DIRECTORY, "today.log"),
            "when": "midnight",
            "backupCount": 7,
            "encoding": "utf-8",
        },
    },
    "loggers": {
        f"{CONFIG.app_name}": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

# Configure logging
dictConfig(log_config)

# Define a logger
LOG = logging.getLogger(f"{CONFIG.app_name}")


# Custom logger adapter to add context dynamically
class ContextLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        # Merge extra data from adapter and log message
        extra = self.extra.copy()
        if "extra" in kwargs:
            extra.update(kwargs["extra"])
        kwargs["extra"] = extra
        return msg, kwargs

def get_logger(**kwargs):
    extra = kwargs
    return ContextLoggerAdapter(LOG, extra)


# Test logging
LOG.info(f"{CONFIG.app_name} logger initialized")
