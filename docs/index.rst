
*snowmicropyn*'s Documentation
==============================

A warmly welcome to the documentation of *snowmicropyn*, a python package to
read, export and post process data (\*.pnt files) recorded by SnowMicroPen_, a
snow penetration probe for scientifc applications developed at SLF_.

The software and its documentation is released under GPL_.

For feedback and suggestions, please write to
`snowmicropen@slf.ch <mailto:snowmicropen@slf.ch>`_ or use our `Issue Tracker`_.

Overview
--------

What's Where
^^^^^^^^^^^^

- Releases_ on PyPI.
- Source Code Repository_ on GitHub.
- Documentation_ on Read the Docs.

What's inside?
^^^^^^^^^^^^^^

The *snowmicropyn* package consits of two entities:

- :program:`Examiner`, a desktop application to read, export and post process
  pnt files
- An :abbr:`API (Application Programming Interface)` to automate reading, exporting and post processing pnt files using
  the python language. You'll need some basic programming skills to use it.

You guessed it, :program:`Examiner` uses the API itself too.

Installation
^^^^^^^^^^^^

Installing *snowmicropyn* is a trivial task in case you're experienced with
Python:

.. code-block:: console

   pip install snowmicropyn

Peep peep? No clue what we're talking about? Hop to section :doc:`install`!

First steps with the API
^^^^^^^^^^^^^^^^^^^^^^^^

The following snippet is a simple example how to read a pnt file, read some of
it's meta information and export the samples (measured distance & force) into
CSV format.

.. code-block:: python

   from snowmicropyn import Profile

   p = Profile.load('S31M0067.pnt')

   print(p.timestamp)  # Timestamp of recording
   print(p.smp_serial)  # Serial number of SnowMicroPen used
   print(p.coordinates)  # WGS84 latitude and longitude

   # Export samples into CSV format
   # (By default, filename will be S31M0067_samples.csv)
   p.export_samples()

You find more information about the API in the :doc:`api_usersguide`.

Launch the :program:`Examiner`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After installing *snowmicropyn*, open a Terminal Window and type
:kbd:`smpexaminer` and hit :kbd:`return` to start the
:program:`Examiner`. Happy examining.

Table of Content
----------------

Here's a list of all sections available in this documentation.

.. toctree::
   :maxdepth: 2

   install.rst
   api_usersguide.rst
   api_reference.rst
   examiner.rst
   develop.rst

Information for *snowmicropyn* developers
-----------------------------------------

You're hacking on *snowmicropyn*? Please read :doc:`develop`.


Acknowledgements
----------------

Thanks to PyPI_, GitHub_, `Read the Docs`_ for hosting our project!



.. _SLF: https://www.slf.ch/
.. _SnowMicroPen: https://www.slf.ch/en/services-and-products/research-instruments/snowmicropen-r-smp4-version.html
.. _GPL: https://www.gnu.org/licenses/gpl.txt

.. _GitHub: https://github.com/
.. _Repository: https://github.com/slf-dot-ch/snowmicropyn/
.. _Issue Tracker: https://github.com/slf-dot-ch/snowmicropyn/issues/

.. _Read the Docs: https://readthedocs.org/
.. _Documentation: https://snowmicropyn.readthedocs.io/

.. _PyPI: https://pypi.org/
.. _Releases: https://pypi.org/project/snowmicropyn/
