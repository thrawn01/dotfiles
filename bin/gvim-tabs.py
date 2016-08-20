#! /usr/bin/python

import platform
import sys
import re
import os


gvim_path = '/usr/bin/gvim'

def linux_buildNewArgs( new_argv ):
    if len(new_argv):
        arg = [ gvim_path, '--servername', 'GVIMLOCAL', '--remote-tab-silent' ]
        arg.extend( new_argv )
        return arg
    return [ gvim_path, '--servername', 'GVIMLOCAL' ]

def osx_buildNewArgs( new_argv ):
    if len(new_argv):
        arg = [ gvim_path, '-g', '--servername', 'GVIMLOCAL', '--remote-tab-silent' ]
        arg.extend( new_argv )
        return arg
    return [ gvim_path, '-g', '--servername', 'GVIMLOCAL' ]

buildNewArgs = linux_buildNewArgs
if platform.system() == "Darwin":
    gvim_path = '/Applications/MacVim.app/Contents/MacOS/Vim'
    buildNewArgs = osx_buildNewArgs

def removeHomeDir( value ):
    home_dir = os.path.expanduser("~")
    regex = "^" + re.escape( home_dir )
    return re.sub( regex, "", value  )

def findInSearchPath( arg, searchPath ):
    for item in searchPath:

        # Remove the home dir if it exists
        arg = removeHomeDir( arg )

        if arg[0] == '/':
            path = os.path.join( item, arg.lstrip("/") )
        else:
            path = os.path.join( item, arg )
        print "Trying: ", path
        if os.path.exists( path ):
            return path
    return False

def replaceFilePaths( argv, searchPath ):
    new_argv = []
    for arg in argv:

        # Might be an absolute path
        if os.path.exists( arg ):
            new_argv.append( os.path.abspath( arg ) )
            continue
       
        # Look for the file in our search path
        path = findInSearchPath( arg, searchPath )
        if path:
            new_argv.append( path )
            continue

        new_argv.append( arg )

    return new_argv


if __name__ == '__main__':
    #home_source = os.path.join( os.path.expanduser("~"), "core.rackspace.com" )
    #searchPath = [home_source, "/home/core/core.rackspace.com", "/home/core",]
    #args = buildNewArgs( replaceFilePaths( sys.argv[1:], searchPath ) )

    args = buildNewArgs( sys.argv[1:] )
    os.execvpe( gvim_path, args, dict(os.environ) )
    #print gvim_path, args
