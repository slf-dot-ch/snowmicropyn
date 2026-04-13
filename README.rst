snowmicropyn
============

A Python package to read, export and post process data (``*.pnt`` files)
recorded by SnowMicroPen_, a snow penetration probe for scientifc applications
developed at SLF_.

The software is open source and released under `GPL`_. Contributions are
welcome.

Installing
----------

Use a virtual environment (recommended), then install with either
``pip`` or ``uv``.

Using ``pip``

.. code-block:: console

    python -m venv .venv
    source .venv/bin/activate
    python -m pip install snowmicropyn

To upgrade in the same environment:

.. code-block:: console

    python -m pip install --upgrade snowmicropyn

Using ``uv``

.. code-block:: console

    uv venv
    uv pip install snowmicropyn

To upgrade in the same environment:

.. code-block:: console

    uv pip install --upgrade snowmicropyn

Editable install (development)

.. code-block:: console

    git clone https://github.com/slf-dot-ch/snowmicropyn.git
    cd snowmicropyn
    python -m venv .venv
    source .venv/bin/activate
    python -m pip install -e .

A Simple Example
----------------

.. code-block:: python

    from snowmicropyn import Profile

    p = Profile.load('/examples/profiles/S37M0876.ini')

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
.. _SnowMicroPen: https://www.slf.ch/en/about-the-slf/instrumented-field-sites-and-laboratories/snow-instruments/snowmicropenr/
.. _GPL: https://www.gnu.org/licenses/gpl-3.0.en.html
.. _documentation: https://snowmicropyn.readthedocs.io/
