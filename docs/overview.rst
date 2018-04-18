Overview
========

What's inside?
--------------

The *snowmicropyn* package consits of two entities:

- :program:`Examiner`, a desktop application to read, export and post process
  pnt files
- An :abbr:`API (Application Programming Interface)` to automate reading,
  exporting and post processing pnt files using the python language. You'll need
  some basic programming skills to use it.

You guessed it, :program:`Examiner` uses the API itself too.

Installation
------------

Installing *snowmicropyn* is a trivial task in case you're experienced with
Python:

.. code-block:: console

   pip install snowmicropyn

Peep peep? No clue what we're talking about? Hop to section :doc:`install`!

First steps with the API
------------------------

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
------------------------------

After installing *snowmicropyn* , open a Terminal Window and type
:kbd:`examiner` and hit :kbd:`return` to start the
:program:`Examiner`. Happy examining.
