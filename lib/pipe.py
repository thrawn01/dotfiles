
from errno import EINTR
from subprocess import Popen, PIPE
import os
import signal
import sys
import time
import traceback
import select
import re

BUFFER_SIZE = 1 << 16

class Pipe(object):
    """
    Starts a process and manages its input and output.
    
    Example Usage:

        # Simple usage
        # ----------------------------
        def findAskPass(cls):
            pipe = Pipe(['which','ssh-askpass']).run()
            if pipe.return_code == 1:
                return None
            return pipe.output()


        # Sending data thru the pipe 
        # ----------------------------
        pipe = Pipe(['/usr/bin/python'], verbose=True } )
        pipe.setInput( "print 'hi'" )
        pipe.run()

        self.assertEquals( "hi\n", pipe.output_buffer )
    
    """

    def __init__(self, cmd, verbose=False, stdin=None):
        self.cmd = cmd

        self.proc = None
        self.exceptions = []
        self.killed = False
        self.input_buffer = stdin
        self.output_buffer = ''
        self.error_buffer = ''
        self.iomap = None

        self.stdin = None
        self.stdout = None
        self.stderr = None

        self.stdin_user_handler = self.defaultStdinHandle
        self.stderr_user_handler = self.defaultStderrHandle

        self.verbose = verbose

    def error(self):
        return self.error_buffer.rstrip('\n')

    def output(self):
        return self.output_buffer.rstrip('\n')
    
    def yield_output(self):
        for line in self.output_buffer.split('\n'):
            yield line

    def defaultStdinHandle(self, buf):
        """ This is the default handle for stdin """
        self.output_buffer += buf

    def defaultStderrHandle(self, buf):
        """ This is the default handle for stderr """
        self.error_buffer += buf

    def appendInput(self,buf):
        """ Use this to append input that will be sent across the pipe to the receiving process """ 
        if self.input_buffer:
            self.input_buffer = self.input_buffer + buf
        else:
            self.setInput( buf )

    def setInput(self,buf):
        """ Use this to set input that will be sent across the pipe to the receiving process """ 
        self.input_buffer = buf

    def run(self):
        """ Runs the process and monitors the calling poll() to destribute the input as needed """
        
        if not self.iomap:
            self.iomap = IOMap()

        self.start(1)
    
        timeout = None
        while self.running():
            if timeout == None or timeout < 1:
                timeout = 1
            self.iomap.poll(timeout)

        return self

    def start(self, id, environ=None):
        """Starts the process and registers files with the IOMap."""
        
        if not environ:
            # Set up the environment.
            environ = dict(os.environ)

        if self.verbose:
            cmdLine = " ".join( self.cmd )
            print "Executing: ", cmdLine

        # Create the subprocess.
        self.proc = Popen(self.cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE,
                close_fds=True, preexec_fn=os.setsid, env=environ)
        if self.input_buffer:
            self.stdin = self.proc.stdin
            self.iomap.registerWrite(self.stdin.fileno(), self.handleStdin)
        else:
            self.proc.stdin.close()
        self.stdout = self.proc.stdout
        self.iomap.registerRead(self.stdout.fileno(), self.handleStdout)
        self.stderr = self.proc.stderr
        self.iomap.registerRead(self.stderr.fileno(), self.handleStderr)

    def kill(self):
        """Signals the sub process to terminate."""
        if self.proc:
            os.kill(-self.proc.pid, signal.SIGKILL)
            self.killed = True

    def running(self):
        """Finds if the process has terminated and saves the return code."""
        if self.stdin or self.stdout or self.stderr:
            return True
        if self.proc:
            self.return_code = self.proc.poll()
            if self.return_code is None:
                if self.killed:
                    return False
                else:
                    return True
            else:
                self.proc = None
                return False

    def handleStdin(self, fd, iomap):
        """Called when the process's standard input is ready for writing."""
        try:
            if self.input_buffer:
                bytes_written = os.write(fd, self.input_buffer)
                self.input_buffer = self.input_buffer[bytes_written:]
            else:
                self.closeStdin(iomap)
        except (OSError, IOError), e:
            if e.errno != EINTR:
                self.closeStdin(iomap)
                self.logException(e)

    def closeStdin(self, iomap):
        if self.stdin:
            iomap.unRegister(self.stdin.fileno())
            self.stdin.close()
            self.stdin = None

    def handleStdout(self, fd, iomap):
        """Called when the process's standard output is ready for reading."""
        try:
            buf = os.read(fd, BUFFER_SIZE)
            if buf:
                # execute the callback function here
                self.stdin_user_handler(buf)
            else:
                # If the read failed - TODO: Call the callback function?
                self.closeStdout(iomap)

        except (OSError, IOError), e:
            if e.errno != EINTR:
                self.closeStdout(iomap)
                self.logException(e)

    def closeStdout(self, iomap):
        """ Closes stdout on the iomap passed """
        if self.stdout:
            iomap.unRegister(self.stdout.fileno())
            self.stdout.close()
            self.stdout = None

    def handleStderr(self, fd, iomap):
        """Called when the process's standard error is ready for reading."""
        try:
            buf = os.read(fd, BUFFER_SIZE)
            if buf:
                # Call the standard error handler
                self.stderr_user_handler(buf)
            else:
                # If the read failed - TODO: Call the callback function?
                self.closeStderr(iomap)

        except (OSError, IOError), e:
            if e.errno != EINTR:
                self.closeStderr(iomap)
                self.logException(e)

    def closeStderr(self, iomap):
        """ Closes stderr on the iomap passed """
        if self.stderr:
            iomap.unRegister(self.stderr.fileno())
            self.stderr.close()
            self.stderr = None

    def logException(self, e):
        """Saves a record of the most recent exception for error reporting."""
        if self.verbose:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            exc = ("Exception: %s, %s, %s" %
                    (exc_type, exc_value, traceback.format_tb(exc_traceback)))
        else:
            exc = str(e)
        self.exceptions.append(exc)


class IOMap(object):
    """
    A manager for file descriptors and their associated handlers.
    The poll method dispatches events to the appropriate handlers.

    This is the poor mans thread event queue, Events are fired 
    when select tells us we have input
    """

    def __init__(self):
        self.read_map = {}
        self.write_map = {}

    def registerRead(self, fd, handler):
        """Registers an IO handler for a file descriptor for reading."""
        self.read_map[fd] = handler

    def registerWrite(self, fd, handler):
        """Registers an IO handler for a file descriptor for writing."""
        self.write_map[fd] = handler

    def unRegister(self, fd):
        """Unregisters the given file descriptor."""
        if fd in self.read_map:
            del self.read_map[fd]
        if fd in self.write_map:
            del self.write_map[fd]

    def poll(self, timeout=None):
        """Performs a poll and dispatches the resulting events."""
        if not self.read_map and not self.write_map:
            return
        rlist = list(self.read_map)
        wlist = list(self.write_map)
        try:
            rlist, wlist, _ = select.select(rlist, wlist, [], timeout)
        except select.error, e:
            errno, message = e.args
            if errno == EINTR:
                return
            else:
                raise
        for fd in rlist:
            handler = self.read_map[fd]
            handler(fd, self)
        for fd in wlist:
            handler = self.write_map[fd]
            handler(fd, self)

