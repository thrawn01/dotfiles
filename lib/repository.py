import os
import re

# 'remote_procedure' might have been sent over ssh pipe
# with this script and is already in the namespace
try: Pipe
except NameError:
    # If not, Import it
    from pipe import Pipe

class Struct(object):
    def __init__(self, **args):
        for attr in args:
            setattr(self, attr, args[attr])

class Repository(object):

    def __init__(self, **args ):
        self.url = None
        self.branch = None
        self.type = None
        self.password = None
        self.username = None

        self.svn_path = self.findSvn()
         
        # Assume current working dir
        self.path = os.getcwd()

        for attr in args:
            setattr(self, attr, args[attr])

    def findSvn(self):
        locations = [ "/usr/local/bin/svn", "/usr/bin/svn", "/bin/svn" ]

        for file in locations:
            if os.path.exists( file ):
                return file
        return False        
        
    def runCmd(self, cmd, working_dir=None, exceptions=True ):
        cwd = ""

        # run command from a specific directory
        if working_dir:
            # Save our current working dir
            cwd = os.getcwd()
            # Move to the working dir requested
            os.chdir( working_dir )

        ret = os.system( cmd )
        if working_dir: os.chdir( cwd )
        if exceptions:
            if ret != 0:
                raise Exception( "Command: '%s' returned non zero result" % (cmd) )
        return ret

    # Implementation Specific
    def update(self): return None
    def checkout(self): return None
    def getUser(self): return None
    def getUrl(self): return None
    def getBranchName(self): return None
    def log(self, args): return None
    def createBranch(self, name): return None
    def ls(self, dir=None): return None
    def mkdir(self, dir): return None
    def remove(self, file): return None
    def add(self, file): return None
    def commit(self, comment): return None

    @classmethod
    def repoFactory(cls, url=None ):
        """ 
        Figure out what the branch name is, if we are not in a git repo, 
        prompt the user for a branch name 
        """

        # If we got a url
        if url:
            # Create a Repo object from the url passed
            return Repository.fromUrl( url )
        else:
            # Create a repo object from the path provided
            return Repository.fromPath( os.getcwd() )

        return None
        
    @classmethod
    def fromUrl(cls, url):

        # If this is a svn checkout
        if re.search( "(^http(s|)://|^file:///)", url):
            return Svn( url=url )

        # If this is a git url    
        if re.search( "\.git", url):
            # TODO: Not Implemented
            return None

        return None

    @classmethod
    def fromPath(cls, path):

        # If this is a svn checkout
        if os.path.exists( os.path.join( path, ".svn") ):
            return Svn( path=path )

        # If this is a git checkout    
        if os.path.exists( os.path.join( path, ".git") ):
            # TODO: Not Implemented
            raise Exception("Couldn't find a valid repo at '%s'" % (path))

        raise Exception("Couldn't find a repo at '%s'" % (path))

