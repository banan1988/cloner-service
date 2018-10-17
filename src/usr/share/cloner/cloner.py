#!/usr/bin/env python
import argparse
import threading

import logger
from command import Command
from configuration import ClonerConfiguration
from env import CONFIGURATION_PATH
from goreplay import GoReplayCommand

LOGGER = logger.get_logger()


class ClonerThread(threading.Thread):
    command = None

    def __init__(self, gor_command):
        threading.Thread.__init__(self)
        self.setName("ClonerThread")
        self.setDaemon(True)
        self.gor_command = gor_command

    def run(self):
        LOGGER.debug("Start ClonerThread.")
        self.command = Command(self.gor_command)
        return self.command.execute()

    def interrupt(self):
        if self.is_alive():
            LOGGER.debug("Interrupt ClonerThread.")
            self.command.interrupt()
        else:
            LOGGER.debug("Could't interrupt ClonerThread because of is not alive.")


class Cloner:
    thread = None

    def __init__(self, configuration, goreplay_fullpath):
        self.gor_command = GoReplayCommand(configuration, goreplay_fullpath).build()
        LOGGER.debug("GorReplayCommand: %s." % self.gor_command)

    def start(self):
        self.thread = ClonerThread(self.gor_command)
        result = self.thread.start()
        LOGGER.info("Cloner has started.")
        self.wait_for_thread()
        return result

    def stop(self):
        if self.thread:
            self.thread.interrupt()
            self.wait_for_thread()
            LOGGER.info("Cloner has stopped.")
        else:
            LOGGER.info("Couldn't stop Cloner because of ClonerThread in None.")

    def wait_for_thread(self):
        self.thread.join()

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
    LOGGER.debug(ARGS)

    result = None
    try:
        if ARGS.version_gor:
            result = Cloner().version_gor()
        elif ARGS.help_gor:
            result = Cloner().help_gor()
        else:
            configuration = ClonerConfiguration(ARGS.configuration_path).load()
            CLONER = Cloner(configuration, "/home/banan/goreplay")
            CLONER.start()

        LOGGER.info("Result: %s.", result)
    except SystemExit:
        LOGGER.error("System exit.")
        pass
    except KeyboardInterrupt:
        LOGGER.error("Keyboard interrupt.")
        pass
    except Exception as e:
        LOGGER.exception("Exception: %s.", e)
        raise e
    finally:
        if CLONER:
            CLONER.stop()
