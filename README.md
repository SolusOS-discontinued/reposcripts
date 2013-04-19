SolusOS Repository Scripts
==========================

The scripts in this git repo are used to maintain the SolusOS package repositories.
Traditionally a direct build-to-repo approach was used, however this has several
disadvantages. A staggered-release model isn't permitted and there are large overheads
involved, primarily disk space.

A buildfarm should merely build the new packages without requiring an entire repository
installation to do its job. Once packages are built, they should be transferred (rsync)
to a package repository server, into its "incoming" queue.

Once packages have hit the incoming queue, they are held for processing. You must use
the repo-scripts here to control distribution and maintenance of the repository

BinMan
------
BinMan is the main controlling script of the repository. It process the incoming queue,
and moves packages into the appropriate directories.


DeltaFise
---------
Delta packages will not be accepted into incoming. All delta packages are produced on
the repository itself, allowing delta upgrades between different SolusOS releases. Using
the traditional build-to-repo system, this would not have been possible.

Authors
-------
The SolusOS RepoScripts are the work of Ikey Doherty <ikey@solusos.com>
