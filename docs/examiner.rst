.. _examiner:

The :program:`Examiner`
=======================

What is :program:`Examiner`?
----------------------------

:program:`Examiner` is a desktop application to read, visualise and export files
recorded by SnowMicroPen (pnt files).

Launch :program:`Examiner`
--------------------------

When the *snowicropyn* package is installed, a simple script to start
:program:`Examiner` is registered too. Open a Terminal Window and type
:kbd:`examiner` and hit :kbd:`return`. A window should open which looks alike
this screenshot:

.. figure:: images/screenshot_examiner.png
   :alt: Screenshot of Examiner

If you want to launch the :program:`Examiner` manually, type:

.. code-block:: console

   python -m snowmicropyn.examiner.app

Features & Tips
---------------

Save your changes!
^^^^^^^^^^^^^^^^^^

:program:`Examiner` does not prompt or warn for unsaved changes. Don't forget
to save your markers, otherwise they will be lost.

Surface & ground
^^^^^^^^^^^^^^^^

:program:`Examiner` uses the marker labels ``surface``and ``ground`` to mark the
begin and end of the snowpack. You can let :program:`Examiner` auto detect
those markers for you by clicking the according icons in the toolbar.

Drift, Offset & Noise
^^^^^^^^^^^^^^^^^^^^^

For each profile, the :program:`Examiner` calculates drift, offset and noise and
displays those values in the sidebar. This data is useful to check for a bad
signal. The values are calculated for a section within the signal. Where this
section starts and end is indicated in the sidebar. In case you want to specify
the section yourself, set markers called ``drift_begin`` and ``drift_end``. To
simplest way to do so is context clicking into the plot.
