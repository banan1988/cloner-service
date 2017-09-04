#!/usr/bin/env python
import json
import os

import re

from validator import Validator

__all__ = ["GorReplay"]

__version__ = "0.1"


def flat_array(array: list):
    # flat [[key, value], [key, value]]
    return [item for sublist in array for item in sublist]


class GorCommandException(Exception):
    pass


class InputType:
    RAW = "raw"
    TCP = "tcp"


class RawEngine:
    DEFAULT = "libpcap"
    RAW_SOCKET = "raw_socket"


class GoReplayCommand:
    def __init__(self, configuration_file, goreplay_file="./goreplay"):
        self.goreplay_file = goreplay_file
        self.configuration = self._load_configuration(configuration_file)

    def _load_configuration(self, configuration_file):
        with open(configuration_file) as f:
            return json.loads(f.read())

    def _input_raw(self):
        if InputType.RAW in self.configuration["input"]:
            if self.configuration["input"][InputType.RAW]["port"] > 0:
                return ["--input-raw", (":%d" % self.configuration["input"][InputType.RAW]["port"])]
            raise GorCommandException(
                "RAW port %s has to be greater than 0" % self.configuration["input"][InputType.RAW]["port"])
        return []

    def _input_raw_engine(self):
        if "engine" in self.configuration["input"]:
            if RawEngine.DEFAULT == self.configuration["input"] or RawEngine.RAW_SOCKET == self.configuration["input"]:
                return ["--input-raw-engine", self.configuration["input"]]
        return ["--input-raw-engine", RawEngine.DEFAULT]

    def _append_rate(self, host, global_rate):
        if host.get("rate", None):
            return '"%s|%s"' % (host["host"], host["rate"])
        elif global_rate:
            return '"%s|%s"' % (host["host"], global_rate)
        return '"%s"' % host["host"]

    def _output_http(self, host):
        if Validator.is_url(host["host"]):
            return ["--output-http", self._append_rate(host, self.configuration["output"]["http"]["rate"])]
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

    def _http_allow_url(self, path):
        if Validator.is_url_path(path):
            return ["--http-allow-url", '"%s"' % path]
        raise GorCommandException("Allow path %s has incorrect format" % path)

    def _http_allow_urls(self):
        if not self.configuration["input"][InputType.RAW]["paths"]:
            return []

        allow_urls = [self._http_allow_url(path) for path in
                      self.configuration["input"][InputType.RAW]["paths"]["allow"]]
        return flat_array(allow_urls)

    def _http_disallow_url(self, path):
        if Validator.is_url_path(path):
            return ["--http-disallow-url", '"%s"' % path]
        raise GorCommandException("Disallow path %s has incorrect format" % path)

    def _http_disallow_urls(self):
        if not self.configuration["input"][InputType.RAW]["paths"]:
            return []

        disallow_urls = [self._http_disallow_url(path) for path in
                         self.configuration["input"][InputType.RAW]["paths"]["disallow"]]
        return flat_array(disallow_urls)

    def _http_rewrite_url(self, rewrite_path):
        if Validator.is_rewrite_path(rewrite_path):
            return ["--http-rewrite-url", '"%s"' % rewrite_path]
        raise GorCommandException("Rewrite path %s has incorrect format. Expects ':' as a delimiter." % rewrite_path)

    def _http_rewrite_urls(self):
        if not self.configuration["input"][InputType.RAW]["paths"]:
            return []

        rewrite_urls = [self._http_rewrite_url(path) for path in
                        self.configuration["input"][InputType.RAW]["paths"]["rewrite"]]
        return flat_array(rewrite_urls)

    def _output_http_workers(self):
        # (Average number of requests per second)/(Average target response time per second)
        if self.configuration["output"]["http"]["workers"] >= 1:
            return ["--output-http-workers", str(self.configuration["output"]["http"]["workers"])]
        return []

    def _exit_after(self):
        if self.configuration["exit_after"]:
            match = re.match("([0-9]+)([smh])", self.configuration["exit_after"])
            if match and int(match.group(1)) > 0:
                return ["--exit-after", self.configuration["exit_after"]]
        return []

    def _extra_args(self):
        if self.configuration["extra_args"]:
            extra_args = [[key, '"%s"' % value] for key, value in self.configuration["extra_args"].items()]
            return flat_array(extra_args)
        return []

    def _goreplay(self):
        if os.path.exists(self.goreplay_file):
            return [self.goreplay_file]
        raise GorCommandException("Not found 'goreplay' application in path: %s" % self.goreplay_file)

    def build(self):
        args = []

        args += self._goreplay()

        if self.configuration:
            args += self._input_raw()
            args += self._input_raw_engine()

            args += self._http_allow_urls()
            args += self._http_disallow_urls()
            args += self._http_rewrite_urls()

            args += self._output_https()
            args += self._output_http_workers()

            args += self._exit_after()
            args += self._extra_args()

        return args

    def build_string(self):
        return " ".join(self.build())


if __name__ == '__main__':
    goReplayCommand = GoReplayCommand("../../../etc/cloner/cloner.json", "../../local/bin/goreplay").build()
    print(goReplayCommand)
