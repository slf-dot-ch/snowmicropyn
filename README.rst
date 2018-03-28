SnowMicroPyn
============

SnowMicroPyn, a python package for analyzing snow profiles recorded
with the snow penetrometer `SnowMicroPen`_ by `SLF`_. It contains a
Desktop Application (using `wxpython`_) for straigt forward plot
creation and data export. But it can also be used within your own
python scripts to enable batch processing or other tasks.

SnowMicroPyn is open source and released under `GPLv3`_. Any
contribution is welcome. For bug reports, please use github issue
tracking or write to snowmicropen@slf.ch.

Features
--------

- Read and plot .pnt Files
- Export measurement, information and plots into human readable format
- View and save measurement GPS locations using Google Static API
- Noise, drift and offset analysis
- Superpose and subtract plots
- Frequency analysis

Prerequisites
-------------

A recent Python Installation. An Anaconda Installation if fine too, of
course.

Installation
------------

Install and update using `pip`_:

.. code-block:: text

    pip install -U snowmicropyn

Run SnowMicroPyn Desktop Application
------------------------------------

On Windows, type:

.. code-block:: text

    python -m snowmicropyn.SnowMicroPyn

On macOS, type:

.. code-block:: text

    pythonw -m snowmicropyn.SnowMicroPyn

Contact
-------

If you like to get in touch with the team, please write to
snowmicropen@slf.ch.

Contributors
------------

- Sascha Grimm, SLF
- Henning Löwe, SLF
- Thiemo Theile, SLF
- Marcel Schoch, SLF

A Simple Scripting Example
--------------------------

.. code-block:: python

    from snowmicropyn.io import Profile

    p = Profile.load('S31M0067.pnt')

    # Read some information about the profile
    timestamp = p.timestamp
    smp_serial = p.smp_serial
    latitude, longitude = p.coordinates  # WGS84 latitude and longitude

    # Export samples into CSV format
    # (By default, filename will be S31M0067_samples.csv)
    p.export_samples()

    # Export meta info into CSV format
    # (By default, filename will be S31M0067_meta.csv)
    p.export_meta()


.. _SLF: https://www.slf.ch
.. _SnowMicroPen: https://www.slf.ch/en/services-and-products/research-instruments/snowmicropen-r-smp4-version.html
.. _GPLv3: https://www.gnu.org/licenses/gpl-3.0.en.html
.. _pip: https://pip.pypa.io/en/stable/quickstart/
.. _wxpython: https://wxpython.org/