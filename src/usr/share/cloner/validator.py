#!/usr/bin/env python
import re             
from urlparse import urlparse

__all__ = ["Validator"]

__version__ = "0.1"


def is_hostname(hostname):
    if len(hostname) > 255:
        return False
    if hostname[-1] == ".":
        hostname = hostname[:-1]
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))


def is_url(url):
    parsed_url = urlparse(url)
    return parsed_url.scheme in ["ftp", "http", "https"]


def is_url_path(path):
    parsed_path = urlparse(path)
    return parsed_path.path and parsed_path.path.startswith("/")


def is_regexp(regexp):
    try:
        re.compile(regexp)
        return True
    except re.error:
        return False


def is_rewrite_path(rewrite_path):
    parts = rewrite_path.split(":")
    if len(parts) == 2:
        return is_regexp(parts[0])
    return False
