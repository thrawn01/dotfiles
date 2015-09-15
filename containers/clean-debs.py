#! /usr/bin/env python

from __future__ import print_function
from argparse import ArgumentParser
import subprocess
import yaml
import sys
import re
import os


class Application(object):

    def __init__(self):
        self.debug = False

    def run(self, args):
        description = """
            Given a YAML config file with a list of packages deletes all
            packages that are not in the dependency tree of the packages
            specified

            *****************************************************************
            NOTE: Script by default prints the packages it will delete, you
            must use --force for the script to actually delete the packages
            *****************************************************************

            Example config file to delete every package except weechat and
            ssh-server

            keep-pkgs:
                - weechat
                - ssh-server

        """
        p = ArgumentParser(description=description)
        p.add_argument('--debug', '-d', action='store_true',
                       help="Print debug stuff to stdout")
        p.add_argument('--root', '-r', action='store_true', default='/',
                       help="Delete from the specified root"
                       " directory (default is '/')")
        p.add_argument('--force', '-f', action='store_true',
                       help="not a dry-run preform the actual removals")
        p.add_argument('config', metavar='<CONFIG-FILE>',
                       help="YAML config file")
        opts = p.parse_args(args)
        self.debug = opts.debug

        with open(opts.config) as fd:
            # Load the config from the YAML file
            cfg = yaml.load(fd)

        keepPkgs = cfg.get('keep-pkgs', [])
        if not len(keepPkgs):
            raise RuntimeError("Config must define a list of 'required-pkgs';"
                               " See --help for config file example")

        # Find Required apps
        if not self.cmd('which dpkg-query'):
            raise RuntimeError("'dpkg-query' is required; Are you on a debian"
                               " based OS?")
        if not self.cmd('which dpkg'):
            raise RuntimeError("'dpkg' is required; Are you on a debian"
                               " based OS?")
        if not self.cmd('which apt-rdepends'):
            raise RuntimeError("'apt-rdepends' is required; Please install"
                               " with 'apt-get install apt-rdepends'")

        keep = self.collectDepends(keepPkgs)
        packages = self.collectInstalledPkgs()
        required, essential, remove = (list(), list(), list())

        meta = self.getMetadata()
        for pkg in packages:
            if pkg in keep:
                print("-- Keeping Package: %s" % pkg)
                continue
            # If this package is essential, defer deletion until after
            # everything else
            if meta[pkg]['essential']:
                essential.append(pkg)
                continue
            # If this package is required, defer deletion until the end
            if meta[pkg]['required']:
                required.append(pkg)
                continue
            remove.append(pkg)

        # Remove Optional packages
        for pkg in remove:
            print("-- Removing Package: %s" % pkg)
            if opts.force:
                self.removePkg(pkg)

        # Remove Required packages
        for pkg in required:
            print("-- Removing Required Package: %s" % pkg)
            if opts.force:
                self.removePkg(pkg)

        # Remove Core packages
        for pkg in essential:
            print("-- Removing Essential Package: %s" % pkg)
            if opts.force:
                self.removePkg(pkg)

    def getMetadata(self):
        result = {}
        print("-- Getting Package Metadata...")
        output = self.cmd("dpkg-query -W --showformat='${Package},"
                          "${Priority},${Essential}\n'")
        for line in output.split('\n'):
            meta = line.split(',')
            result[meta[0]] = {
                'essential': (meta[2] == 'yes'),
                'required': (meta[1] == 'required')
            }
        return result

    def removePkg(self, pkg):
        try:
            self.cmd("dpkg --force-all --purge %s" % pkg)
        except subprocess.CalledProcessError, e:
            print("-- '%s' returned non-zero status: '%s'" % (e.cmd, e.output))

    def collectInstalledPkgs(self):
        print("-- Getting List of Installed Packages...")
        output = self.cmd("dpkg-query -f '${binary:Package}\n' -W")
        return [re.sub('\:.*$', '', line) for line in output.split('\n')]

    def collectDepends(self, keepPkgs):
        results = set()
        for keep in keepPkgs:
            # Run rdepends capturing the dependency output
            print("-- Getting List of Dependencies for %s ..." % keep)
            tree = self.cmd("apt-rdepends %s" % keep)
            # Parse the dependency output into a list of packages
            depends = self.parseDependsTree(tree)
            results.update(set(depends))
        return results

    def parseDependsTree(self, string):
        """ Parses output that looks like
            ----- snip -----
            libselinux1
              Depends: libc6 (>= 2.14)
              Depends: libpcre3
              PreDepends: multiarch-support
            ----- snip -----
        """
        results = []
        for line in string.split('\n'):
            # Package name line
            match = re.match('^(\S*)$', line)
            if match:
                results.append(match.group(1))
            # Grab the 'Depends:' line
            match = re.match('^.*Depends: (\S*).*$', line)
            if match:
                results.append(match.group(1))
        return results

    def cmd(self, cmd):
        env = os.environ
        env.update({'DEBIAN_FRONTEND': 'noninteractive'})
        print("-- Run: %s" % cmd.replace('\n', '\\n'))
        output = subprocess.check_output(cmd, shell=True, env=env)
        return output.rstrip('\n')


if __name__ == "__main__":
    try:
        app = Application()
        sys.exit(app.run(sys.argv[1:]))
    except (Exception), e:
        print("-- non-zero exit: %s" % e)
        sys.exit(1)
