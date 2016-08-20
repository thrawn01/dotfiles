#! /usr/bin/env python

from __future__ import print_function
from argparse import ArgumentParser
import time
import sys
import os


def connect():
    """
       -t   Force pseudo-tty allocation.  This can be used to execute arbi-
            trary screen-based programs on a remote machine, which can be
            very useful, e.g., when implementing menu services.  Multiple -t
            options force tty allocation, even if ssh has no local tty.


       -m   causes screen  to  ignore  the  $STY  environment  variable.  With
            "screen  -m"  creation  of  a  new session is enforced, regardless
            whether screen is called from within  another  screen  session  or
            not.  This  flag has a special meaning in connection with the `-d'
            option:
    """
    if isRackspace():
        os.execle("/usr/bin/ssh", '-t', '-t', 'thrawn01.org.bast',
                  'screen', '-mdr', os.environ)
    else:
        os.execle("/usr/bin/ssh", '-t', '-t', 'thrawn01.org',
                  'screen', '-mdr', os.environ)
    return 0


def connect_forever():
    pid = None
    try:
        print("Connecting Forever...")
        while True:
            print("Connecting...")
            pid = os.fork()
            if pid == 0:
                sys.exit(connect())
            print("parent: %d, child: %d" % (os.getpid(), pid))
            os.waitpid(pid, 0)
            print("Sleeping...")
            time.sleep(10)
    finally:
        if pid:
            os.wait()
        return 0


def isRackspace():
    # Ping 1 Count, Wait 1 Second for response
    return os.system("ping -c 1 -W 1 inside.rackspace.com 2>&1>/dev/null") == 0



parser = ArgumentParser(description="Decide what network I'm on "
                        "and connect to my IRC screen")
parser.add_argument('--reconnect', action='store_true', default=False,
                    help='Continue to attempt reconnection when disconnected')
opt = parser.parse_args()

if opt.reconnect:
    sys.exit(connect_forever())
sys.exit(connect())

