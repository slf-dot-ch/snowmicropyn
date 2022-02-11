.. _troubleshooting:

Troubleshooting
===============

Problems with starting the GUI / Qt
-----------------------------------

You should install through pip (both from remote and locally) so that you can
uninstall cleanly (i. e. not through setup.py directly).
Qt should be installed automatically, but it may happen that there are multiple
versions (or references to them) on the system, especially when working with
virtual environment managers (such as conda or venv).
Try to uninstall every version of snowmicropyn automatically and manually (by
deleting all .egg and .egg-link files, as well as any cloned code):

.. code-block:: console

    pip3 uninstall snowmicropyn
    sudo pip3 uninstall snowmicropyn
    locate snowmicropyn
    which pyngui

And inside Python:

.. code-block:: python

   from PyQt5.QtCore import QT_VERSION_STR
   from PyQt5.QtCore import PYQT_VERSION_STR
   print(QT_VERSION_STR, PYQT_VERSION_STR)
    
Try to do the same with PyQt5 and remove all installation locations of the Qt
libraries which you do not need globally, as well as from your virtual envs.

Then, try a fresh install of *snowmicropyn* via :code:`pip`.

If this does not help you can set your :code:`LD_LIBRARY_PATH` to the correct
location (parent folder of the missing libraries). Don't forget to
:code:`ldconfig`. Or you can install Qt for Python through pip or (worse) apt
to the correct location.

Problems with xcb
-----------------

*"Failed to load platform plugin "xcb"."* means that the graphics plugin can
not be initialized. Maybe you need :code:`libxcb-xinerama0` or the dev package
of it? Try enabling plugin debugging with :code:`export QT_DEBUG_PLUGINS=1` to
see what's up and check that the location of the libraries is correct.
(Through a terminal maybe you or your multiplexer forgot to ssh -X?)
