.. _api_usersguide:

API User's Guide
================

Data Files (file:`*.pnt`)
-------------------------

When performing a measurement with SnowMicroPen, the device writes the data
onto its SD card in a binary and proprietary file with a :file:`pnt` extension.
(Example: :file:`S13M0067.pnt`). For each measurment process, a new pnt file is
written. Each pnt file consists of a header with meta information followed by
the actual data, the force samples.

.. tip:: The *snowmicropyn* package never ever writes into a pnt file. Good to
         know your precious raw data is always save.

The corresponding ini file
^^^^^^^^^^^^^^^^^^^^^^^^^^

However, when using functionality of this package, an additional storage to save
other data is required. This storage is an :file:`ini` file, named like the pnt
file (Example from section before: :file:`S13M0067.ini`).


First steps
-----------

The core class of the API is the :class:`snowmicropyn.Profile` class. It
represents a profile loaded from a pnt file. By using its static load method,
you can load a profile:

.. code-block:: python

   import snowmicropyn
   p = snowmicropyn.Profile.load('./S13M0067.pnt')

In the load call, there's also a check for a corresponding ini file, in this
case for the :file:`S13M0067.ini`.

Examples
--------

Have a look at our collection of :github_tree:`examples` in our GitHub
repository.
