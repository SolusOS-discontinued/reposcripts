#!/usr/bin/env python

import os
import pisi.api
import shutil
import sys
from pisi.file import File


class BinMan:
	
	def process_incoming (self, scanDir):
		''' Process all packages in the scanDir and organise them properly '''
		if not os.path.exists (scanDir):
			print "Directory not found: %s" % scanDir
			sys.exit (1)

		searchList = list()
		print "Scanning current working directory for .pisi files"
					
		for potential in os.listdir (scanDir):
			if potential.endswith (".pisi") and not potential.endswith (".delta.pisi"):
				searchList.append (potential)
				
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
                       compression=File.COMPRESSION_TYPE_XZ)
                       		
if __name__ == "__main__":
	repo = BinMan ()
	# Check the command
	if len(sys.argv) < 2:
		print "Please specify a command"
		sys.exit (1)
	
	keyword = sys.argv[1]
	if keyword == "process":
		repo.process_incoming ("./incoming")
	elif keyword == "index":
		repo.index (["./incoming"], ".")
	else:
		print "Unknown command"
	
