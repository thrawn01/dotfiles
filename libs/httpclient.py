#! /usr/bin/env python

from __future__ import print_function

from argparse import ArgumentParser, RawDescriptionHelpFormatter
import requests

class HttpClientError(Exception):

    def __init__(self, url, msg, code):
        self.msg = "%s returned %s with \"%s\"" % (url, code, msg)
        self.status_code = code

    def __str__(self):
        return self.msg


class HttpClient(object):

    def __init__(self, debug=False, headers=None, timeout=500):
        self.timeout = timeout
        self.debug = debug
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "custom-python-script"
        }
        if headers:
            self.headers.update(headers)
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def http_request(self, call, url, **kwargs):
        try:
            # Remove args with no value
            kwargs = self.unused(kwargs)
            if self.timeout:
                kwargs['timeout'] = self.timeout

            self.print_request((url, call.__name__.upper(),), kwargs)
            resp = call(url, **kwargs)
            self.print_response(resp)
            if resp.status_code != 200:
                raise HttpClientError(url, resp.content,
                                      resp.status_code)
            return resp
        except requests.RequestException, e:
            raise HttpClientError(url, str(e), 0)

    def http_get(self, uri, **kwargs):
        return self.http_request(self.session.get, uri, **kwargs)

    def http_put(self, uri, **kwargs):
        return self.http_request(self.session.put, uri, **kwargs)

    def http_delete(self, uri, **kwargs):
        return self.http_request(self.session.delete, uri, **kwargs)

    def http_post(self, uri, **kwargs):
        return self.http_request(self.session.post, uri, **kwargs)

    def unused(self, _dict):
        """ Remove empty parameters from the dict """
        for key, value in _dict.items():
            if value is None:
                del _dict[key]
        return _dict

    def print_request(self, args, kwargs):
        if not self.debug:
            return

        parts = ['curl -i']
        for arg in args:
            if arg in ('GET', 'POST', 'DELETE', 'PUT'):
                parts.append(' -X %s' % arg)
            else:
                parts.append(' %s' % arg)

        for header in self.session.headers:
            parts.append(' -H "%s: %s"' %
                         (header, self.session.headers[header]))

        if 'data' in kwargs:
            parts.append(" -d '%s'" % (kwargs['data']))
        print("-- request: %s\n" % "".join(parts))

    def print_response(self, resp):
        if self.debug:
            print("-- response: %s " % resp.content)


if __name__ == "__main__":
    desc = """
        Simple http client with proper error reporting and debug output

        Run with debug output
            ./httpclient http://google.com --debug
    """
    p = ArgumentParser(prog='api-check',
                       description=desc,
                       formatter_class=RawDescriptionHelpFormatter)

    p.add_argument('--debug', action='store_true', help="Print debug messages")
    p.add_argument('url', help="The http url to fetch")
    opts = p.parse_args()

    # Create the client with options
    client = HttpClient(debug=opts.debug)
    resp = client.http_get(opts.url)
    print("-- Resp: %s" % resp.text)
