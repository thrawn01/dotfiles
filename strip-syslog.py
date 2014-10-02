#! /usr/bin/env python

import sys

#with open(sys.argv[2], 'w') as output:
with open(sys.argv[1]) as input:
    for line in input:
        print line[96:],


#Oct  2 06:39:02.632766 api02.dfw2.lunr.racklabs.com 2014-10-02 06:39:02.632 55817 INFO wsgi [-]
