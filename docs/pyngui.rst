.. _pyngui:

:program:`pyngui`
=================

What is :program:`pyngui`?
--------------------------

:program:`pyngui` is a desktop application to read, visualise and export files
recorded by SnowMicroPen (pnt files).

Launch :program:`pyngui`
--------------------------

When the *snowicropyn* package is installed, a simple script to start
:program:`pyngui` is registered too. Open a Terminal Window and type
:kbd:`pyngui` and hit :kbd:`return`. A window should open which looks alike
this screenshot:

.. figure:: images/screenshot_pyngui.png
   :alt: Screenshot of pyngui

Probably, this command fails to launch :program:`pyngui`. Try to launch
it manually then. Type:

.. code-block:: console

   python -m snowmicropyn.pyngui.app

or:

.. code-block:: console

   python -m snowmicropyn.pyngui.app

Features & Tips
---------------

Save your changes!
^^^^^^^^^^^^^^^^^^

:program:`pyngui` does not prompt or warn for unsaved changes. Don't forget
to save your markers, otherwise they will be lost.

Surface & ground
^^^^^^^^^^^^^^^^

:program:`pyngui` uses the marker labels ``surface``and ``ground`` to mark the
begin and end of the snowpack. You can let :program:`pyngui` auto detect
those markers for you by clicking the according icons in the toolbar.

Drift, Offset & Noise
^^^^^^^^^^^^^^^^^^^^^

For each profile, the :program:`pyngui` calculates drift, offset and noise and
displays those values in the sidebar. This data is useful to check for a bad
signal. The values are calculated for a section within the signal. Where this
section starts and end is indicated in the sidebar. In case you want to specify
the section yourself, set markers called ``drift_begin`` and ``drift_end``. To
simplest way to do so is context clicking into the plot.
