A simpe code coverage tool using Pin. It can creates a minimum set of files
with the best code coverage. This is very useful for fuzzing. 
Currently the pintool is only compiled for linux x86. But it can be easily 
compiled for other platforms. 
Pin should be in the same directory like coverage.py. If it is lying in 
another path, the path in the script has to be changed. 

Dependencies
------------

- Pin
- psutil


Usage
-----
	usage: coverage.py [-h] [-f <files>]
					   [-a <application string> [<application string> ...]] -b
					   <output path> [-s <output path>] [-l] [-t] [--only <libs>]

	optional arguments:
	  -h, --help            show this help message and exit
	  -f <files>, --files <files>
							path to files
	  -a <application string> [<application string> ...], --application <application string> [<application string> ...]
							application string
	  -b <output path>, --bbls <output path>
							the path where the code coverage files should be saved
	  -s <output path>, --set <output path>
							the path where the minimum set of files should be
							saved
	  -l, --list-libraries  prints all the touched libraries used by the
							application
	  -t, --terminate       terminates the process if this idling
	  --only <libs>         a comma separated list which libraries should only use
							for code coverage analysis

	example:
	Create only coverage files. So it is possible to generate the coverage files on different machines.
	coverage.py --files files --bbls bbls --application /usr/bin/evince %FILE% --terminate

	Create coverage files and the minimum set of files
	coverage.py --files files --bbls bbls --application /usr/bin/evince %FILE% --set set --terminate

	Only create the minimum set, when you have existing coverage files.
	coverage.py --files files --bbls bbls --set set 

	List all used libraries
	coverage.py --bbls bbls --list-libraries

	Create a set with the best coverage over just a few libs
	coverage.py --files files --bbls bbls --set set --only libc.so.6,evince,libjpeg.so.62

