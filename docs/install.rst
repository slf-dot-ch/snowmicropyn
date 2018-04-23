.. _install:

Installation
============

Prerequisite: Python 3
----------------------

snowmicropyn is written in the Python_ programming language. You need to have
Python 3.4 (or later) installed on your machine to install *snowmicropyn*.

To check if your computer has Python installed, open a Terminal Window and type

.. code-block:: console

   python --version

.. note:: When both, Python 2 and Python 3 is installed on your computer,
   usually you run Python 2 by the command :command:`python` and Python 3 by the
   command :command:`python3`.

If you have Python installed, you'll get a version string returned. In case you
get a response like "``command not found``" or a version smaller than 3.4.x, you
have to install or update Python.

How to install Python? Download an
`official package <https://www.python.org/downloads/>`_ or follow the
`instructions <http://docs.python-guide.org/en/latest/starting/installation/>`_
from the Python Guide.

Make sure you install the latest Python 3 release.

Installing *snowmicropyn*
-------------------------

So you managed to install Python 3 on your computer. Well done! Now, by using
the :command:`pip` command (which is part of Python), the installation of
*snowmicropyn* is a peace of cake. Open a terminal window and type:

.. code-block:: console

   pip install snowmicropyn

.. note:: When both, Python 2 and Python 3 is installed on your computer, you
   may need to type :command:`pip3` instead of command :command:`pip`.

This will install the latest version of *snowmicropyn* available on PyPI_ and
its dependencies. In case you want to install a specific version of
snowmicropyn, append it to the package name as in this example:

.. code-block:: console

   pip install snowmicropyn==0.1.3

That's about it. We hope you managed to get *snowmicropyn* on your machine.

.. hint:: You may consider using a `virtual environment`_ to separate your
          *snowmicropyn* installation from other projects. But that's already
          an more advanced topic.

.. tip:: A good place to start getting into Python is the `Python Guide`_.


Uninstalling
------------

Get rid of *snowmicropyn* is simple too:

.. code-block:: console

   pip uninstall snowmicropyn


.. _Python: https://www.python.org/
.. _PyPI: https://pypi.org/
.. _virtual environment: https://docs.python.org/3/tutorial/venv.html
.. _Python Guide: http://docs.python-guide.org
