import Queue
from threading import Thread

from command import Command
from configuration import ClonerConfiguration
from goreplay import GoReplayCommand

configuration = ClonerConfiguration("./").load()
goReplayCommand = GoReplayCommand(configuration, "/home/banan/goreplay").build_string()
goReplay = Command(goReplayCommand, shell=True)
results = Queue.Queue()


def execute(goReplay, results):
    results.put(goReplay.execute())


def stop(goReplay):
    return goReplay.interrupt()


if __name__ == '__main__':
    t = None
    try:
        t = Thread(target=execute, args=[goReplay, results])
        t.setName("GoReplay")
        t.setDaemon(True)
        t.start()
    finally:
        print("==== Good bye !")

    while t.isAlive():
        print("---> What's up !")
        print ("alive:", t.isAlive())
        kill = raw_input("Kill ? ")
        if kill in ['yes', 'True', 'true']:
            code = stop(goReplay)
            print ("Code: ", code)

    while not results.empty():
        result = results.get()
        print("Result: ", result)
    print ("Finished. Alive:", t.isAlive())
