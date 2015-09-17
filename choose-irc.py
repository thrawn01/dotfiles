#! /usr/bin/env python

import os

def isRackspace():
    # Ping 1 Count, Wait 1 Second for response
    return os.system("ping -c 1 -W 1 inside.rackspace.com 2>&1>/dev/null") == 0

if isRackspace():
    os.execle("/usr/bin/ssh", '-X', 'thrawn01.org.bast', os.environ)
else:
    os.execle("/usr/bin/ssh", '-X', 'thrawn01.org', os.environ)
