.. _develop:

Information for Developers of *snowmicropyn*
============================================

Compiling Icons Into a Python File
----------------------------------

The :program:`Examiner` application requires icons used in menus and toolbar
buttons. They are stored in the folder :file:`resources`. For easy deployment,
they are compiled into a python source file using the :command:`pyrcc5` tool,
which comes with the Qt package. Execute the following command when you did do
changes in the resources folder:

.. code-block:: console

    pyrcc5 -o snowmicropyn/examiner/icons.py resources/icons.qrc

This command generates an updated version of the file called :file:`icons.py`.
Don't ever edit this file manually.

Help, the icons are gone!
^^^^^^^^^^^^^^^^^^^^^^^^^

In case you're suddenly see no more icons when running :program:`Examiner`, it's
likely due to your IDE has optimized your imports and dropped the statement

.. code-block:: python

   import snowmicropyn.examiner.icons

as it seems to not have an effect. But it actually does. No icons without this
import statement!

Releasing a New Version of snowmicropyn
---------------------------------------


#. Update version string (``__version__``) in file
   :file:`snowmicropyn/__init__.py`

#. Make sure you updated the version string!

#. Commit you changes

   .. code-block:: console

      git commit -m "Some nice words about your changes"

#. Add an annotated tag in your repo

   .. code-block:: console

      git tag -a <version-number> -m "Version <version-number>"

   Some examples for <version-number>, also consider reading :pep:`440`.

   - ``v0.2.dev21`` (Development Release)
   - ``v0.2a4`` (Alpha Release)
   - ``v0.2b7`` (Beta Release)
   - ``v0.2.0`` (Final Release)
   - ``v0.2.11`` (Bugfix Release)

#. Push the Tag to GitHub

   .. code-block:: console

      git push origin <version-number>

#. Use the script :file:`publish_to_pypi.sh` to publish this release on PyPI.
   You'll be asked for your username and password on PyPI to do so.

   .. code-block:: console

      publish_to_pypi.sh <version-number>

   .. warning:: :command:`publish_to_pypi.sh` is a unix shell script. You won't be able
      to run it on Windows unless you install Cygwin_, Gow_ or a similar tool.

   If all goes fine, you should be able to install the release using the
   following commands:

        First, uninstall the current snowmicropyn package:

        .. code-block:: console

            pip uninstall snowmicropyn

        Then install the just released (latest) version:

        .. code-block:: console

            pip install --index-url https://test.pypi.org/simple/ --no-cache-dir snowmicropyn

.. _Cygwin: https://www.cygwin.com/
.. _Gow: https://github.com/bmatzelle/gow/wiki