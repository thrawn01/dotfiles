#! /usr/bin/python
import sys
import re
import os
import commands
import traceback

# Add ~/bin/lib to the python search path
sys.path.append( os.path.join( os.path.expanduser("~"), "bin/lib" ) )
import utils
from repository import Svn
from pipe import Pipe

version = "1.0"
class SvnProxy(object):
    def __init__(self):
        self.repo = "https://source.core.rackspace.com/svnroot"
        self.branch = ''
        self.project = ''
        self.url = ''
        self.fs_path = None
        self.my_name = None

    def buildSafeArguments(self):
        argv = []
        for i in range(0, 15):
            try:
                argv.append(sys.argv[i])
            except:
                argv.append('')

        # Save the name of our program
        self.my_name = argv[0]
        argv[0] = ''

        return argv

    def usage(self, msg = ""):
        if msg != "": print " -- ", msg
        print """
        Usage: svn (checkout|diff|log|automerge|rollback|revert all)

            This a is small script to assist SVN users with managing 
            branches, merging, and un-merging

            checkout <project> <branch>
                Checks out a branch from a specified project 
                    $ svn checkout core NTL-38
                    $ svn checkout core NTL-38 local-name
                    $ svn checkout maintcal trunk

            diff
                Colorizes the output if colordiff is installed
                    $ svn diff
                    $ svn diff file1 file2
                    $ svn diff `svn-url core releases core-release-2010.02.09-1200` `svn-url core releases core-release-2010.02.23-1200`
            
            changes
                Shows all changes made to the current branch since the branch was created
                    $ svn changes
                    $ svn changes https://source.core.rackspace.com/svnroot/core/branches/NTL-38
                    $ svn changes core NTL-38

            log 
                Outputs the log and pipes the output to less also
                    $ svn log 
                    $ svn log https://source.core.rackspace.com/svnroot/core/branches/NTL-38

                    # Is the same as '--stop-on-copy -v'
                    $ svn log branch 
                    $ svn log branch https://source.core.rackspace.com/svnroot/core/branches/NTL-38

            automerge
                Attempts to merge in a branch by looking thru the log
                    $ svn automerge NTL-38
                    $ svn automerge https://source.core.rackspace.com/svnroot/core/branches/NTL-38

            unmerge
                Creates an un-merge patch file to un-merges the requested revision numbers
                    $ svn automerge 54573 54472 54449 

            rollback
                Attempts to rollback the last revision committed, or specifed revision
                    $ svn rollback 
                    $ svn rollback 47925
            
            revert all
                Reverts all the changes in the current branch
                    $ svn revert all

            url
                Produces a url from the project and branch names
                    $ svn changes `svn url core NTL-80`

            branch
                Creates a new branch from the current release
                    $ svn branch core SUP-179

            show
                Shows the changes related to a specific revision
                    $ svn show r52608
                    $ svn show 52608

         Written by: Derrick J. Wippler 
         Version: 1.3
        """
        return -1

    def shortPath(self, path ):
        """ Return a short version of the path passed """
        return re.search( '/source.core.rackspace.com\/(.*)/', path ).group(0)

    def removeArgs(self, argv, remove ):
        args = []
        for arg in argv:
            # Skip these arguments
            if arg in remove:
                continue
            args.append(arg)
        return args
           
    def quoteArgs(self, argv):
        args = []
        for arg in argv:
            # Quote args with spaces in them
            if re.search(  ' ', arg):
                args.append( ("\"%s\"" % arg) )
                continue

            args.append(arg)

        return " ".join(args)

    def findSvn(self):
        locations = [ "/usr/local/bin/svn", "/usr/bin/svn" ]

        for file in locations:
            if os.path.exists( file ):
                return file
        return False        

    def buildColorDiff(self):
        pipe = Pipe(['/bin/which','colordiff']).run()
        if pipe.return_code == 1:
            return ''
        return " | %s " % pipe.output()

    def clean(self, svn_path):
        cleaned = []
        self.parseCurrentPath( svn_path )
        output = utils.runCmd( "%s status" % svn_path, capture=True )
        for line in output.split('\n'):
            if re.match( "^\?", line ):
                file = re.sub( "^\? *", "", line)
                print "-- Cleaning  %s" % file 
                utils.runCmd( "rm %s" % file )
        return 0

    def arguments(self, call):
        """ Quote arguments that have spaces, remove the name of 
        our script and remove the argument specific by 'call' """
        return self.quoteArgs( self.removeArgs( sys.argv, [ sys.argv[0], call ] ) ) 

    def buildLessPipe(self, color_diff=""):

        # Don't pipe to colordiff or less if the user is piping our output
        if not sys.stdout.isatty():
            return " 2>&1 "

        # Are we asking for color diff?
        if color_diff == True:
            color_diff = self.buildColorDiff()

        return (" 2>&1 %s | less -S -R" % (color_diff))

    def buildUrl(self, fmt_string=None):
        return (fmt_string % {'repo':self.repo, 'project':self.project, 
                'branch':self.branch, 'fs_path':self.fs_path } )

    def parseCurrentPath(self, svn_path ):
        result = Svn.parseUrl( Svn.discoverUrl( svn_path, os.getcwd() ) )
        if result == None:
            raise Exception( "Could not get path of current checkout, " +\
                "Are you running this command inside a valid svn checkout?");

        self.repo = result['repo']
        self.branch = result['branch']
        self.project = result['project']
        self.fs_path = result['fs-path']
        self.url = result['url']

    def getBranchRoot(self):
        if self.fs_path == None:
            raise Exception( "Please call parseCurrentPath() before calling getBranchRoot()" )
        
        chgdir = ''
        dirs = self.fs_path.split('/')
        for i in range(0, (len(dirs)-1)):
            chgdir = chgdir + "../"
        return chgdir

    def runInBranchRoot(self, cmd, capture=False ):
        chgdir = self.getBranchRoot()
        return utils.runCmd( cmd, working_dir=chgdir, capture=capture );

    def getChangedFiles(self, svn_path ):
        print "-- Running 'svn status' ..."
        result = self.runInBranchRoot( ("%s status" % svn_path), capture=True )
        changed = []
        for line in result.split('\n'):
            if re.search( "^M", line ):
                changed.append( line.rstrip('\n') )
        return changed

    def findPrevRevision(self, svn_path, rev=None ):
        last = capture = False
        prev_rev = ""

        # If we are looking for the first previous revision
        if rev == None:
            last = True

        lines = commands.getoutput( ( "%s log --stop-on-copy --limit 50" % svn_path ) ).split('\n')
        for line in lines:

            # If we should be capturing the log entry
            if capture != False:
                if re.search( "----", line):
                    break
                capture = capture + line + "\n"
                continue

            # If this is a revision number
            if re.search("^r\d*", line ):
                curr_rev = re.search("^r(\d*)", line ).groups()[0]
                if curr_rev == rev:
                    # Found the Revision to rollback
                    last = True

                # Record this revision
                if last:
                    prev_rev = re.search("^r(\d*)", line ).groups()[0]
                    capture = line + "\n"

        if prev_rev == "":
            return (0, "")

        return (prev_rev, capture)

    def rollback(self, svn_path, argv ):
        print "-- Running Update to grab the latest history..."
        self.parseCurrentPath( svn_path )
        self.runInBranchRoot( ("%s update" % svn_path) )

        if argv[2] != '':
            (rev, log) = self.findPrevRevision( svn_path, rev=argv[2] )
        else:  
            (rev, log) = self.findPrevRevision( svn_path )

        if rev == 0:
            print " -- Couldn't find the previous revision, " +\
                    "Try running this command from a directory higher up in the build system"
            return 0

        print "------------------------------------------------------------------------"
        print log
        print "------------------------------------------------------------------------"

        ans = utils.YesNo( ("Roll Back Revision %s (Y/N) ?" % rev), default="N" )
        if ans:
            cmd = ( "%s merge -r %s:%s ." % ( svn_path, rev, (int(rev)-1 ) ) )
            print "--", cmd
            return self.runInBranchRoot( cmd )
        return -1

    def unmerge(self, svn_path, argv ):
        self.parseCurrentPath( svn_path )
        args = self.remove( argv, [ 'unmerge', '' ] )
        # Revsions should be in reverse order, to make for clean un-merge
        args.sort( reverse=True )
        revisions = []
        print " -- Unmerging the following -- "
        for arg in args:
            print "Revision: %s" % arg
            (rev, log) = self.findPrevRevision( svn_path, rev=arg )
            print "------------------------------------------------------------------------"
            print log
            print "------------------------------------------------------------------------"
            revisions.append( (rev, log ) )
        
        file = ( "un-merge-%s.patch" % "-".join( args ) )
        print "\n\n"
        ans = utils.YesNo( ( "Create Un-merge file %s (Y/N) ?" % file ), default="N" )
        if ans:
            for rev,log in revisions:
                cmd = ( "%s diff -r %s:%s >> %s" % ( svn_path, rev, ( int(rev)-1 ), file ) )
                self.runInBranchRoot( cmd )
            print ( "-- now run 'patch -p0 < %s'" % file )
            print "-- Remember to ADD deleted or moved files to svn after the patch"
        return -1

    def remove(self, list, keys):
        """ Remove all occurances of the keys from the list """
        for key in keys:
            while key in list:
                list.remove(key)
        return list

    def show(self, svn_path, argv ):

        # Check we have enough arguments
        if argv[2] == '':
            print "-- Please specify a revision to show"
            return -1

        #print "-- Running Update to grab the latest history..."
        self.parseCurrentPath( svn_path )
        #self.runInBranchRoot( ("%s update" % svn_path) )

        (rev, log) = self.findPrevRevision( svn_path, rev=argv[2].strip('r') )
        if rev == 0:
            rev = argv[2]
        print "------------------------------------------------------------------------"
        print log
        print "------------------------------------------------------------------------"
    
        # Remove all the options we know about, anything else gets passed along
        options = " ".join( self.remove( argv, [ 'show', argv[2] ] ) )
        pipe = app.buildLessPipe( color_diff=True )

        cmd = ( "%s diff %s -r %s:%s . %s" % ( svn_path, options, (int(rev)-1 ), rev, pipe ) )
        print "--", cmd
        return self.runInBranchRoot( cmd )
        
    def automerge(self, svn_path, argv ):
        url = ""

        # Check we have enough arguments
        if argv[2] == '':
            print "-- Please specify a branch or url to merge"
            return -1

        self.parseCurrentPath( svn_path )

        # Is the current checkout clean?
        if len(self.getChangedFiles( svn_path )) != 0:
            print "-- Current checkout is not clean, commit or "+\
            "revert changes in the current checkout and try again"
            return -1

        if not Svn.isValidUrl( argv[2] ):
            # Build the merge target url
            self.branch = argv[2]
            url = self.buildUrl("%(repo)s/%(project)s/branches/%(branch)s") 
        else:
            # The user passed us a path
            url = argv[2]
        
        # Grab the begining and ending revision numbers
        rev = Svn.getBranchRevisionNumbers( svn_path, url )

        # Build the merge command 
        options = ( "merge -r %s:%s %s" % (rev.beginRev, rev.endRev, url) )
        cmd =  ("%(svn_path)s %(options)s" % locals())
        print "-- ", cmd
        return self.runInBranchRoot( cmd )

    def urlFromArguments(self, argv):
        # If nothing was provided, return nothing
        if argv[2] == '':
            return ''

        # If we were passed something that is NOT a SVN checkout url
        if not Svn.isValidUrl( argv[2] ):
            self.project = argv[2]
            if argv[3] == '':
                print ( "-- Please specify a branch along with the project name '%s'" % self.project )
                sys.exit(-1)

            if argv[3] == 'trunk':
                self.branch = "trunk"
            else:
                self.branch = 'branches/%s' % argv[3]
            return self.buildUrl("%(repo)s/%(project)s/%(branch)s")
        return argv[2]
        
    def checkout(self, argv):
        argv[2] = self.urlFromArguments(argv)
        argv[3] = ''

    def revertAll(self, svn_path):
        self.parseCurrentPath( svn_path )
        self.runInBranchRoot( ("%s revert . --recursive" % svn_path) )

    def changes(self, svn_path, argv ):
        options = ""

        self.parseCurrentPath( svn_path )
        if self.branch == 'trunk':
            print "-- Can't run 'changes' command in trunk/"
            sys.exit(-1)

        svn = Svn()

        # Translate the arguments
        argv[2] = self.urlFromArguments(argv)
        argv[3] = ''

        if argv[2] != '':
            # The user provided a path to diff
            rev = svn.getBranchRevisionNumbers( svn_path, argv[2] )
            options = ("-r %s:%s" % (rev.beginRev, rev.endRev))
            argv[1] = 'diff'
        else:
            # Diffing the current checkout
            rev = svn.getBranchRevisionNumbers( svn_path, svn.path )
            options = ("-r %s:%s %s" % (rev.beginRev, rev.endRev, svn.path))
            argv[1] = 'diff'
        return options


    def exists(self, svn_path, path):
        cmd = ("%(svn_path)s ls %(path)s" % locals() )
        output = utils.runCmd( cmd, capture=True )
        if re.search( 'non-existent', output ):
            return False
        return True

    def createBranch(self, svn_path, argv):
        if argv[3] == '':
            print "-- Not enough arguments to create a new branch"
            sys.exit(-1)

        self.project = argv[2]
        self.branch = argv[3]
        self.jira = argv[4]

        if self.jira == '':
            ans = utils.YesNo( ("Is '%s' also the jira name (Y/N) ?" % self.branch) , default='Y' )
            if ans: self.jira = self.branch

        # Build the path to the branch to create
        branch_path = self.buildUrl("%(repo)s/%(project)s/branches/%(branch)s")
        print "-- Checking for Pre-existing branch"
        if self.exists( svn_path, branch_path ):
            print ("-- Branch Already exists: %s" % (branch_path) )

        # Build path to current production tag
        trunk_path = self.buildUrl( "%(repo)s/%(project)s/tags/current-production-tag" )
        comment = ("%s: Created Branch '%s'" % (self.jira, branch_path) )
        cmd = ( "%s copy %s %s -m \"%s\"" % (svn_path, trunk_path, branch_path, comment ) )
        print "-- ", cmd
        utils.runCmd( cmd )

