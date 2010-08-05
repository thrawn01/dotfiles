#! /usr/bin/python

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

    # Verify the user has ~/bin already
    bin_path = os.path.join( os.path.expanduser("~"), "bin" )
    if not path.exists( bin_path ):
        print ""
        if not YesNo( "~/bin doesn't exist, Should I create it (Y/N) ? ", "Y" ):
            sys.exit(-1)

        os.makedirs( bin_path )

    # Get a listing of all the programs in the current directory
    list = os.listdir( os.getcwd() )
    for file in list:

        # Skip the setup.py program
        if skipable(file, [ prog_name, '.swp', '^\.' ] ):
            continue

        # Some file need to be linked as different names
        newName = rename(file,  {'svn.py':'svn'})

        cmd = "ln -sf %s/%s %s/%s" % ( os.getcwd(), file, bin_path, newName )
        print " -- ", cmd
        os.system( cmd )

    
