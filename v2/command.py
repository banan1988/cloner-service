#!/usr/bin/env python

import atexit
import os
import shlex
import signal
import subprocess

import logger

os.environ["PYTHONUNBUFFERED"] = "1"

LOGGER = logger.get_logger()
LOGGER_GOR = logger.get_logger('gor')

_processes = []


@atexit.register
def _kill_processes():
    for process in _processes:
        try:
            LOGGER.debug("Try to kill process %d.", process.pid)
            process.kill()
            LOGGER.debug("Successfully killed process %d with exit code %s.", process.pid, process.returncode)
        except OSError as e:
            if process.returncode >= 0:
                LOGGER.debug("Process %d is already killed.", process.pid)
            else:
                LOGGER.warning("Couldn't kill process %d: %s.", process.pid, e)


class Command:
    _process = None
    exit_code = 0
    stdout = []
    stderr = []

    def __init__(self, command, realtime_output=True, fast_fail=True, shell=False):
        if not command:
            raise Exception("Command is empty !")
        if list == type(command):
            self.command = command
        else:
            self.command = shlex.split(str(command))
        self.realtime_output = realtime_output
        self.fast_fail = fast_fail
        self.shell = shell

    def __str__(self):
        return str({
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr
        })

    def execute(self):
        LOGGER.info("[shell=%s] Execute %s", self.shell, " ".join(self.command))
        try:
            if os.name == 'posix':
                # unix
                LOGGER.debug("UNIX")
                kwargs = {'preexec_fn': os.setsid}
            else:
                # windows
                LOGGER.debug("Windows")
                kwargs = {'creationflags': subprocess.CREATE_NEW_PROCESS_GROUP}

            if self.realtime_output:
                return self._run_realtime_output(kwargs, LOGGER_GOR)
            return self._run(kwargs)
        except OSError as e:
            LOGGER.exception("OSError[while execute %s]: %s.", " ".join(self.command), e)
            raise e
        except Exception as e:
            LOGGER.exception("Exception[while execute %s]: %s.", " ".join(self.command), e)
            raise e

    def _run(self, kwargs):
        self._process = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
        _processes.append(self._process)

        (self.stdout, self.stderr) = self._process.communicate()
        self.exit_code = self._process.returncode
        return self

    def _run_realtime_output(self, kwargs, log):
        self._process = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
        _processes.append(self._process)

        while True:
            stdout = self._process.stdout.readline().strip()
            stderr = self._process.stderr.readline().strip()

            if stdout:
                self.stdout.append(stdout)
                log.info(stdout)
            if stderr:
                self.stderr.append(stderr)
                log.error(stderr)

                if self.fast_fail:
                    LOGGER.info("Fast fail !")
                    self.exit_code = 1
                    return self

            if (stdout == '' or stderr == '') and self._process.poll() is not None:
                break

        self.exit_code = self._process.poll()
        return self

    def interrupt(self):
        if self.shell:
            group_pid = os.getpgid(self._process.pid)
            LOGGER.debug("Try to kill group %d.", group_pid)
            return os.killpg(group_pid, signal.SIGTERM)

        LOGGER.debug("Try to kill process %d.", self._process.pid)
        return self._process.kill()