if __name__ == '__main__':
    pipe = ""
    options = ""

    try:
        app = SvnProxy()
        argv = app.buildSafeArguments()

        svn_path = app.findSvn()
        if not svn_path:
            print "-- Unable to find svn binary, run 'which svn'"
            sys.exit(-1)

        # User passed no argument
        if argv[1] == '':
            sys.exit( utils.runCmd( svn_path ) )

        # User passed an argument
        if argv[1] == 'help':
            sys.exit( app.usage() )

        # Are we checking out a branch
        if argv[1] == 'checkout' or argv[1] == 'co':
            app.checkout( argv )
                
        # Apply color to the diff to improve readability
        if argv[1] == 'diff':
            pipe = app.buildLessPipe( color_diff=True )

        # Get the log of the current task
        if argv[1] == 'log':
            # Show a log of only the changes since we made this branch
            if argv[2] == 'branch':
                options = "--limit 50 --stop-on-copy -v"
                argv[2] = ''
            else: 
                options = "--limit 50"
            # Pipe to less, if appropriate
            pipe = app.buildLessPipe()

        # Show a diff of only the changes since we made this branch
        if argv[1] == 'changes':
            options = app.changes( svn_path, argv )
            pipe = app.buildLessPipe( color_diff=True )

        if argv[1] == 'revert':
            if argv[2] == 'all':
                sys.exit(app.revertAll( svn_path ))

        if argv[1] == 'automerge':
            sys.exit( app.automerge( svn_path, argv ) )

        if argv[1] == 'rollback':
            sys.exit( app.rollback( svn_path, argv ) )

        if argv[1] == 'unmerge':
            sys.exit( app.unmerge( svn_path, argv ) )

        if argv[1] == 'branch':
            sys.exit( app.createBranch( svn_path, argv) )

        if argv[1] == 'clean':
            sys.exit( app.clean( svn_path ) )

        if argv[1] == 'url':
            print app.urlFromArguments( argv )
            sys.exit( 0 )

        if argv[1] == 'show':
            sys.exit( app.show( svn_path, argv ) )

        # Fall Thru to svn if we didn't match any commands
        args = app.quoteArgs( app.removeArgs( argv, [ argv[0], '' ] ) )
        print "-- %(svn_path)s %(args)s %(options)s %(pipe)s" % locals()
        sys.exit( utils.runCmd( ( "%(svn_path)s %(args)s %(options)s %(pipe)s" % locals() ) ) )

    except SystemExit,e:
        sys.exit()

    #except Exception, e:
    #    traceback.print_exc()
    #    print e
    #    sys.exit(-1)

