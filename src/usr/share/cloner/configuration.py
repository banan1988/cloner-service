#!/usr/bin/env python
import json
import os

from env import CONFIGURATION_CLONER_FILENAME, CONFIGURATION_CLONER_FULLPATH, CONFIGURATION_CLONER_SERVICE_FULLPATH, \
    CONFIGURATION_CLONER_SERVICE_FILENAME

__all__ = ["ClonerConfiguration"]

__version__ = "0.1"


class ClonerConfiguration:
    def __init__(self, path):
        if path:
            self.configuration_file = os.path.join(path, CONFIGURATION_CLONER_FILENAME)
        else:
            self.configuration_file = CONFIGURATION_CLONER_FULLPATH
        print("ClonerConfiguration: %s" % self.configuration_file)

    def load(self):
        with open(self.configuration_file) as f:
            return json.loads(f.read())


class ClonerServiceConfiguration:
    def __init__(self, path):
        if path:
            self.configuration_file = os.path.join(path, CONFIGURATION_CLONER_SERVICE_FILENAME)
        else:
            self.configuration_file = CONFIGURATION_CLONER_SERVICE_FULLPATH
        print("ClonerServiceConfiguration: %s" % self.configuration_file)

    def load(self):
        with open(self.configuration_file) as f:
            return json.loads(f.read())
