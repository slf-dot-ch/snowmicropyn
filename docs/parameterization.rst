Custom Parameterizations
========================

Adding custom parameterizations to snowmicropyn
-----------------------------------------------

If you have derived or found a different way to deduce the density and/or
specific surface area from an SMP signal (for example for a different version
of the device or altogether different snow conditions) than what is included
in this package (Proksch, Calonne/Richter, King, ...) it is easy to add it
requiring only minimal programming skills.

We hope to offer an interface which will let you focus on the Physics.

Implementation
--------------

#. Copy a fitting template.

   Duplicate :file:`parameterizations/proksch2015.py` and rename it as a
   starting point. Give your class a fitting name, here `Custom2022`.

#. Choose your attributes.

   In the class' :meth:`__init__` function you will see a couple of variables
   being initialized, like a name and shortcut (here "C2022") for your algorithm.
   Set these accordingly.

#. Define your density and SSA functions.

   Your class must define the :meth:`density` function and may define the
   :meth:`ssa` function. These will be passed the lower level SMP properties (e. g.
   median of force, element size, and in case of SSA the density) by the calling
   chain to process to your liking. You can freely program your functions as long
   as they return a single float value.

#. Register your parameterization in the GUI.

   The last line like

   .. code-block:: python

      derivatives.parameterizations.register(Custom2022())

   registers your parameterization in the GUI and for a unified API by creating
   an instance of your class. The appropriate menus, save- and export
   functionality will automatically be added to the GUI. Furthermore, you can
   now access your custom algorithm like all the others:

   .. code-block:: python

      import snowmicropyn as smp
      pro = smp.Profile.load('../examples/profiles/S37M0876.pnt')
      c2022 = smp.params['C2022'].calc(pro.samples)

#. Document your work

   Documentation is built from source code, so adhering to commenting standards
   (or sticking to the template) should ensure easy integration.
   To insert your module, add it in :file:`docs/api_reference.rst`.

Colors
------
A color will be auto-chosen for your parameterization that is slightly different
to the existing ones. If you wish to override it you can do so after registering
the class:

   .. code-block:: python

      derivatives.parameterizations.register('Custom2022())
      rgb = lambda rr, gg, bb: '#%02x%02x%02x' % (rr, gg, bb)
      derivatives.parameterizations['C2022']._density_color = rgb(255, 0, 0) # RGB color
      derivatives.parameterizations['C2022']._ssa_color = 'C1' # matplotlib enumerated color


Publishing your Efforts
-----------------------

If your work is peer reviewed we are very happy to receive a pull request on
GitHub.
