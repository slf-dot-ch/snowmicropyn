.. _api_usersguide:

API User's Guide
================

Data Files
----------

When performing a measurement with SnowMicroPen, the device writes the data
onto its SD card in a binary file with a :file:`pnt` extension. (Example:
:file:`S13M0067.pnt`). For each measurment process, a new pnt file is written.
Each pnt file consists of a header with meta information followed by the actual
data, the force samples.

.. note:: The *snowmicropyn* package never ever writes into a pnt file. Good to
   know your precious raw data is always safe.

Corresponding ini files
^^^^^^^^^^^^^^^^^^^^^^^

However, when using functionality of this package, an additional storage to save
other data is required. This storage is an :file:`ini` file, named like the pnt
file (example from previous section: :file:`S13M0067.ini`).

First steps
-----------

The core class of the API is the :class:`snowmicropyn.Profile` class. It
represents a profile loaded from a pnt file. By using its static load method,
you can load a profile:

.. code-block:: python

   import snowmicropyn
   p = snowmicropyn.Profile.load('./S13M0067.pnt')

In the load call, there's also a check for a corresponding ini file, in this
case for :file:`S13M0067.ini`.

Logging *snowmicropyn*'s Version and Git Hash
---------------------------------------------

As a scientist, you may be interested to keep a log so you can reproduce what
you calculated with what version of *snowmicropyn*. The package contains a
version string and a git hash identifier.

To access the package's version string, you do:

.. code-block:: python

   import snowmicropyn
   v = snowmicropyn.__version__

To access the git hash string of this release, you do:

.. code-block:: python

   import snowmicropyn
   gh = snowmicropyn.githash()

When exporting data using this module, the created CSV files will also contain a
comment as first line with the version string and git hash to identify which
version of *snowmicropyn* was used to create the file.

.. warning::

   However, this is no mechanism to protect a file from later alternation. It's
   just some basic information which maybe will be useful to you.

Examples
--------

Some examples will help you get an overview of *snowmicropyn*'s features.

.. hint::

   To get the code mentioned in this guide, Download_ the source code of
   *snowmicropyn*. You'll find the examples in the subfolder ``examples``
   and even some pnt files to play around with in the folder
   ``examples/profiles``.

Explore properties
^^^^^^^^^^^^^^^^^^

In our first example, we load a profile and explore its properties. We set some
markers and finally call the :meth:`snowmicropyn.Profile.save` so the markers
get saved in an ini file so we don't lose them.

.. literalinclude::  ../examples/explore.py

Batch exporting
^^^^^^^^^^^^^^^

You're just home from backcountry where you recorded a series of profiles with
your SnowMicroPen and now want to read this data with your tool of choice which
supports reading CSV files? Then this example is for you!

.. literalinclude::  ../examples/batch_export.py

After you executed this example, there will be a :file:`..._samples.csv` and a
:file:`..._meta.csv` for each pnt file in the directory.

Plotting
^^^^^^^^

In this example, we use the delightful matplotlib_ to explore the penetration
signal of a profile.

.. literalinclude::  ../examples/plot.py


When this code is executed, a window like the following should open:

.. figure:: images/screenshot_matplotlib.png
   :alt: Screenshot of matplotlib Window

Explore using the tool buttons below the plot! You can even modify the axes and
export the plot into an image file.

A Touch of Science
^^^^^^^^^^^^^^^^^^

Alright, let's do some science. In this example, we examine a profile recorded
at our test site Weissfluhjoch. There's a crust and a depth hoar layer in this
profile. By using :command:`pyngui`, we already identified the layers for you by
setting markers. Let's calculate the mean specific surface area (SSA) within the
crust and the weight that lies on the depth hoar layer.

.. literalinclude::  ../examples/weaklayer.py

This will print something like:

.. code-block:: console

   Mean SSA within crust: 5.5 m^2/m^3
   Weight above hoar layer: 98 kg/m^2

Using Different Parameterizations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Depending on your SMP device and/or your climatic settings different
parameterizations to derive observables from the raw SMP measurements may be
preferable. Have a look at the Parameterizations_ help topic for details on
what's available.

In the GUI you are able to select them individually, and programmatically
this is done by giving their short names.

The names are found in the :code:`shortname` property in the respective
implementations (in the :file:`parameterizations` subdirectory) and can
be e. g. "P2015", "CR2020", "K2020a" or "K2020b".

.. literalinclude:: ../examples/parameterizations.py

Working with the machine learning module
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Have a look at how snowmicropyn uses machine learning for its
`grain shape estimation`_. To reiterate, this is done in order to be able
to provide valid snowpit CAAML output. For example, niViz_ needs the grain
shape to display something.

In order to accomplish this, snowmicropyn offers a machine learning interface
which will try to learn the connection between the measured SMP microparameters
and known grain shapes.

As usual you can control this interface through the API and via the GUI. Have a
look at the shipped `ai example program`_ to see how to control the API. The
GUI on the other hand is opened when exporting to CAAML.

Snowmicropyn ships a training data file which has been pre-computed for your
convenience, so ideally when enabling grain shape export it should produce
valid output. However, it will be trained with a limited amount of profiles
from a certain climate setting so if available you should produce your own
training data.

To do so you need to specify a folder containing SMP data and grain shape
information, as well as the method used for parsing. For example, method
'exact' expects a folder that contains both pnt files and caaml files (same base
name) where the grain shape is taken from the caaml file at measurement depth.
Method 'RHOSSA' on the other hand expects pnt files only but they must have
markers set for the grain types.

The folder :file:`tools` contains a script to download and prepare both of
these types of datasets, in this case from the RHOSSA campaign (follow the
links therein for more information about this dataset).

Obviously if you are inherently interested in the grain shape then these
methods have their limits - again, the provided example performs some test
scores to give an idea about the accuracy.

.. _matplotlib: https://www.matplotlib.org/
.. _Download: https://github.com/slf-dot-ch/snowmicropyn/
.. _Parameterizations: https://snowmicropyn.readthedocs.io/en/latest/api_reference.html#module-snowmicropyn.parameterizations.proksch2015
.. _grain shape estimation: https://snowmicropyn.readthedocs.io/en/latest/snowpit.html#snow-grain-shapes-machine-learning
.. _niViz: https://niviz.org/
.. _ai example program: https://github.com/slf-dot-ch/snowmicropyn/blob/master/examples/machine_learning.py
