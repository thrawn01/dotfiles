#! /usr/bin/env python

from nova.auth import manager
import sys

def usage():
    print """
Usage: zip_credentials <project> <user> <password>
    Create a credential auth file

    Example:
        ./zipfile myProject MyUsername MyPass
        ./zipfile admin admin qwerty 

    Options:
         -h   This help message
"""
    return 0

def safeArgs( args ):
    argv = []
    for i in range(0, 15):
        try:
            argv.append(args[i])
        except:
            argv.append('')
    return argv

if __name__ == "__main__":

    args = safeArgs( sys.argv )

    if '-h' in args:
        sys.exit( usage() )
    
    if args[3] == '':
        sys.exit( usage() )
   
    auth_manager = manager.AuthManager()
    user = manager.User('1', args[2], None, args[3] , True)
    
    zip_file = auth_manager.get_credentials(user, args[1])
    with open('nova.zip', 'w') as f:
        f.write(zip_file)

