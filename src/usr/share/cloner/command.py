#!/usr/bin/env python
import atexit
import shlex
from subprocess import Popen, PIPE

import logger

LOGGER = logger.get_logger()

_processes = []


@atexit.register
def _kill_processes():
    for process in _processes:
        try:
            LOGGER.debug("Try to kill process %d.", process.pid)
            process.kill()
            LOGGER.debug("Successfully killed process %d with exit code %d.", process.pid, process.returncode)
        except OSError as e:
            if process.returncode >= 0:
                LOGGER.debug("Process %d is already killed.", process.pid)
            else:
                LOGGER.exception("Couldn't kill process %d: %s.", process.pid, e)


class Command:
    _process = None
    return_code = 0
    stdout = None
    stderr = None

    def __init__(self, command):
        LOGGER.debug("Execute: %s.", command)

        if not command:
            raise Exception("Command is empty !")
        if type(command) == str:
            self.command = shlex.split(command)
        else:
            self.command = command

    def execute(self):
        try:
            self._process = Popen(self.command, stdout=PIPE, stderr=PIPE, shell=False)
            _processes.append(self._process)
            result = self._process.communicate()
            self.return_code = self._process.returncode
            self.stdout = result[0]
            self.stderr = result[1]
            return self
        except Exception as e:
            LOGGER.exception("Exception: %s.", e)
            raise e

    def interrupt(self):
        self._process.kill()
