#!/usr/bin/env python
import argparse
import threading

from command import *
from configuration import ClonerConfiguration
from env import CONFIGURATION_PATH
from goreplay import GoReplayCommand

__all__ = ["Cloner"]

__version__ = "0.1"


class ClonerThread(threading.Thread):
    command = None

    def __init__(self, gor_command):
        threading.Thread.__init__(self)
        self.setName("ClonerThread")
        self.setDaemon(True)
        self.gor_command = gor_command

    def run(self):
        try:
            print("Start cloner thread")
            self.command = Command(self.gor_command)
            return self.command.execute()
        finally:
            print("Stop cloner thread")

    def interrupt(self):
        if self.is_alive():
            self.command.interrupt()


class Cloner:
    thread = None

    def __init__(self, configuration):
        self.gor_command = GoReplayCommand(configuration).build()

    def start(self):
        self.thread = ClonerThread(self.gor_command)
        self.thread.start()
        self.thread.join()

    def stop(self):
        if self.thread:
            self.thread.interrupt()

    def version_gor(self):
        result = Command(self.gor_command).execute()
        return result.stdout.strip().split(" ")[1]

    def help_gor(self):
        result = Command(" ".join([self.gor_command, "-h"])).execute()
        return result.stderr.strip()


def get_args():
    parser = argparse.ArgumentParser(
        description='Cloner',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--version-gor', action='store_true')
    parser.add_argument('--help-gor', action='store_true')
    parser.add_argument('--configuration-path', type=str,
                        required=False,
                        default=CONFIGURATION_PATH,
                        help='Path to cloner\'s configuration.')
    return parser.parse_args()


if __name__ == '__main__':
    CLONER = None
    ARGS = get_args()
    print(ARGS)

    try:
        if ARGS.version_gor:
            result = Cloner().version_gor()
        elif ARGS.help_gor:
            result = Cloner().help_gor()
        else:
            configuration = ClonerConfiguration(ARGS.configuration_path).load()
            CLONER = Cloner(configuration)
            CLONER.start()

        print(result)
    except SystemExit:
        print('System exit')
        pass
    except KeyboardInterrupt:
        print('Keyboard interrupt')
        pass
    except Exception as e:
        raise e
    finally:
        if CLONER:
            CLONER.stop()
