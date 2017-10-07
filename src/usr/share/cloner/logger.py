import json
import logging
import logging.config
import os

LOGGER_CONFIG_FULLPATH = os.getenv("LOGGER_CONFIG_FULLPATH", "logger.json")
LOGGER_DEFAULT_LEVEL = os.getenv("LOGGER_DEFAULT_LEVEL", logging.DEBUG)


def _setup(path=LOGGER_CONFIG_FULLPATH, default_level=LOGGER_DEFAULT_LEVEL):
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


def get_logger(name=None, path=LOGGER_CONFIG_FULLPATH, default_level=LOGGER_DEFAULT_LEVEL):
    _setup(path, default_level)
    return logging.getLogger(name)
