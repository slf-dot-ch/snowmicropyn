SnowMicroPyn Version 0.0.26 alpha
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


Installation:
-------------
A) If not yet installed, install Anaconda or Miniconda
   https://conda.io/docs/user-guide/install/download.html

B) Windows: Start Anaconda Prompt
   macOS: Start Terminal Application

C) Create new conda environment
   conda create -n smpenv

D) Run SnowMicroPyn:
   python -m snowmicropyn.SnowMicroPyn  (on Windows)
   pythonw -m snowmicropyn.SnowMicroPyn  (on macOS)

Contact:
--------
For questions and bug reports please contact snowmicropyn@slf.ch

Developer:
-----------
Sascha Grimm
WSL Institute for Snow and Avalanche Research SLF
Team Snow Physics
Flüelastrasse 11
CH-7260 Davos
