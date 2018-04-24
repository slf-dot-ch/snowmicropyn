API Reference
=============

Receive Version Number and Git Hash
-----------------------------------

To receive the version of *snowmicropyn* and the githash of *snowmicropyn* your
using, do the following:

.. code-block:: python

   import snowmicropyn
   version = snowmicropyn.__version__  #  e.g. '0.1.2'
   hash = snowmicropyn.githash()  # e.g. '55623b2d71e7cb7...'

Receiving and logging this is useful for tracking purposes. The version and the
git hash are 

.. autofunction:: snowmicropyn.githash

Its Core: The :class:`Profile` Class
------------------------------------

.. autoclass:: snowmicropyn.Profile
   :members:

Shotnoise Model (Löwe, 2011)
----------------------------

.. automodule:: snowmicropyn.loewe2011
   :members:

SSA & Density (Proksch, 2015)
-----------------------------

.. automodule:: snowmicropyn.proksch2015
   :members:

Under the hood
--------------

:class:`snowmicropyn.Profile` uses the method :meth:`load` of class
:class:`snowmicropyn.Pnt` to get the raw data of pnt file. You probably won't
ever use this class yourself.

.. autoclass:: snowmicropyn.Pnt
   :members:
