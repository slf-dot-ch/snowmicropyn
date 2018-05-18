Overview
========

What's inside?
--------------

The *snowmicropyn* package contains two entities:

- An :doc:`API <api_usersguide>` to automate reading, exporting and post
  processing pnt files using the python language. You'll need some basic
  programming skills to use it.
- :doc:`pyngui`, a desktop application to read, export and post
  process pnt files. :program:`pyngui` uses the API itself too.

How do I get it?
----------------

Installing *snowmicropyn* is a trivial task in case you're experienced with
Python:

.. code-block:: console

   pip install snowmicropyn

No clue what we're talking about? You find a more detailed description in
section :doc:`install`!

*snowmicropyn*'s API
--------------------

The following snippet is a simple example how to read a pnt file, read some of
it's meta information and export its samples (measured distance & force) into a
CSV file.

.. code-block:: python

   from snowmicropyn import Profile

   p = Profile.load('S31M0067.pnt')

   print(p.timestamp)  # Timestamp of recording
   print(p.smp_serial)  # Serial number of SnowMicroPen used
   print(p.coordinates)  # WGS 84 (latitude, longitude)

   # Export samples into CSV format
   # (By default, filename will be :file:`S31M0067_samples.csv)
   p.export_samples()

You find detailed information about the API in the :doc:`api_usersguide`. For
more information about the API's elements, checkout the :doc:`api_reference`.

Launch :program:`pyngui`
------------------------

After installing *snowmicropyn* , open a Terminal Window and type
:kbd:`pyngui` and hit :kbd:`return` to start the
:program:`pyngui`. Happy examining!

If you want to launch the :program:`pyngui` manually, type:

.. code-block:: console

   python -m snowmicropyn.pyngui.app