class Svn( Repository ):

    def __init__(self, **args ):
        Repository.__init__(self, **args)

        self.type = 'svn'
        self.url = self.getUrl()
        self.branch = self.getBranchName()

    @classmethod
    def isValidUrl(self, url):
        if re.search( "(^http(s|)://|^file:///)", url):
            return True
        return False

    def getBranchName(self):

        if not self.url:
            return None

        match = re.search( "(\/[A-Za-z0-9_\-\.]*(|\/|))$", self.url )
        if not match:
            Exception("Couldn't determine the branch name from the repo Url")

        return re.sub( '\/', '', match.group() )

    @classmethod
    def parseUrl(self, url ):
        result = ('','','')
        
        if not self.isValidUrl( url ):
            raise Exception( ("'%s' Is invalid for Svn(), url must start with http:// or https://" % url) )

        # This is a releases url
        if re.search( 'releases', url ):
            match = re.search( r"(.*)\/(.*)\/releases\/([A-Za-z0-9_\-]*)(\/.*|)", url )
            result = match.groups()
            
        # This is a branch url
        if re.search( 'branches', url ):
            match = re.search( r"(.*)\/(.*)\/branches\/([A-Za-z0-9_\-]*)(\/.*|)", url )
            result = match.groups()
        
        # This is a url to trunk
        if re.search( 'trunk', url ):
            match = re.search( r"(.*)\/(.*)\/(trunk)(\/.*|)", url )
            result = match.groups()

        # This is a branch url
        if re.search( 'tags', url ):
            match = re.search( r"(.*)\/(.*)\/tags\/([A-Za-z0-9_\-]*)(\/.*|)", url )
            result = match.groups()

        # This is a Basic url
        if (result[0] == '') and (re.search( 'svnroot', url )):
            match = re.search( r"(.*\/svnroot)(\/.*|)(\/.*|)(\/.*|)", url )
            result = match.groups()

        return { 'repo':result[0], 'project':result[1], 'branch':result[2], 'fs-path': result[3], 'url':url }

    def getUrl(self):
        """ Figures out what branch your in from 'svn info' """
       
        # If the object already knows, no need to look it up again
        if self.url:
            return self.url

        return self.discoverUrl( self.svn_path, self.path )

    @classmethod
    def discoverUrl(self, svn_path, path):

        cmd = [svn_path,'info', path]
        # Ask Svn
        pipe = Pipe( cmd ).run()
        if pipe.return_code == 1:
            raise Exception( "svn returned non-zero value '%s' - %s " % (" ".join(cmd), pipe.error()) )

        match = re.search( "URL: (.*)", pipe.output_buffer )
        if not match:
            return None
        
        # Remove URL: from the string
        return re.sub( "^URL: ", "", match.group())

    def getUser(self):
        svn_conf_dir = os.path.join( os.path.expanduser("~"), ".subversion/auth/svn.simple" )

        if not os.path.exists( svn_conf_dir ):
            return None

        for file in os.listdir( svn_conf_dir ):
            user = self.userFromAuthFile( os.path.join( svn_conf_dir, file ) )
            if user: return user.rstrip('\n')
        
    def userFromAuthFile( self, file ):
        """
        A simple algorithm for extracting the username from the .subversion/auth/svn.simple/* files
        
        Example file
        -------------
        V 66
        <https://source.core.rackspace.com:443> CORE Subversion Repository
        K 8
        username
        V 15
        derrick.wippler
        END
        ---------------
        """
        mark = 0

        fd = open( file , "r" )
        
        for line in fd:
            if mark == 2: return line
            if mark: mark = mark + 1
            if re.search( "username", line ): mark = 1
        return None

    def optionalCredentials(self):
        list = []
        if self.username:
            list.append( ("--username=%s" % (self.username)) )
        if self.password:
            list.append( ("--password=%s" % (self.password)) )
        return " ".join(list)

    def update(self):
        options = self.optionalCredentials()
        self.runCmd( ("%s update %s" % (self.svn_path,options)), self.path )

    def checkout(self):
        parent_dir = os.path.join( (os.path.split( self.path )[0:-1]) )[0]
        options = self.optionalCredentials()
        return self.runCmd( ("%s checkout %s %s %s" % (self.svn_path, options, self.url, self.path)), parent_dir )

    @classmethod
    def log(self, svn_path, path):
        pipe = Pipe([svn_path, 'log', '-v', '--stop-on-copy', path]).run()
        if pipe.return_code != 0:
            raise Exception( "Unable to retrieve log entry for path '%s'" % path )
        return pipe.yield_output()

    @classmethod
    def getBranchRevisionNumbers(self, svn_path, path):
        result = Struct( endRev='', beginRev='', copiedFrom='', copiedRev='' )

        # find the revision number
        for line in self.log( svn_path, path):
            if re.search( '^r\d*', line ):

                # Grab ending revision number	
                if result.endRev == "":
                    result.endRev = int(re.search( '^r(\d*)', line ).groups()[0])

                # last matched revision is beginning revision number
                result.beginRev = int(re.search( '^r(\d*)', line ).groups()[0])

            # Figure out what the branch was copied from 
            #( Should be the last copy we find in the log )
            if re.search( '\(from', line ):
                match = re.search( '\(from (.*):(\d*)\)', line ).groups()
                result.copiedFrom = match[0]
                result.copiedRev  = int(match[1])

        return result

    def notNone(self, item):
        if item: return True
        return False

    def joinUrlPath(self, *args):
        if len(args) == 1: return args[0]
        # Remove any args that are 'None'
        args = filter(self.notNone, args)
        return "/".join( args )

    def exists(self, path):
        try:
            self.ls(path, exceptions=True)
        except Exception, e:
            return False
        return True

    def createBranch(self, project, branch, jira="", verbose=False, comment=None):

        url_parsed = self.parseUrl( self.url )

        # Build the path to the branch to create
        branch_path = self.joinUrlPath( url_parsed['repo'], project, 'branches', branch )
        if self.exists( branch_path ):
            raise Exception( ("Branch Already exists: %s" % (branch_path) ) )

        # Build path to current production tag
        trunk_path = self.joinUrlPath( url_parsed['repo'], url_parsed['project'], "tags/current-production-tag" )

        if not comment:
            comment = ("%s: Created Branch '%s'" % (jira, branch_path) )

        if verbose:
            print ("-- svn copy %s %s -m %s" % (trunk_path, branch_path, comment) )

        pipe = Pipe([self.svn_path, 'copy', trunk_path, branch_path, '-m', comment ]).run()
        if pipe.error_buffer:
            raise Exception( pipe.error_buffer )
        print pipe.output_buffer
        return int(re.search( "Committed revision (\d*)", pipe.output_buffer).groups()[0])

    def ls(self, dir=None, exceptions=False):
        result = []
        repo = self.parseUrl( self.url )['repo']
        full_path = self.joinUrlPath( repo, dir )
        pipe = Pipe([self.svn_path, 'ls', full_path]).run()
        if exceptions and pipe.error_buffer:
            raise Exception( pipe.error_buffer )

        for line in pipe.yield_output():
            if line == "": continue
            result.append(line)
        return result 

    def mkdir(self, dir=None, jira="", comment=None):
        
        full_path = self.joinUrlPath( self.url, dir )
        if not comment:
            comment = ("%s: Created directory '%s'" % (jira, full_path) )

        pipe = Pipe([self.svn_path, 'mkdir', full_path, '-m', comment ]).run()
        if pipe.error_buffer:
            raise Exception( pipe.error_buffer )
        return int(re.search( "Committed revision (\d*)", pipe.output_buffer).groups()[0])

    def add(self, file):
        self.runCmd( "%s add %s" % ( self.svn_path, file ), working_dir=self.path, exceptions=True )

    def commit(self, comment=""):
        cwd = os.getcwd()
        os.chdir( self.path )
        pipe = Pipe([self.svn_path, 'commit', '-m', comment ]).run()
        os.chdir( cwd )

        if pipe.error_buffer:
            raise Exception( pipe.error_buffer )
        return int(re.search( "Committed revision (\d*)", pipe.output_buffer).groups()[0])

    def remove(self, file, comment=None, jira=""):
        repo = self.parseUrl( self.url )['repo']
        full_path = self.joinUrlPath( repo, file )
        if not comment:
            comment = ("%s: Removed '%s'" % (jira, full_path) )

        pipe = Pipe([self.svn_path, 'rm', full_path, '-m', comment]).run()
        if pipe.error_buffer:
            raise Exception( pipe.error_buffer )
        return int(re.search( "Committed revision (\d*)", pipe.output_buffer).groups()[0])

class Git( Repository ):

    def __init__(self, **args ):
        Repository.__init__(self, **args)

        if not re.search( "^ssh://", url):
            raise Exception( "Invalid Url for Git(), url must start with ssh://" )    
        
        self.type = 'git'

