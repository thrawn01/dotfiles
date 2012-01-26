#! /usr/bin/python

from distutils.core import setup 
from os import path
import os
import sys
import re

def getUserInput( msg, default=None, validate=None ):
    while True:
        input = raw_input( msg )

        # Did we pass in a default
        if default:
            if input == "":
                return default

        # Did we ask to validate the input
        if validate:
            if re.search( validate, input ):
                return input
            print "Invalid entry, Try again"
        else:
            return input

def YesNo( msg, default=None ):
    while True:
        result = getUserInput( msg, default )
        if re.match( "^(Y|y)$", result ):
            return True
        if re.match( "^(N|n)$", result ):
            return False

def rename( file, rename_list ):
    for old,new in rename_list.items():
        #print ("Rename: '%s' '%s'" % (old, new))
        if file == old:
            return new
    return file


def skipable( file, skip_regex ):
    for regex in skip_regex:
        #print ("regex: '%s' '%s'" % (regex, file))
        if re.search( regex, file ):
            return True
    return False



if __name__ == "__main__":
    
    # Get my name
    prog_name = sys.argv[0].lstrip("./")

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

    if not path.exists( bin_path ):
        print ""
        if not YesNo( "'%s' doesn't exist, Should I create it (Y/N) ? " % bin_path, "Y" ):
            sys.exit(-1)
        os.makedirs( bin_path )

    # Get a listing of all the programs in the current directory
    list = os.listdir( os.getcwd() )
    for file in list:

        # Skip the setup.py program
        if skipable(file, [ 'dev-utils.py', prog_name, '.swp', '^\.', '\.vim', 'rc$', 'README' ] ):
            continue

        # Some file need to be linked as different names
        newName = rename(file,  {'svn.py':'svn'})

        cmd = "cp -f %s/%s %s/%s" % ( os.getcwd(), file, bin_path, newName )
        print " -- ", cmd
        os.system( cmd )

    os.system('mkdir -p ~/.vim/colors');
    os.system('cp thrawn.vim ~/.vim/colors');
    os.system('cp vimrc ~/.vimrc');
    os.system('cp gvimrc ~/.gvimrc');

    # Print out 
    print """
# Add this to .bashrc or .bash_profile
export PATH="$PATH:~/bin"
alias gvim='~/bin/gvim-tabs.py'

# OSX X11 Timeout Issue
#ForwardX11Timeout 596h
alias ssh='ssh -X'

# Leet Promptness
C0="\[\e[0m\]"
C1="\[\e[1;30m\]" # <- subdued color
C2="\[\e[1;37m\]" # <- regular color
C3="\[\e[1;32m\]" # <- hostname color
C4="\[\e[1;34m\]" # <- seperator color (..[ ]..)
#PROMPT='\$'                                    
PROMPT='>'
export PS1="$C3$C4..( $C2\u$C1@$C3\h$C1($C2\l$C1): $C2\w$C1$C1 : $C2\\t$C1 $C4)..\\n$C3$C2$PROMPT$C1$PROMPT$C0 "
"""

