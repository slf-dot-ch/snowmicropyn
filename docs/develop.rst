.. _develop:

Information for Developers of *snowmicropyn*
============================================

Necessary Accounts
------------------

To **develop** on *snowmicropyn*, you need a Github_ account. In case you've got
write access to the repository, you can push you changes directly. Otherwise
you have to send a pull request.

To **release** new versions of *snowmicropyn*, you need accounts on PyPI_ and
`test PyPI`_. The project maintainer must grant your account the necessary
rights so your user is able to deploy releases.

The documentation is built automatically on each code push, so as long as you
adhere to documentation standards everything should work out of the box.
To manage the **documentation**'s builds however you need an account on
`Read the Docs`_ (you can also use your GitHub account) where the control panel
will let you work on all branches. The project maintainer must grant your
account the necessary rights so your user is able to deploy releases.

Git Hash
--------

To identify a version of *snowmicropyn* more accurately than just its version
string, its git hash is added while publishing the package to PyPI. So in case a
developer forgets to update a version string (in file:`__init__.py`) before
releasing an update of *snowmicropyn*, it's still possible to identify what
exactly was released.

The git hash is written to the file :file:`snowmicropyn/githash` in the script
:command:`publish_to_pypi.sh`.

When using *snowmicropyn*, the hash of a release can be retrieved by method
:meth:`snowmicropyn.githash()`.

Compiling Icons Into a Python File
----------------------------------

The :program:`pyngui` application requires icons used in menus and toolbar
buttons. They are stored in the folder :file:`resources`. For easy deployment,
they are compiled into a Python source file using the :command:`pyrcc5` tool,
which comes with the Qt package. Execute the following command when you made
changes in the resources folder:

.. code-block:: console

    pyrcc5 -o snowmicropyn/pyngui/icons.py resources/icons.qrc

This command generates an updated version of the file called :file:`icons.py`.
Don't ever edit this file manually.

WTF, the icons are gone!
^^^^^^^^^^^^^^^^^^^^^^^^

In case you suddenly see no more icons when running :program:`pyngui`, it's
likely due to your IDE optimizing your imports and dropping the statement

.. code-block:: python

   import snowmicropyn.pyngui.icons

as it seems to not have an effect. But it actually does. No icons without this
import statement!

Releasing a New Version of *snowmicropyn*
-----------------------------------------

#. Commit your changes

.. code-block:: console

   git commit -m "Some nice words about your changes"

Also make sure you updated the documentation if necessary!

#. Run the unit tests

   This will (partly) make sure that the core functionality was not messed up.

#. Update version string (``__version__``) in file
   :file:`snowmicropyn/__init__.py`

   Some examples for <version-number>, also consider reading :pep:`440`:

   - ``v0.2.dev21`` (Development Release)
   - ``v0.2a4`` (Alpha Release)
   - ``v0.2b7`` (Beta Release)
   - ``v0.2.0`` (Final Release)
   - ``v0.2.11`` (Bugfix Release)

#. MAKE SURE YOU UPDATED THE VERSION STRING!

#. Add an annotated tag in your repo

   .. code-block:: console

      git tag -a v<version-number> -m "Version v<version-number>"

   .. note:: It's common to add a 'v' character in front of the version number in a git version tag.

#. Push the Tag to GitHub

   .. code-block:: console

      git push origin

#. Use the script :command:`publish_to_pypi.sh` to publish this release on PyPI.
   You have to provide the git tag which you want to release as a first
   parameter. In case you want to release to the hot PyPI (not test PyPI), you
   have to provide the string LIVE as a second parameter.

   The script will ask for your username and password on PyPI.

   .. code-block:: console

      publish_to_pypi.sh <version-number> LIVE

   .. note:: :command:`publish_to_pypi.sh` is a unix shell script. You won't
      be able to run it on Windows unless you install Cygwin_, Gow_ or a similar
      tool.

   If all goes fine, you should be able to install the release using the
   following commands:

   .. code-block:: console

      pip install --upgrade --no-cache-dir snowmicropyn

   In case you released to test PyPI:

   .. code-block:: console

      pip install --index-url https://test.pypi.org/simple/ --upgrade --no-cache-dir snowmicropyn

#. Release new documentation on Read the Docs.

.. _Github: https://github.com/
.. _PyPI: https://pypi.org/
.. _test PyPI: https://test.pypi.org/
.. _Read the Docs: https://readthedocs.org/
.. _Cygwin: https://www.cygwin.com/
.. _Gow: https://github.com/bmatzelle/gow/wiki

