#! /usr/bin/python

from distutils.core import setup
from subprocess import call
from os import path
import os
import sys
import re


def getUserInput(msg, default=None, validate=None):
    while True:
        input = raw_input(msg)

        # Did we pass in a default
        if default:
            if input == "":
                return default

        # Did we ask to validate the input
        if not validate:
            return input
        if re.search(validate, input):
            return input
        print "Invalid entry, Try again"


def YesNo(msg, default=None):
    while True:
        result = getUserInput(msg, default)
        if re.match("^(Y|y)$", result):
            return True
        if re.match("^(N|n)$", result):
            return False


def rename(file, rename_list):
    for old, new in rename_list.items():
        #print ("Rename: '%s' '%s'" % (old, new))
        if file == old:
            return new
    return file


def skipable(file, skip_regex):
    for regex in skip_regex:
        #print ("regex: '%s' '%s'" % (regex, file))
        if re.search(regex, file):
            return True
    return False


def search(file, needle):
    try:
        with open(file, 'r') as haystack:
            for line in haystack:
                if re.search(needle, line):
                    return True
        return False
    except IOError, e:
        return False


def append(target, source):
    # If the target file already has the appends
    if search(target, '# dev-tools'):
        return

    with open(source, 'r') as src:
        with open(target, "a") as dest:
            for line in src:
                dest.write(line)

def edit(file, regex, replace):
    output = []
    found = False
    replace = "%s\n" % replace

    # Open the file and search for the regex
    with open(file, 'r') as src:
        for line in src:
            if re.search(regex, line):
                output.append(replace)
                found = True
            else:
                output.append(line)

    # If the regex was found in the file, write out the new file
    if found:
        with open(file, 'w') as src:
            src.truncate()
            for line in output:
                src.write(line)


if __name__ == "__main__":

    # Get my name
    prog_name = sys.argv[0].lstrip("./")

    # Ensure we don't get run on shared user accounts!
    user = os.environ.get('USER', '')
    if user != 'thrawn':
        question = "\n-- Current user '%s' != 'thrawn' Continue (Y/N) ? " % user
        if not YesNo(question, "Y"):
            sys.exit(-1)


    # Default install directory to ~/bin
    home_dir = os.environ.get('HOME', '')
    if home_dir == '':
        print "-- Could not determine your home directory"
        sys.exit(-1)

    bin_path = os.path.join(home_dir, "bin")

    # If the user supplied a dest directory, use that instead
    if len(sys.argv) > 1:
        print "-- Installing into %s" % sys.argv[1]
        bin_path = sys.argv[1]

    if not path.exists(bin_path):
        question = "\n-- '%s' doesn't exist, create it (Y/N) ? " % bin_path
        if not YesNo(question, "Y"):
            sys.exit(-1)
        os.makedirs(bin_path)

    # Get a listing of all the programs in the current directory
    list = os.listdir(os.getcwd())
    for file in list:

        # Skip the setup.py program
        if skipable(file, ['dev-utils.py', prog_name, '.swp', '^\.',
                '\.vim', '.cnf$', 'mysql-user', 'rc$', 'README']):
            continue

        # Some file need to be linked as different names
        newName = rename(file,  {'svn.py': 'svn'})

        cmd = "cp -f %s/%s %s/%s" % (os.getcwd(), file, bin_path, newName)
        print " -- ", cmd
        call(cmd, shell=True)

    call('mkdir -p ~/.vim', shell=True)
    call('mkdir -p ~/.vimswap', shell=True)
    call('cd vim; tar -vcf - . | $( cd ~/.vim; tar -vxf - )', shell=True)
    call('cp vimrc ~/.vimrc', shell=True)
    call('cp gvimrc ~/.gvimrc', shell=True)

    # SSH
    call('mkdir -p ~/.ssh', shell=True)
    call('chmod u+rwx,go-rwx ~/.ssh', shell=True)
    call('cd ssh; tar -vcf - . | $( cd ~/.ssh; tar -vxf - )', shell=True)

    call('git config --global color.diff auto', shell=True)
    call('git config --global color.status auto', shell=True)
    call('git config --global color.branch auto', shell=True)
    call('git config --global user.name "Derrick J. Wippler"', shell=True)
    call('git config --global user.email thrawn01@gmail.com', shell=True)
    call('git config --global push.default current', shell=True)

    bashrc = os.path.join(home_dir, ".bashrc")
    # Setup .bashrc
    if path.exists("/Library"):
        bashrc = os.path.join(home_dir, ".bash_profile")
        # OSX
        append(bashrc, "osx/bash_profile")
        os.system('cd `git --exec-path`; sudo ln -s %s/bin/git-* ."' % home_dir)
        print "--- OSX only ---"
        print "-- brew install coreutils && brew install git && brew doctor"
        print "-- Fix the paths by modifying /etc/paths"

    else:
        # Linux
        append(bashrc, "bashrc")

    print "\n\n"
    print "Choose a color for the bash prompt hostname"
    print " 1 = Red, 2 = Green, 3 = Yellow, 4 = Blue "
    print " 5 = Pink, 6 = Cyan, 7 = White, 8 = Black "
    color = getUserInput("Color (default=4) > ", '4', '^\d$')
    edit(bashrc, "^C3=", "C3=\"\[\e[1;3%sm\]\" # <- hostname color" % color)

    print "Choose a name to report in iterm tabs"
    tab = getUserInput("Tab (default=\h) > ", '\h')
    edit(bashrc, "^TAB=", "TAB='\\033]0;%s\\007'" % tab)

    print " -- Modify This line in /etc/sudoers"
    print "%sudo	ALL=(ALL:ALL) NOPASSWD: ALL"
