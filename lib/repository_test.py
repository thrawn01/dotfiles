#!/usr/bin/env python

# Run Individual Tests with 
# nosetests repository_test:RepositoryTest.testLs

import os 
import sys
import shutil
import tempfile
import time
import unittest

# Add the local directory to the python library path
basedir, bin = os.path.split(os.path.dirname(os.path.abspath(sys.argv[0])))
sys.path.append("%s" % basedir)

from repository import Repository

class RepositoryTest(unittest.TestCase):

    def createRepo(self, dir, repo_name ):
        cwd = os.getcwd()
        os.chdir( dir )
        os.system( "svnadmin create --fs-type fsfs %s" % repo_name )
        os.chdir( cwd )

    def createFullRepo(self):
        self.createTestDir( "/tmp/tests" )
        self.createRepo( "/tmp/tests", 'svnroot' )
        repo = Repository.fromUrl( "file:///tmp/tests/svnroot" )
        self.assertEquals( repo.mkdir( "core" ), 1 )
        self.assertEquals( repo.mkdir( "core/trunk" ), 2 )
        self.assertEquals( repo.mkdir( "core/tags" ), 3 )
        self.assertEquals( repo.mkdir( "core/tags/current-production-tag" ), 4 )
        self.assertEquals( repo.mkdir( "core/branches" ), 5 )
        self.assertEquals( repo.ls( "core" ), ['branches/', 'tags/', 'trunk/'] )

    def createTestDir(self, dir):
        self.cleanUp()
        os.makedirs( dir )
        self.assertExists( dir )

    def cleanUp(self):
        try:
            os.system( "rm -rf /tmp/tests" )
        except OSError, e:
            pass
    
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def assertExists(self, file):
        if not os.path.exists(file):
            self.fail(("Path '%s', should exist" % (file)))

    def assertNotExists(self, file):
        if os.path.exists(file):
            self.fail(("Path '%s', should NOT exist" % (file)))

    def testJoinPath(self):
        repo = Repository.fromUrl( "https://source.core.rackspace.com/svnroot/core/branches/SUP-179" )
        self.assertEquals( repo.joinUrlPath( repo.url, "python" ), 
                "https://source.core.rackspace.com/svnroot/core/branches/SUP-179/python" )
        self.assertEquals( repo.joinUrlPath( repo.url, "python", "lib" ), 
                "https://source.core.rackspace.com/svnroot/core/branches/SUP-179/python/lib" )
        self.assertEquals( repo.joinUrlPath( repo.url, None ), 
                "https://source.core.rackspace.com/svnroot/core/branches/SUP-179" )

    def testParseUrl(self):
        repo = Repository.fromUrl( "https://source.core.rackspace.com/svnroot/test-svn" )
        result = repo.parseUrl( "https://source.core.rackspace.com/svnroot/core/branches/test_branch" )
        self.assertEquals( result['repo'], 'https://source.core.rackspace.com/svnroot' )
        self.assertEquals( result['branch'], 'test_branch' )
        self.assertEquals( result['project'], 'core' )
        self.assertEquals( result['fs-path'], '' )
        self.assertEquals( repo.isValidUrl( result['url'] ), True )

        result = repo.parseUrl( "https://source.core.rackspace.com/svnroot/core/trunk" )
        self.assertEquals( result['repo'], 'https://source.core.rackspace.com/svnroot' )
        self.assertEquals( result['branch'], 'trunk' )
        self.assertEquals( result['project'], 'core' )
        self.assertEquals( result['fs-path'], '' )
        self.assertEquals( repo.isValidUrl( result['url'] ), True )
        self.assertEquals( repo.isValidUrl( 'blah' ), False )
        
        result = repo.parseUrl( "file:///tmp/tests/svnroot" )
        self.assertEquals( result['repo'], 'file:///tmp/tests/svnroot' )
        self.assertEquals( result['branch'], '' )
        self.assertEquals( result['project'], '' )
        self.assertEquals( result['fs-path'], '' )

        result = repo.parseUrl( "https://source.core.rackspace.com/svnroot/core/trunk/python/lib" )
        self.assertEquals( result['repo'], 'https://source.core.rackspace.com/svnroot' )
        self.assertEquals( result['branch'], 'trunk' )
        self.assertEquals( result['project'], 'core' )
        self.assertEquals( result['fs-path'], '/python/lib' )

        result = repo.parseUrl( "https://source.core.rackspace.com/svnroot/core/branches/test_branch/python/lib" )
        self.assertEquals( result['repo'], 'https://source.core.rackspace.com/svnroot' )
        self.assertEquals( result['branch'], 'test_branch' )
        self.assertEquals( result['project'], 'core' )
        self.assertEquals( result['fs-path'], '/python/lib' )

        result = repo.parseUrl( "https://source.core.rackspace.com/svnroot/core/tags/NTL-38/python/lib" )
        self.assertEquals( result['repo'], 'https://source.core.rackspace.com/svnroot' )
        self.assertEquals( result['branch'], 'NTL-38' )
        self.assertEquals( result['project'], 'core' )
        self.assertEquals( result['fs-path'], '/python/lib' )

    def testFromUrl(self):
    
        repo = Repository.fromUrl( "https://source.core.rackspace.com/svnroot/core/branches/SUP-179" )
        self.assertEquals( repo.branch, "SUP-179" )
        self.assertEquals( repo.url, "https://source.core.rackspace.com/svnroot/core/branches/SUP-179" )
        self.assertEquals( repo.type, 'svn' )
        self.assertEquals( repo.path, os.getcwd()  )

        repo = Repository.fromUrl( "file:///tmp/tests/svnroot" )
        self.assertEquals( repo.branch, "svnroot" )
        self.assertEquals( repo.url, "file:///tmp/tests/svnroot" )
        self.assertEquals( repo.type, 'svn' )
        self.assertEquals( repo.path, os.getcwd()  )

    def testMkDir(self):

        self.createTestDir( "/tmp/tests" )
        self.createRepo( "/tmp/tests", 'svnroot' )

        repo = Repository.fromUrl( "file:///tmp/tests/svnroot" )

        self.assertEquals( repo.mkdir( "trunk" ), 1 )
        self.assertEquals( repo.mkdir( "tags" ), 2 )
        self.assertEquals( repo.mkdir( "branches" ), 3 )
        self.assertEquals( repo.ls( ), ['branches/', 'tags/', 'trunk/'] )

        repo = Repository.fromUrl( "file:///tmp/svnroot/" )
        self.assertRaises( Exception, repo.mkdir, "trunk" )

    def testLs(self):
        self.createFullRepo()
        repo = Repository.fromUrl( "file:///tmp/tests/svnroot" )
        self.assertEquals( repo.ls( 'core' ), ['branches/', 'tags/', 'trunk/'] )
        self.assertEquals( repo.ls( 'core/branches' ), [] )
        self.assertEquals( repo.ls( 'core/non-existant-dir' ), [] )
        self.assertRaises( Exception, repo.ls, 'core/non-existant-dir', exceptions=True )
        self.assertEquals( repo.exists( "core/non-existant-dir") , False )
        self.assertEquals( repo.exists( "core/branches") , True )
    
        repo = Repository.fromUrl( "file:///tmp/tests/svnroot/core/trunk" )
        self.assertEquals( repo.ls( ), ['core/'] )
        self.assertEquals( repo.ls( 'core' ), ['branches/', 'tags/', 'trunk/'] )

    def testCheckout(self):
        self.createFullRepo()
        repo = Repository.fromUrl( "file:///tmp/tests/svnroot/core/trunk" )
        repo.path = "/tmp/tests/trunk"
        repo.checkout()
        self.assertExists( "/tmp/tests/trunk/.svn" )
        return repo

    def testFromPath(self):
        self.testCheckout()
        repo = Repository.fromPath( "/tmp/tests/trunk" )
        self.assertEquals( repo.branch, "trunk" )
        self.assertEquals( repo.url, "file:///tmp/tests/svnroot/core/trunk" )
        self.assertEquals( repo.path, "/tmp/tests/trunk" )

    def testCommit(self):
        repo = self.testCheckout()
        os.system( "touch /tmp/tests/trunk/newFile" )

        repo.add( "/tmp/tests/trunk/newFile" )
        self.assertEquals( repo.commit( "Added new file 'newFile'" ), 6 )

    def testUpdate(self): 
        repo = self.testCheckout()

        repo.mkdir( "testDir" )
        repo.update()
        self.assertExists( "/tmp/tests/trunk/testDir" )

    def testCreateBranch(self):
        self.createFullRepo()
        repo = Repository.fromUrl( "file:///tmp/tests/svnroot/core/trunk" )

        repo.createBranch( project="core", branch="test-branch" )
        self.assertEquals( repo.ls( 'core/branches' ), ["test-branch/"] )

        repo.createBranch( project="core", branch="SUP-179", jira="SUP-179" )
        self.assertEquals( repo.ls( 'core/branches' ), ["SUP-179/", "test-branch/"])
        return repo

    def testRemove(self):
        repo = self.testCreateBranch()
        self.assertEquals( repo.remove( "core/branches/test-branch" ), 8 )
        self.assertEquals( repo.ls( 'core/branches' ), ['SUP-179/'] )
        self.assertEquals( repo.remove( "core/branches/SUP-179" ), 9 )
        self.assertEquals( repo.ls( 'core/branches' ), [] )

    def testGetBranchRevisionsNumbers(self):
        self.createFullRepo()
        repo = Repository.fromUrl( "file:///tmp/tests/svnroot/core/trunk" )
        repo.createBranch( project="core", branch="SUP-179" )

        repo = Repository.fromUrl( "file:///tmp/tests/svnroot/core/branches/SUP-179" )
        repo.path = "/tmp/tests/SUP-179"
        repo.checkout()

        os.system( "touch /tmp/tests/SUP-179/file1" )
        repo.add( "/tmp/tests/SUP-179/file1" )
        repo.commit( "Added file1" )
        os.system( "touch /tmp/tests/SUP-179/file2" )
        repo.add( "/tmp/tests/SUP-179/file2" )
        repo.commit( "Added file1" )
        repo.update()

        result = repo.getBranchRevisionNumbers( repo.svn_path, repo.path )

        self.assertEquals( result.beginRev, 6 )
        self.assertEquals( result.endRev, 8 )
        self.assertEquals( result.copiedFrom, "/core/tags/current-production-tag" )
        self.assertEquals( result.copiedRev, 5 )

        result = repo.getBranchRevisionNumbers( repo.svn_path, "file:///tmp/tests/svnroot/core/branches/SUP-179" )
        self.assertEquals( result.beginRev, 6 )
        self.assertEquals( result.endRev, 8 )
        self.assertEquals( result.copiedFrom, "/core/tags/current-production-tag" )
        self.assertEquals( result.copiedRev, 5 )
        self.assertRaises( Exception, repo.getBranchRevisionNumbers, repo.svn_path, "file:///tmp/tests/root/core/branches/SUP-179" )


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(RepositoryTest, "test"))
    unittest.TextTestRunner().run(suite)

