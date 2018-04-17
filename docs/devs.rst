.. _devs:

Information for Developers
==========================

Compiling Icons Into a Python File
----------------------------------

The *Profile Examiner* application requires icons used in menus and
toolbar buttons. They are stored in the folder ``resources``. For easy
deployment, they are compiled into a python source file using the CLI
tool ``pyrcc5``, which comes with the Qt package. Execute the following
command when you did do changes in the resources folder:

.. code-block:: console

    pyrcc5 -o snowmicropyn/examiner/icons.py resources/icons.qrc

This command generates an updated version of the file called
``icons.py``. Don't ever edit this file manually.

Releasing a New Version of snowmicropyn
---------------------------------------


#.  Update version string (``__version__``) in file
    snowmicropyn/__init__.py

#.  Make sure you updated the version string!

#.  Commit you changes

    .. code-block:: console

        git commit -m "Some nice words about your changes"

#.  Add an annotated tag in your repo

    .. code-block:: console

        git tag -a <version-number> -m "Version <version-number>"

    Some examples for <version-number>, also consider reading PEP440_.

    - ``v0.2.dev21`` (Development Release)
    - ``v0.2a4`` (Alpha Release)
    - ``v0.2b7`` (Beta Release)
    - ``v0.2.0`` (Final Release)
    - ``v0.2.11`` (Bugfix Release)

#.  Push the Tag to github

    .. code-block:: console

        git push origin <version-number>

#.  Use the script ``publish_to_pypi.sh`` to publish this
    release on PyPI. You'll be asked for your username and password on
    PyPI to do so.

    .. code-block:: console

        publish_to_pypi.sh <version-number>

    If all goes fine, you should be able to install the release using
    the ``pip`` command:

    .. code-block:: console

        pip install --index-url https://test.pypi.org/simple/
        snowmicropyn==<version-number>


.. _PEP440: https://www.python.org/dev/peps/pep-0440/