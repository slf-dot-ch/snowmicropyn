API Reference
=============

.. module::snowmicropyn

Its core: The :class:`Profile`
------------------------------

.. autoclass:: snowmicropyn.Profile
   :members:

Proksch 2015
------------

.. automodule:: snowmicropyn.proksch2015
   :members:

Under the hood
--------------

:class:`snowmicropyn.Profile` uses the method :meth:`load` of class
:class:`snowmicropyn.Pnt` to get the raw data of pnt file. You probably won't
ever use this class yourself.

.. autoclass:: snowmicropyn.Pnt
   :members:
