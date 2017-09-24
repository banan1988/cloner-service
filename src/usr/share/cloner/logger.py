import json
import logging
import logging.config
import os

__all__ = ["Logger"]

__version__ = "0.1"

LOGGER_CONFIG_PATH = os.getenv("LOGGER_CONFIG_PATH", "logger.json")
LOGGER_DEFAULT_LEVEL = os.getenv("LOGGER_DEFAULT_LEVEL", logging.DEBUG)


def _setup(path=LOGGER_CONFIG_PATH, default_level=LOGGER_DEFAULT_LEVEL):
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


def get_logger(name=None, path=LOGGER_CONFIG_PATH, default_level=LOGGER_DEFAULT_LEVEL):
    _setup(path, default_level)
    return logging.getLogger(name)
