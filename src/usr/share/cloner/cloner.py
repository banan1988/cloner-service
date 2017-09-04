#!/usr/bin/env python
import argparse
import threading

from command import *

__all__ = ["Cloner"]

__version__ = "0.1"


class ClonerThread(threading.Thread):
    def __init__(self, command):
        super(ClonerThread, self).__init__(
            name="ClonerThread",
            daemon=True,
        )
        self.command = command

    def run(self):
        try:
            print("Start cloner thread")
            self.command = Command(self.command)
            return self.command.execute()
        finally:
            print("Stop cloner thread")

    def interrupt(self):
        if self.is_alive():
            self.command.interrupt()


class Cloner:
    # gor_command = "/home/banan/goreplay --input-raw :8080 --output-http localhost:8081"
    # gor_command = "/usr/local/bin/goreplay"
    gor_command = "/home/banan/goreplay"

    def __init__(self):
        pass

    def start(self):
        self.thread = ClonerThread(self.gor_command)
        self.thread.start()
        self.thread.join()

    def stop(self):
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
                        help='Path to configuration.')
    return parser.parse_args()


if __name__ == '__main__':
    ARGS = get_args()
    print(ARGS)

    try:
        if ARGS.version_gor:
            result = Cloner().version_gor()
        elif ARGS.help_gor:
            result = Cloner().help_gor()
        else:
            ARGS.configuration_path

    except SystemExit:
        print('System exit')
        pass
    except KeyboardInterrupt:
        print('Keyboard interrupt')
        pass
    except Exception as e:
        raise e
