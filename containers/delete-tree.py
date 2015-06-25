#! /usr/bin/env python

from __future__ import print_function

from argparse import ArgumentParser
import shutil
import yaml
import sys
import re
import os


class RegexMatcher(object):
    """ Given a config will create a match object that
    matches a file based on the config passed in.

    # Config example
    config = {
        'delete' [
            '\.go$',
            '\.bat$',
        ],
        'exclude': [
            '/docs'
        ]
    }
    """
    def __init__(self, config):
        self.deletes = self.compile(config.get('delete', []))
        self.excludes = self.compile(config.get('exclude', []))

    def match(self, path):
        def _match(regexes):
            for regex in regexes:
                if regex.search(path):
                    return regex.pattern
            return None

        # If the path matches any delete reqexes
        matched = _match(self.deletes)
        if matched:
            # and if the match is not in the excludes
            if not _match(self.excludes):
                print("-- Matched '%s' - '%s'" % (matched, path))
                return True

    def compile(self, regexes):
        return [re.compile(regex) for regex in regexes]


class Application(object):

    def isEmpty(self, dirName):
        return (len(os.listdir(dirName)) == 0)

    def deleteDirs(self, path, opts):
        if self.isEmpty(path) and opts.del_dirs:
            print("-- Deleting empty Directory %s" % (path))
            if opts.force:
                shutil.rmtree(path)
            # Climb up the dir tree, is it empty also?
            return self.deleteDirs(os.path.dirname(path), opts)

    def delete(self, path, matcher, opts):
        for dirName, dirNames, fileNames in os.walk(path):
            for name in dirNames:
                path = os.path.join(dirName, name)
                if not matcher.match(path):
                    continue
                if opts.force:
                    if os.path.islink(path):
                        os.unlink(path)
                    else:
                        shutil.rmtree(path)

            for name in fileNames:
                path = os.path.join(dirName, name)
                if not matcher.match(path):
                    continue
                if opts.force:
                    os.unlink(path)

            if opts.del_dirs:
                self.deleteDirs(dirName, opts)

    def run(self, args):
        description = """
            Delete files from a directory tree by reading a list of file
            regexes from a yaml config file

            Example config file to delete all *.go and *.bat files, excluding
            files inside /docs directory.

            delete:
                - \.go$
                - \.bat$

            exclude:
                - /docs
        """
        p = ArgumentParser(description=description)
        p.add_argument('--path', '-p', default='.', help="Delete files"
                       " specified in this path tree (default: current"
                       " directory)")
        p.add_argument('--del-dirs', '-d', default=False, action='store_true',
                       help="Delete directories if they are empty")
        p.add_argument('--force', '-f', default=False, action='store_true',
                       help="Delete files")
        p.add_argument('config', metavar='<CONFIG-FILE>', help="YAML config file")
        opts = p.parse_args(args)

        with open(opts.config) as fd:
            # Load the config from the YAML file
            config = yaml.load(fd)

        # Load the regex expression from the config
        matcher = RegexMatcher(config)
        self.delete(opts.path, matcher, opts)


if __name__ == "__main__":
        #try:
            app = Application()
            sys.exit(app.run(sys.argv[1:]))
        #except (Exception), e:
            #print("-- non-zero exit: %s" % e)
            #sys.exit(1)
