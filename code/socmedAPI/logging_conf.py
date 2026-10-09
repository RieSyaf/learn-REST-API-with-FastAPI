import logging

from logging.config import dictConfig

from socmedAPI.config import DevConfig, config

def obfuscared(email: str, obfuscated_length: int) -> str:
    characters = email[:obfuscated_length]
    first, last = email.split("@")
    return characters + "*" * (len(first) - obfuscated_length) + "@" + last


class EmaailObfuscatingFilter(logging.Filter):
    def __init__(self, name: str = "", obfuscated_length: int = 3) -> None:
        super().__init__(name)
        self.obfuscated_length = obfuscated_length

    def filter(self, record: logging.LogRecord) -> bool:
        if "email" in record.__dict__:
            record.email = obfuscared(record.email, self.obfuscated_length)
        return True


def configure_logging() -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                "correlation_id": {
                    "()": "asgi_correlation_id.CorrelationIdFilter",
                    "uuid_length": 8 if isinstance(config, DevConfig) else 32,
                    "default_value": "-",
                },
                "email_obfuscator": {
                    "()": EmaailObfuscatingFilter,
                    "obfuscated_length": 3 if isinstance(config, DevConfig) else 0,
                },
            },
            "formatters": {
                "console": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                    "format": "(%(correlation_id)s) %(name)s:%(lineno)d - %(message)s",
                },
                "file": {
                    "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                    "format": "%(correlation_id)s %(asctime)s  %(name)s:%(lineno)d  %(levelname)-8s  %(message)s",
                }
            },
            "handlers": {
                "default": {
                    "class": "rich.logging.RichHandler",
                    "formatter": "console",
                    "level": "DEBUG",
                    "filters": ["correlation_id", "email_obfuscator"]
                },
                "rotating_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": "socmedAPI.log",
                    "formatter": "file",
                    "level": "DEBUG",
                    "maxBytes": 1024 * 1024 * 5,  # 5 MB
                    "backupCount": 5,
                    "encoding": "utf8",
                    "filters": ["correlation_id", "email_obfuscator"]
                }
            },
            "loggers": {
                "uvicorn": {"handlers": ["default", "rotating_file"], "level": "INFO"},
                "socmedAPI": {
                    "handlers": ["default", "rotating_file"],
                    "level": "DEBUG" if isinstance(config, DevConfig) else "INFO",
                    "propagate": False,
                },
                "databases": {"handlers": ["default"], "level": "WARNING"},
                "aiosqlite": {"handlers": ["default"], "level": "WARNING"}
            }
        }
    )