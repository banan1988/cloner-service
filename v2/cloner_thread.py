try:
    # Python 2
    from Queue import Queue
except ImportError:
    # Python 3
    from queue import Queue

from threading import Thread

from command import Command
from configuration import ClonerConfiguration
from goreplay import GoReplayCommand


class ClonerThread(Thread):
    results = Queue()

    def __init__(self, configuration, goreplay_fullpath="./goreplay", shell=False):
        Thread.__init__(self)
        self.setName("ClonerThread")
        self.setDaemon(True)
        go_replay_command = GoReplayCommand(configuration, goreplay_fullpath).build()
        self.go_replay = Command(go_replay_command, shell=shell)

    def run(self):
        result = self.go_replay.execute()
        self.results.put(result)

    def stop(self):
        return self.go_replay.interrupt()

    def get(self):
        while not self.results.empty():
            return self.results.get()


if __name__ == '__main__':
    configuration = ClonerConfiguration("./").load()
    t = ClonerThread(configuration, shell=False)
    t.start()

    try:
        while t.isAlive():
            print("---> What's up !")
            print ("alive:", t.isAlive())
            kill = input("Kill ? ")
            print(kill, t.isAlive())
            if kill in ['yes', 'True', 'true']:
                code = t.stop()
                print ("Code: ", code)

        print("Result: %s" % t.get())
        print ("Finished. Alive:", t.isAlive())
    except Exception as e:
        print(e)
        t.stop()
    except KeyboardInterrupt as e:
        print(e)
        t.stop()
    except SystemExit as e:
        print(e)
        t.stop()
