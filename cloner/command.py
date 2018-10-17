#!/usr/bin/env python
import atexit
import os
import shlex
import signal
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

    def __init__(self, command, shell=False):
        if not command:
            raise Exception("Command is empty !")
        if type(command) == str:
            self.command = shlex.split(command)
        else:
            self.command = command
        LOGGER.debug("Execute: %s.", command)
        self.shell = shell

    def execute(self):
        try:
            self._process = Popen(self.command, stdout=PIPE, stderr=PIPE, shell=self.shell, preexec_fn=os.setsid)
            _processes.append(self._process)
            result = self._process.communicate()
            self.return_code = self._process.returncode
            self.stdout = result[0]
            self.stderr = result[1]
            return self
        except OSError as e:
            LOGGER.exception("OSError[while execute %s]: %s.", self.command.split(' ')[0], e)
            raise e
        except Exception as e:
            LOGGER.exception("Exception[while execute %s]: %s.", self.command.split(' ')[0], e)
            raise e

    def interrupt(self):
        if self.shell:
            group_pid = os.getpgid(self._process.pid)
            LOGGER.debug("Try to kill group %d.", group_pid)
            return os.killpg(group_pid, signal.SIGTERM)

        LOGGER.debug("Try to kill process %d.", self._process.pid)
        return self._process.kill()
