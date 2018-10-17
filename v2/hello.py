from flask import Flask

from cloner_thread import ClonerThread
from configuration import ClonerConfiguration

app = Flask(__name__)

configuration = ClonerConfiguration("./").load()
t = ClonerThread(configuration, shell=False)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/start')
def start():
    try:
        return "Start: %s" % t.start()
    except:
        return "Error"


@app.route('/stop')
def stop():
    if t.isAlive():
        t.stop()
    return "Stop: %s" % t.get()


@app.route('/status')
def status():
    alive = t.isAlive()
    return "alive: %s" % alive


if __name__ == '__main__':
    app.run(threaded=True)
