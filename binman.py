#!/usr/bin/env python

import os
import pisi.api
import shutil
import sys
from pisi.file import File

from configobj import ConfigObj

class BinMan:
	def __init__(self, configFile):
		self.config = ConfigObj (configFile)
		self.incoming_dir = self.config ["Repository"]["Incoming"]
		comp_type = self.config ["Repository"]["IndexCompression"]
		self.index_compression = File.COMPRESSION_TYPE_XZ if comp_type == "xz" else File.COMPRESSION_TYPE_BZ2
		
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
			
			path = os.path.abspath (full_dir_name)
			if not os.path.exists (path):
				os.makedirs (path)
			shutil.move (item, path)
				
	def index (self, inputs=["."], outputDir="."):
		''' Pisi index '''
		pisi.api.index(inputs,
                       output=os.path.join(outputDir, "pisi-index.xml"),
                       skip_sources=True,
                       skip_signing=True,
                       compression=self.index_compression)
                       
	def not_implemented (self):
		print "Not yet implemented"
		
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
				 'delta': ('create deltas for the repository', repo.not_implemented) }

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
	
