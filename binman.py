#!/usr/bin/env python

import os
import pisi.api
import shutil
import sys

class BinMan:
	
	def __init__(self, scanDir):
		searchList = list()
		print "Scanning current working directory for .pisi files"
		
		if not os.path.exists (scanDir):
			print "Directory not found: %s" % scanDir
			sys.exit (1)
			
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
				
				
if __name__ == "__main__":
	BinMan ("./incoming")
