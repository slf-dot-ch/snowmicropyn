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

   In the class' :meth:`__init__` function you will see a couple of quite
   self-explanatory variables being initialized, like a name and shortcut for
   your algorithm. Set these accordingly.

#. Define your density and SSA functions.

   Your class must define the :meth:`density` and :meth:`ssa` functions. These
   will be passed the higher level SMP properties (median of force, element
   size, and in case of SSA the density) by the calling chain to process to your
   liking. You can freely program your functions as long as they return a single
   float value.

#. Register your parameterization in the GUI.

   The last line like

   .. code-block:: python

      derivatives.parameterizations.register('custom2022', Custom2022())

   registers your parameterization in the GUI and for a unified API by creating
   an instance of your class. The appropriate menus, save- and export
   functionality will automatically be added to the GUI. Furthermore, you can
   now access your custom algorithm like all the others:

   .. code-block:: python
   
      import snowmicropyn as smp
      pro = smp.Profile.load('../examples/profiles/S37M0876.pnt')
      c2021 = smp.params['custom2021'].calc(pro.samples)

Colors
------
A color will be auto-chosen for your parameterization that is slightly different
to the existing ones. If you wish to override it you can do so after registering
the class:

   .. code-block:: python

      derivatives.parameterizations.register('custom2022', Custom2022())
      rgb = lambda rr, gg, bb: '#%02x%02x%02x' % (rr, gg, bb)
      derivatives.parameterizations['custom2022']._density_color = rgb(255, 0, 0) # RGB color
      derivatives.parameterizations['custom2022']._ssa_color = 'C1' # matplotlib enumerated color


Publishing your Efforts
-----------------------

If your work is peer reviewed we are very happy to receive a pull request on
GitHub.
