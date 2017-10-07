#!/usr/bin/env python
import threading
from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from SocketServer import ThreadingMixIn
from string import Template

import logger

LOGGER = logger.get_logger()


class DefaultHTTPRequestHandler(SimpleHTTPRequestHandler):
    def log_request(self, code='-', size='-'):
        LOGGER.info(
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

    def get_content_from_template(self, filename, parameters):
        assert type(parameters) == dict

        try:
            with open(filename) as template_file:
                template = Template(template_file.read())
                return template.safe_substitute(parameters)
        except IOError as e:
            raise Exception("Not found template: %s" % filename, e)
        except Exception as e:
            raise Exception("Couldn't get content based on template: %s" % filename, e)

    def get_content_from_file(self, filename):
        try:
            with open(filename) as f:
                return f.read()
        except IOError as e:
            raise Exception("Not found file: %s" % filename, e)
        except Exception as e:
            raise Exception("Couldn't get content based on file: %s" % filename, e)


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
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            LOGGER.info("HTTP server has started listening on %s." % str(self.server.server_address))
            self.wait_for_thread()
        finally:
            LOGGER.info("HTTP server has finished.")

    def wait_for_thread(self):
        self.server_thread.join()

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.wait_for_thread()
            LOGGER.info("HTTP server has stopped.")
        else:
            LOGGER.info("Couldn't stop HTTP server because of server in None.")


if __name__ == '__main__':
    SERVER = None
    try:
        SERVER = SimpleHttpServer('127.0.0.1', 8080, DefaultHTTPRequestHandler)
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
