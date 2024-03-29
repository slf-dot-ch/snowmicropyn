API Reference
=============

Receive Version Number and Git Hash
-----------------------------------

To receive the version of *snowmicropyn* and the git hash of
*snowmicropyn* you're using, do the following:

.. code-block:: python

   import snowmicropyn
   version = snowmicropyn.__version__  #  e.g. '0.1.2'
   hash = snowmicropyn.githash()  # e.g. '55623b2d71e7cb7...'

Receiving and logging this is useful for tracking purposes. The version and the
git hash are loggend also when you import the package (using Python's standard
logging facility). In case this information is crucial to you, it's important
to set up the logging before importing the package, otherwise you will miss it.
The other option is to do the logging yourself using the function
:func:`snowmicropyn.githash` and accessing :const:`snowmicropyn.__version__`.

.. autofunction:: snowmicropyn.githash

Its Core: The :class:`Profile` Class
------------------------------------

.. autoclass:: snowmicropyn.Profile
   :members:

Auto-detection of Ground & Surface
----------------------------------

*snowmicropyn* contains algorithms to detect beginning and end of the snowpack
automatically. This algorithms may fail, so you may check the values before
you process your data any further.

.. automodule:: snowmicropyn.detection
   :members:

Shot Noise Model (Löwe, 2012)
-----------------------------

.. automodule:: snowmicropyn.loewe2012
   :members:

SSA & Density (Proksch, 2015)
-----------------------------

.. automodule:: snowmicropyn.parameterizations.proksch2015
   :members:

SSA & Density (Calonne and Richter, 2020)
-----------------------------------------

.. automodule:: snowmicropyn.parameterizations.calonne_richter2020
   :members:

Density (King, 2020)
-----------------------------------------

.. automodule:: snowmicropyn.parameterizations.king2020
   :members:

Under the hood
--------------

:class:`snowmicropyn.Profile` uses the method :meth:`load` of class
:class:`snowmicropyn.Pnt` to get the raw data of pnt file. You probably won't
ever use this class yourself.

.. autoclass:: snowmicropyn.Pnt
   :members:
