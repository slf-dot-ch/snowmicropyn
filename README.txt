SnowMicroPyn Version 0.0.21 alpha
=================================

About:
------
SnowMicroPyn is a Python based reader for SnowMicroPen binary files. The Software
is open source and licensed under GNU GPL terms of conditions.
Feel free to use, modify and/or extend the code.

The program is still an alpha revision. Please report bugs, see section "Contact".
Development takes place mainly on and for Linux systems, thus bugs might occur in
in MacOSX and Win versions.

Newest software releases can be found here:
http://sourceforge.net/projects/pyntreader

Features:
---------
-Read and plot .pnt Files
-Export measurement, infos and plots into human readable
-View and save measurement GPS locations using Google Static API
-Noise, drift and offset analysis
-batch mode
-super pose and subtract plots
-frequency analysis

Requirements:
-------------
A) Using a Python Interpreter:
	-tested on python 2.7.x
	-use wxPython 3.0.0
	-use matplotlib <= 1.2.2 (version = 1.3.0 has a bug in zoom function)
	-use scipy >= 13.0
	-see ./src/extensions/requirements.txt

B) Stand alone binaries:
	-binary (.bin/.app/.exe) should be in the same folder as artwork directory
	-no other dependencies are known

Installation:
-------------
A) Using a Python Interpreter:
	-install Python 2.7.x (python.org)
	-t is recommended to use virtualenv, see http://blog.dbrgn.ch/2012/9/18/virtualenv-quickstart/
	-install dependencies using pip
		pip install -r requirements.txt
		wxpython >= 2.8 can be installed from wxpython.org
	-run "python PyNTReader.py" from terminal
	-or in Ubuntu make file executable: "chmod +x PyNTReader.py" and run ./PyNTReader from terminal, respectively double click the file 

B) Stand alone binaries:

	I) Linux
		compiled and tested on Ubuntu 13.10 64bit
		-make file executable: chmod +x PyNTReader
		-double click executable or type /path/to/file/PyNTReader
		-optionally pass file names as command line argument to open them directly, or try "open with"
	II) MacOS
		compiled and tested on MacOSX 10.8.5 64bit
		-double click .app or executer PyNTReader in terminal
	III) Windows
		compiled and tested on Win7 64bit and WinXP 32bit
		-double click .exe, or press on "open with" on a .pnt file 
Contact:
--------
For questions and bug reports please contact sascha.grimm@slf.ch

Developer:
-----------
Sascha Grimm
WSL Institute for Snow and Avalanche Research SLF
Team Snow Physics
Flüelastrasse 11
CH-7260 Davos
