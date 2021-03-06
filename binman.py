#!/usr/bin/env python

import os
import pisi.api
import shutil
import sys
from pisi.file import File

from configobj import ConfigObj

import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SocketServer import ThreadingMixIn

class AsyncXMLRPCServer(ThreadingMixIn,SimpleXMLRPCServer): pass

from deltafise import produce_deltas_for_directory

def redirect_io (stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
    stdin_ = open (stdin, "r")
    stdout_ = open (stdout, "a+")
    stderr_ = open (stderr, "a+")
    
    os.dup2 (stdin_.fileno(), sys.stdin.fileno())
    os.dup2 (stdout_.fileno(), sys.stdout.fileno())
    os.dup2 (stderr_.fileno(), sys.stderr.fileno())
    
class BinMan:
    def __init__(self, configFile):
        self.config = ConfigObj (configFile)
        self.incoming_dir = self.config ["Repository"]["Incoming"]
        comp_type = self.config ["Repository"]["IndexCompression"]
        self.index_compression = File.COMPRESSION_TYPE_XZ if comp_type == "xz" else File.COMPRESSION_TYPE_BZ2
        self.server = AsyncXMLRPCServer ((self.config["Controller"]["Address"], int(self.config["Controller"]["Port"])))
        self.server.register_introspection_functions()
        self.server.register_instance (self)
        
        self.repo_dir = self.config ["Repository"]["BaseDirectory"]
        
    def _serve (self):
        self.server.serve_forever ()

    def pending_count (self):
        count = 0
        for item in os.listdir (self.incoming_dir):
            if item.endswith (".pisi"):
                count += 1
        return count
        
    def process_incoming (self):
        ''' Process all packages in the scanDir and organise them properly '''
        if not os.path.exists (self.incoming_dir):
            print "Directory not found: %s" % self.incoming_dir
            sys.exit (1)

        searchList = list()
        print "Scanning current working directory for .pisi files"
                    
        for potential in os.listdir (self.incoming_dir):
            if potential.endswith (".pisi") and not potential.endswith (".delta.pisi"):
                fPath = os.path.join (self.incoming_dir, potential)
                searchList.append (fPath)
                
        total = len(searchList)
        count = 0
        for item in searchList:
            count += 1
            print "Scanning %d of %d: %s" % (count, total, item)
            meta,files = pisi.api.info (item)
            
            source = meta.source
            
            source_name = source.name.lower ()
            if source_name.startswith ("lib"):
                # Handle lib* differently
                base_dir = source_name [:4]
            else:
                base_dir = source_name[0]
            
            arch = meta.package.architecture # Not yet needed
            full_dir_name = "%s/%s" % (base_dir, source_name)
            
            path = os.path.join (self.repo_dir, full_dir_name)
            possible_item = os.path.join (path, item.split("/")[-1])
            if os.path.exists (possible_item):
                print "Skipping inclusion of already included package: %s" % item
                continue
            if not os.path.exists (path):
                os.makedirs (path)
            shutil.move (item, path)
        return True
                        
    def index (self, inputs=["."]):
        ''' Pisi index '''
        pisi.api.index(inputs,
                       output=os.path.join(self.repo_dir, "pisi-index.xml"),
                       skip_sources=True,
                       skip_signing=True,
                       compression=self.index_compression)
        return True

    def produce_deltas (self):
        produce_deltas_for_directory (self.repo_dir)
        return True

    def serve_forked (self):
        print "Running"
        try:
            pid = os.fork ()
            if pid > 0: sys.exit(0) # Exit first parent.
        except OSError, e:
            print e
            sys.exit (1)
        
        os.umask (0)
        os.setsid ()
        
        # Fork again, daemonize
        try:
            pid = os.fork ()
            if pid > 0:
                print "SLAVE_PID=%d" % pid
                sys.exit(0) # Exit second parent.
        except OSError, e:
            print e
            sys.exit (1)
            
        # All setup to go
        redirect_io ()
        self._serve ()
    		
def print_help (commands):
		print "Commands:"
		longest_name = 0
		offset = "\t"
 		for cmd in commands:
			# First loop, determine the longest name
			if len(cmd) > longest_name:
				longest_name = len(cmd)
				
		# Alphabetically sort the command list
		keyset = commands.keys()
		keyset.sort ()		
		for cmd in keyset:
			spaces = ""
			if len(cmd) < longest_name:
				# If this isn't the longest name, add spaces until they line up
				spaces = (longest_name - len(cmd)) * " "		
			print "%s%s%s - %s" % (offset, spaces, cmd, commands[cmd][0])



if __name__ == "__main__":
    if not os.path.exists ("repo.conf"):
        print "Please use from a valid repository"
        sys.exit (1)
        
    repo = BinMan ("repo.conf")

    Commands = { 'index' : ( 'index the repository', repo.index ), \
                 'process': ('process the incoming queue', repo.process_incoming), \
                 'help': ('display this help message', print_help),
                 'runserver': ('run the binman service', repo.serve_forked), \
                 'delta': ('create deltas for the repository', repo.produce_deltas) }

    # Check the command
    if len(sys.argv) < 2:
        print "%s - repository management\n" % sys.argv[0]
        print_help (Commands)
        sys.exit (1)
        
    keyword = sys.argv[1]
    if keyword in Commands:
        # Store a pointer to the function in the Commands list for the keyword
        # and execute it, saves having a lot of if/else statements
        command = Commands[keyword][1]
        if command == print_help:
            command (Commands)
        else:
            command ()
    else:
        print "Unknown command: %s" % keyword
        print_help (Commands)

