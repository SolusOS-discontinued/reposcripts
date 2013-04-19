#!/usr/bin/env python
import pisi.operations.delta
import os

import pisi.api
from pisi.operations.delta import create_delta_packages


def workDirForPackage (meta):
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
	
	return path
	
for root,dirs,files in os.walk ("."):
	
	currentPkgs = dict ()
	for file in files:
		if not file.endswith (".delta.pisi") and file.endswith (".pisi"):
			path = os.path.join (root, file)
			print "Examining %s" % path
			pkg,fileList = pisi.api.info (path)
			
			# Use a mapping
			name = pkg.package.name
			pkg.FILEPATH = file
			if not name in currentPkgs:
				currentPkgs [name] = list()
			currentPkgs [name].append (pkg)
				
	# Now loop back through current packages
	for package_name in currentPkgs:
		packages = currentPkgs [package_name]
		print "%d packages found for %s" % (len(packages), package_name)
		
		package_list = list()
		for pkg in packages:
			package_list.append( pkg.FILEPATH )
		
		workDir = workDirForPackage (packages[0])
		oldDir = os.getcwd ()
		os.chdir (workDir)
		
		# Generate all possible dependencies
		if len(package_list) > 1:
			print "Creating deltas for %s" % package_name
			
			package_list.sort ()
			mapping = dict ()
			for pkg in package_list:
				print pkg
				splits = pkg.split ("-")
				arch = splits[-1].split (".")[0]
				distro = splits[-2]
				release = splits [-3]
				mapping [release] = pkg
			# Go back through em
			keys = mapping.keys()
			keys.sort()
			for key in keys:
				# Again, i know, weird.
				olderPackages = list ()
				TopDog = None
				for key2 in keys:
					if key2 >= key:
						TopDog = mapping[key2]
						break
					olderPackages.append (mapping[key2])
				create_delta_packages (olderPackages, TopDog)
			#create_delta_packages (package_list, highItem.FILEPATH)
		os.chdir (oldDir)
