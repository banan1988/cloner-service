#!/usr/bin/env python
import os
import re

from configuration import ClonerConfiguration
from env import GO_REPLAY_FULLPATH
from validator import is_url, is_url_path, is_rewrite_path


# flat [[key, value], [key, value]]
def flat_array(array):
    return [item for sublist in array for item in sublist]


class GorCommandException(Exception):
    pass


class InputType:
    RAW = "raw"
    TCP = "tcp"

    def __init__(self):
        pass


class RawEngine:
    DEFAULT = "libpcap"
    RAW_SOCKET = "raw_socket"

    def __init__(self):
        pass


class GoReplayCommand:
    def __init__(self, configuration, goreplay_fullpath=GO_REPLAY_FULLPATH):
        self.configuration = configuration
        self.goreplay_fullpath = goreplay_fullpath

    def _input_raw(self):
        if InputType.RAW in self.configuration["input"]:
            if self.configuration["input"][InputType.RAW]["port"] > 0:
                return ["--input-raw", (":%d" % self.configuration["input"][InputType.RAW]["port"])]
            raise GorCommandException(
                "RAW port %s has to be greater than 0" % self.configuration["input"][InputType.RAW]["port"])
        return []

    def _input_raw_engine(self):
        raw_engines = [RawEngine.DEFAULT, RawEngine.RAW_SOCKET]
        if "engine" in self.configuration["input"][InputType.RAW]:
            if self.configuration["input"][InputType.RAW]["engine"] in raw_engines:
                return ["--input-raw-engine", self.configuration["input"][InputType.RAW]["engine"]]
        return []

    def _append_rate(self, host, global_rate):
        if host.get("rate", None):
            return '"%s|%s"' % (host["host"], host["rate"])
        elif global_rate:
            return '"%s|%s"' % (host["host"], global_rate)
        return '"%s"' % host["host"]

    def _output_http(self, host):
        if is_url(host["host"]):
            return ["--output-http", self._append_rate(host, self.configuration["output"]["http"].get("rate", "100%"))]
        raise GorCommandException("Output's HTTP host %s has incorrect format" % host["host"])

    def _output_https(self):
        if not self.configuration["output"]["http"]:
            return []

        target_hosts = self.configuration["output"]["http"]["hosts"]
        if len(target_hosts) == 0:
            raise GorCommandException("List of output's HTTP hosts is empty")

        output_https = []
        for target_host in target_hosts:
            output_https += self._output_http(target_host)
        return output_https

    def _output_elasticsearch(self):
        if "elasticsearch" in self.configuration["output"]:
            return ["--output-http-elasticsearch", '"%s/%s"' % (
                self.configuration["output"]["elasticsearch"]["host"],
                self.configuration["output"]["elasticsearch"]["index"])]
        return []

    def _http_allow_url(self, path):
        if is_url_path(path):
            return ["--http-allow-url", '"%s"' % path]
        raise GorCommandException("Allow path %s has incorrect format" % path)

    def _http_allow_urls(self):
        if not self.configuration["input"][InputType.RAW]["paths"]:
            return []

        allow_urls = [self._http_allow_url(path) for path in
                      self.configuration["input"][InputType.RAW]["paths"]["allow"]]
        return flat_array(allow_urls)

    def _http_disallow_url(self, path):
        if is_url_path(path):
            return ["--http-disallow-url", '"%s"' % path]
        raise GorCommandException("Disallow path %s has incorrect format" % path)

    def _http_disallow_urls(self):
        if not self.configuration["input"][InputType.RAW]["paths"]:
            return []

        disallow_urls = [self._http_disallow_url(path) for path in
                         self.configuration["input"][InputType.RAW]["paths"]["disallow"]]
        return flat_array(disallow_urls)

    def _http_rewrite_url(self, rewrite_path):
        if is_rewrite_path(rewrite_path):
            return ["--http-rewrite-url", '"%s"' % rewrite_path]
        raise GorCommandException("Rewrite path %s has incorrect format. Expects ':' as a delimiter." % rewrite_path)

    def _http_rewrite_urls(self):
        if not self.configuration["input"][InputType.RAW]["paths"]:
            return []

        rewrite_urls = [self._http_rewrite_url(path) for path in
                        self.configuration["input"][InputType.RAW]["paths"]["rewrite"]]
        return flat_array(rewrite_urls)

    def _http_allow_method(self, method):
        allowed_methods = ["GET", "POST", "PUT", "DELETE"]
        if method in allowed_methods:
            return ["--http-allow-method", method]
        raise GorCommandException("Allow method %s should be one of: %s." % (method, allowed_methods))

    def _http_allow_methods(self):
        if "methods" in self.configuration["input"][InputType.RAW]:
            allowed_methods = [self._http_allow_method(method) for method in
                               self.configuration["input"][InputType.RAW]["methods"]["allow"]]
            return flat_array(allowed_methods)
        return []

    def _output_http_workers(self):
        # (Average number of requests per second)/(Average target response time per second)
        if self.configuration["output"]["http"].get("workers", 0) >= 1:
            return ["--output-http-workers", str(self.configuration["output"]["http"]["workers"])]
        return []

    def _output_http_timeout(self):
        if self.configuration["output"]["http"].get("timeout", "5s"):
            match = re.match("([0-9]+)(s|m|h)", self.configuration["output"]["http"]["timeout"])
            if match and int(match.group(1)) > 0:
                return ["--output-http-timeout", self.configuration["output"]["http"]["timeout"]]
        return []

    def _exit_after(self):
        if self.configuration.get("exit_after", None):
            match = re.match("([0-9]+)(s|m|h)", self.configuration["exit_after"])
            if match and int(match.group(1)) > 0:
                return ["--exit-after", self.configuration["exit_after"]]
        return []

    def _extra_args(self):
        if self.configuration.get("extra_args", None):
            extra_args = [[key, '"%s"' % value] for key, value in self.configuration["extra_args"].items()]
            return flat_array(extra_args)
        return []

    def _debug(self):
        if self.configuration.get("debug", False):
            return ["--debug"]
        return []

    def _stats(self):
        if self.configuration.get("stats", False):
            return ["--stats"]
        return []

    def _verbose(self):
        if self.configuration.get("verbose", False):
            return ["--verbose"]
        return []

    def _goreplay(self):
        if os.path.exists(self.goreplay_fullpath):
            return [self.goreplay_fullpath]
        raise GorCommandException("Not found 'goreplay' application in path: %s" % self.goreplay_fullpath)

    def build(self):
        args = []

        args += self._goreplay()

        if self.configuration:
            args += self._input_raw()
            args += self._input_raw_engine()

            args += self._http_allow_urls()
            args += self._http_disallow_urls()
            args += self._http_rewrite_urls()

            args += self._http_allow_methods();

            args += self._output_https()
            args += self._output_http_workers()
            args += self._output_http_timeout()

            args += self._output_elasticsearch()

            args += self._extra_args()

            args += self._exit_after()

            args += self._debug()
            args += self._verbose()
            args += self._stats()

        return args

    def build_string(self):
        return " ".join(self.build())


if __name__ == '__main__':
    configuration = ClonerConfiguration("./").load()
    goReplayCommand = GoReplayCommand(configuration, "goreplay").build_string()
    print(goReplayCommand)
