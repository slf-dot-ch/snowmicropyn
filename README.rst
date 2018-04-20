snowmicropyn
============

A python package to read, export and post process data (``*.pnt`` files)
recorded by SnowMicroPen_, a snow penetration probe for scientifc applications
developed at SLF_.

The software is open source and released under `GPL`_. Contributions are
welcome.

Installing
----------

Install and update using ``pip``:

.. code-block:: console

    pip install -U snowmicropyn

A Simple Example
----------------

.. code-block:: python

    from snowmicropyn import Profile

    p = Profile.load('./some_directory/S31M0067.pnt')

    ts = p.timestamp
    coords = p.coordinates
    samples = p.samples  # It's a pandas dataframe

Documentation
-------------

The project's documentation_ can be studied on *Read the Docs*.

Contact
-------

To get in touch, please write to snowmicropen@slf.ch.


.. _SLF: https://www.slf.ch
.. _SnowMicroPen: https://www.slf.ch/en/services-and-products/research-instruments/snowmicropen-r-smp4-version.html
.. _GPL: https://www.gnu.org/licenses/gpl-3.0.en.html
.. _documentation: https://snowmicropyn.readthedocs.io/
