#!/usr/bin/env python
import atexit
import shlex

from subprocess import Popen, PIPE

__version__ = "0.1"

__all__ = ["Command"]

subprocesses = []


@atexit.register
def _kill_subprocesses():
    for proc in subprocesses:
        try:
            print("Try to kill process %d." % proc.pid)
            proc.kill()
            print("Successfully killed process %d with exit code %d." % (proc.pid, proc.returncode))
        except OSError as e:
            if proc.returncode >= 0:
                print("Process %d is already killed." % proc.pid)
            else:
                print("Couldn't kill process %d - %s" % (proc.pid, e))


class Command:
    _proc = None
    return_code = 0
    stdout = None
    stderr = None

    def __init__(self, command):
        print("execute", command)
        if not command:
            raise Exception("command is empty")
        if type(command) == str:
            self.command = shlex.split(command)
        else:
            self.command = command

    def execute(self):
        try:
            self._proc = Popen(self.command, stdout=PIPE, stderr=PIPE, shell=False)
            subprocesses.append(self._proc)
            result = self._proc.communicate()
            self.return_code = self._proc.returncode
            self.stdout = result[0]
            self.stderr = result[1]
            return self
        except Exception as e:
            raise e

    def interrupt(self):
        self._proc.kill()
