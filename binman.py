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
				
	def index (self, inputs, outputDir):
		''' Pisi index '''
		pisi.api.index(inputs,
                       output=os.path.join(outputDir, "pisi-index.xml"),
                       skip_sources=True,
                       skip_signing=True,
                       compression=self.index_compression)
                       		
if __name__ == "__main__":
	if not os.path.exists ("repo.conf"):
		print "Please use from a valid repository"
		sys.exit (1)
		
	repo = BinMan ("repo.conf")
	# Check the command
	if len(sys.argv) < 2:
		print "Please specify a command"
		sys.exit (1)
	
	keyword = sys.argv[1]
	if keyword == "process":
		repo.process_incoming ()
	elif keyword == "index":
		repo.index (["."], ".")
	else:
		print "Unknown command"
	
