import re
import os
import commands

return_code = 0

class Struct(object):
    def __init__(self, **args):
        for attr in args:
            setattr(self, attr, args[attr])

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

def runCmd(cmd, working_dir='', exceptions=False, capture=False ):
    global return_code
    cwd = ""

    # run command from a specific directory
    if working_dir != '':
        # Save our current working dir
        cwd = os.getcwd()
        # Move to the working dir requested
        os.chdir( working_dir )

    if capture:
        (return_code, output) = commands.getstatusoutput(cmd)
        if (exceptions) and (return_code != 0):
                raise Exception( "Command: '%s' returned non zero result" % (cmd) )
        if working_dir != '': os.chdir( cwd )
        return output

    return_code = os.system( cmd )
    if working_dir != '': os.chdir( cwd )

    if (exceptions) and (return_code != 0):
            raise Exception( "Command: '%s' returned non zero result" % (cmd) )
    return return_code

def quoteArgs( argv ):
    args = []
    for arg in argv:
        # Quote args with spaces in them
        if re.search(  ' ', arg):
            args.append( ("\"%s\"" % arg) )
            continue
        args.append(arg)
    return " ".join(args)

def removeArgs( argv, remove ):
    args = []
    for arg in argv:
        # Skip these arguments
        if arg in remove:
            continue
        args.append(arg)
    return args

def safeArgs( args ):
    argv = []
    for i in range(0, 15):
        try:
            argv.append(args[i])
        except:
            argv.append('')
    return argv

