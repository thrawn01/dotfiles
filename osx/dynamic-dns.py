#! /usr/bin/python

# sudo cp org.afraid.freedns.plist /Library/LaunchAgents
# sudo cp dynamic-dns.py /usr/local/bin
# then edit this file adding your key

from subprocess import check_output, call
import re
import sys


def ipAddress(interface):
    for line in check_output(['ifconfig', interface]).split('\n'):
        match = re.search('(inet) (\S*)', line)
        if match:
            return match.group(2)


def buildUrl(address):
    key = "<insert-key-here>"
    return "http://freedns.afraid.org/dynamic/update.php?%s&address=%s" % (key, address)


for line in check_output('ifconfig').split('\n'):
    match = re.match('^en\d', line)
    if match:
        address = ipAddress(match.group())
        url = buildUrl(address)
        print "IP Address: ", address
        print "Update URL: ", url
        call(['curl', '-s', url])
        sys.exit(0)
