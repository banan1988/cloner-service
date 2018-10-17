import Queue
from threading import Thread

from command import Command
from configuration import ClonerConfiguration
from goreplay import GoReplayCommand


class ClonerThread(Thread):
    results = Queue.Queue()

    def __init__(self, configuration, goreplay_fullpath="/home/banan/goreplay", shell=False):
        Thread.__init__(self)
        self.setName("ClonerThread")
        self.setDaemon(True)
        go_replay_command = GoReplayCommand(configuration, goreplay_fullpath).build_string()
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
    t = ClonerThread(configuration, shell=True)
    t.start()

    while t.isAlive():
        print("---> What's up !")
        print ("alive:", t.isAlive())
        kill = raw_input("Kill ? ")
        if kill in ['yes', 'True', 'true']:
            code = t.stop()
            print ("Code: ", code)

    print("Result: ", t.get())
    print ("Finished. Alive:", t.isAlive())
