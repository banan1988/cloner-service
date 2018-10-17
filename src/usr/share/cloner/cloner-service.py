#!/usr/bin/env python
import os
import socket
from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from SocketServer import ThreadingMixIn
from threading import Thread

import logger
from cloner import Cloner
from cloner import ClonerConfiguration

LOGGER = logger.get_logger('cloner_service')
ACCESS_LOG_LOGGER = logger.get_logger('access_log')


class DefaultHTTPRequestHandler(SimpleHTTPRequestHandler):
    def log_request(self, code='-', size='-'):
        ACCESS_LOG_LOGGER.info(
            "%s %s %s %s %s",
            self.address_string(),
            self.log_date_time_string(),
            self.requestline,
            str(code),
            str(size))

    def send_headers(self, parameters):
        assert type(parameters) == dict

        for key, value in parameters.items():
            self.send_header(key, value)

        self.end_headers()

    def send_content(self, content):
        self.wfile.write(content)

    def send_error_404(self):
        error_msg = "Not Found resources under %s path" % self.path
        self.send_error(404, error_msg)

    def send_error_500(self, e):
        error_msg = "Couldn't handle request for path: %s - %s" % (self.path, e)
        self.send_error(500, error_msg)


class HTTPRequestHandler(DefaultHTTPRequestHandler):
    """python 2"""

    CLONER = None

    def do_GET(self):
        try:
            if self.path == "/":
                self.send_response(200)
                self.send_headers({"Content-type": "text/html; charset=utf-8"})

                self.send_content("Say hello !")
                return

            if self.path == "/start":
                self.send_response(200)

                configuration = ClonerConfiguration("../../../etc/cloner").load()
                self.CLONER = Cloner(configuration)
                self.CLONER.start()

                return

            if self.path == "/stop":
                self.send_response(200)

                if self.CLONER:
                    self.CLONER.stop()

                return

        except Exception as e:
            self.send_error_500(e)
            return

        self.send_error_404()
        return


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    allow_reuse_address = True

    def shutdown(self):
        self.socket.close()
        HTTPServer.shutdown(self)


class SimpleHttpServer:
    server = None
    server_thread = None

    def __init__(self, ip, port, handler):
        self.server = ThreadedHTTPServer((ip, port), handler)

    def start(self):
        try:
            self.server_thread = Thread(target=self.server.serve_forever)
            self.server_thread.name = "HTTPServerThread"
            self.server_thread.daemon = True
            self.server_thread.start()
            LOGGER.info("HTTP server has started listening on %s." % str(self.server.server_address))
            self.wait_for_thread()
        finally:
            LOGGER.info("HTTP server has finished.")

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.wait_for_thread()
            LOGGER.info("HTTP server has stopped.")
        else:
            LOGGER.info("Couldn't stop HTTP server because of server in None.")

    def wait_for_thread(self):
        self.server_thread.join()


def hostname():
    return socket.getfqdn()


def register():
    # r = requests.get('http://127.0.0.1:8080')
    # LOGGER.debug(r)
    pass


def check_configuration():
    LOGGER.info("Check configuration for %s." % hostname())


if __name__ == '__main__':
    os.environ.setdefault('GO_REPLAY_PATH', '../../local/bin/goreplay')

    SERVER = None
    try:
        SERVER = SimpleHttpServer('127.0.0.1', 8080, HTTPRequestHandler)
        SERVER.start()
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
        if SERVER:
            SERVER.stop()
