#! /usr/bin/env python

from subprocess import call
import sys
import os
import re

def fixPermissions(cwd='.'):

    for dirname, dirnames, filenames in os.walk(cwd):
        # print path to all filenames.
        for filename in filenames:
            path = os.path.join(dirname, filename)
            print "-- file: %s" % path
            if re.search("(.sh)%", path):
                call(['chmod', 'o-rw' ,'%s' % path])
            else:
                call(['chmod', 'ugo-x', '%s' % path])
                call(['chmod', 'ug+rw', '%s' % path])

        for subdirname in dirnames:
            print "-- dir: %s" % path
            path = os.path.join(dirname, subdirname)
            call(['chmod', 'o-rw' ,'%s' % path])

        # Advanced usage:
        # editing the 'dirnames' list will stop os.walk() from recursing into there.
        if '.git' in dirnames:
            # don't go into any .git directories.
            dirnames.remove('.git')

if __name__ == '__main__':
    sys.exit(fixPermissions())

