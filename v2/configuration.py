#!/usr/bin/env python

import json

from env import *

LOGGER = logger.get_logger()


class ClonerConfiguration:
    def __init__(self, path):
        if path:
            self.configuration_file = os.path.join(path, CONFIGURATION_CLONER_FILENAME)
        else:
            self.configuration_file = CONFIGURATION_CLONER_FULLPATH
        LOGGER.debug("ClonerConfiguration: %s.", self.configuration_file)

    def load(self):
        # type: () -> object
        with open(self.configuration_file) as f:
            return json.loads(f.read())


class ClonerServiceConfiguration:
    def __init__(self, path):
        if path:
            self.configuration_file = os.path.join(path, CONFIGURATION_CLONER_SERVICE_FILENAME)
        else:
            self.configuration_file = CONFIGURATION_CLONER_SERVICE_FULLPATH
        LOGGER.debug("ClonerServiceConfiguration: %s.", self.configuration_file)

    def load(self):
        # type: () -> object
        with open(self.configuration_file) as f:
            return json.loads(f.read())
