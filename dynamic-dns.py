#! /usr/bin/python

# Run every 10 mins in crontab

from subprocess import check_output, call
import argparse
import sys
import re
import os


def ipAddress(interface):
    for line in check_output(['/sbin/ifconfig', interface]).split('\n'):
        match = re.search('(inet addr:)(\S*)', line)
        if match:
            return match.group(2)


def findInterface():
    for line in check_output('/sbin/ifconfig').split('\n'):
        match = re.match('^eth\d', line)
        if match:
            return match.group()
    raise RuntimeError("Unable to find appropriate interface")


def load(address):
    try:
        with open("%s/.dynip-address" % os.environ['HOME'], 'r') as file:
            print file.name
            return file.read()
    except IOError:
        return ''

def save(address):
    with open("%s/.dynip-address" % os.environ['HOME'], 'w') as file:
        return file.write(address)


def run(interface, key):
    if not interface:
        interface = findInterface()
    address = ipAddress(interface)
    if load(address) != address:
        url = "http://freedns.afraid.org/dynamic/update.php?%s&address=%s" % (key, address)
        print "IP Address Changed: ", address
        print "Update URL: ", url
        call(['curl', '-s', url])
        save(address)
        return 0
    return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Update ip address for dynamic dns for freedns.afraid.org")
    parser.add_argument('-i', '--interface', help='The interface to get the ip"\
        " from (defaults to the first eth interface returned by ifconfig')
    parser.add_argument('-c', '--crontab', action='store_true',
        help="Output a crontab file that will execute this script every 10 mins")
    parser.add_argument('key', help="the 'Direct URL' key from http://freedns.afraid.org/dynamic/")
    opt = parser.parse_args()

    if opt.crontab:
        print "*/10 * * * * ~/bin/dynamic-dns.py %s" % opt.key
        sys.exit(0)

    sys.exit(run(opt.interface, opt.key))
