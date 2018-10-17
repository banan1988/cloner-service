#!/usr/bin/env python

import os

import logger

LOGGER = logger.get_logger()

BASEDIR = os.path.dirname(os.path.realpath(__file__))
LOGGER.debug("BASEDIR: %s" % BASEDIR)

# GO_REPLAY_PATH = os.getenv("GO_REPLAY_PATH", "/usr/local/bin")
GO_REPLAY_PATH = os.getenv("GO_REPLAY_PATH", "../../local/bin")
GO_REPLAY_FILENAME = "goreplay"
GO_REPLAY_FULLPATH = os.path.join(GO_REPLAY_PATH, GO_REPLAY_FILENAME)

LOGGER.debug("GO_REPLAY_PATH: %s", GO_REPLAY_PATH)
LOGGER.debug("GO_REPLAY_FILENAME: %s", GO_REPLAY_FILENAME)
LOGGER.debug("GO_REPLAY_FULLPATH: %s", GO_REPLAY_FULLPATH)

CONFIGURATION_PATH = os.getenv("CONFIGURATION_PATH", "/etc/cloner")
CONFIGURATION_CLONER_FILENAME = "cloner.json"
CONFIGURATION_CLONER_FULLPATH = os.path.join(CONFIGURATION_PATH, CONFIGURATION_CLONER_FILENAME)
CONFIGURATION_CLONER_SERVICE_FILENAME = "cloner-service.json"
CONFIGURATION_CLONER_SERVICE_FULLPATH = os.path.join(CONFIGURATION_PATH, CONFIGURATION_CLONER_SERVICE_FILENAME)

LOGGER.debug("CONFIGURATION_PATH: %s", CONFIGURATION_PATH)
LOGGER.debug("CONFIGURATION_CLONER_FILENAME: %s", CONFIGURATION_CLONER_FILENAME)
LOGGER.debug("CONFIGURATION_CLONER_FULLPATH: %s", CONFIGURATION_CLONER_FULLPATH)
LOGGER.debug("CONFIGURATION_CLONER_SERVICE_FILENAME: %s", CONFIGURATION_CLONER_SERVICE_FILENAME)
LOGGER.debug("CONFIGURATION_CLONER_SERVICE_FULLPATH: %s", CONFIGURATION_CLONER_SERVICE_FULLPATH)

CLONER_SERVICE_BIND_ADDRESS = os.getenv("BIND_ADDRESS", "127.0.0.1:8888")
CLONER_SERVICE_CHECK_CONFIGURATION = os.getenv("CHECK_CONFIGURATION", 30)

LOGGER.debug("CLONER_SERVICE_BIND_ADDRESS: %s", CLONER_SERVICE_BIND_ADDRESS)
LOGGER.debug("CLONER_SERVICE_CHECK_CONFIGURATION: %s", CLONER_SERVICE_CHECK_CONFIGURATION)
