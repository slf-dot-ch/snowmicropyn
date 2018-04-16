Information for Developers
==========================

Compiling the icons into a python file
--------------------------------------

.. code-block:: console

    pyrcc5 -o /snowmicropyn/examiner/icons.py resources/icons.qrc

Releasing a new Version of snowmicropyn
---------------------------------------

#. Update version string (``__version__``) in file snowmicropyn/__ini__.py
#. Commit and tag repository with **exactly** same string.

.. code-block:: console

    git commit -m "Some nice words about this commit"
    git tag 0.1.0a1 -m "Adds tag 0.1.0a1 for PyPI"

#. Push to github.

.. code-block:: console
    git push --tags

