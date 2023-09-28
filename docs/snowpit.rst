Snow pit measurements
=====================

The SnowMicroPen_ (SMP) measures penetration force of a cone driven into the
snowpack from above. It delivers output in form of applied force at penetration
depth at high resolution.

This signal is quite dense in information given that the SMP probes the
mechanical failure of snow, albeit maybe a bit hard to interpret directly in the
field.

For the (software) lab however, the SMP offers an objective method of
measurement delivering data in a timely manner which would be an impossible
undertaking by traditional methods. There exist accompanying routines to
meaningfully derive some fundamental quantities like the density and grain size
from this signal so that the relevance to the practitioner is immediate.

This satisfies a great variety of scientific research applications but it leaves
something to be desired for daily field work where information flow may be
tailored to more traditional types of information like the grain shapes.

Luckily, the SMP's force profile is such a significant gain in information that
it is possible to derive almost all data that would also be gathered in a manual
snow pit from it - within certain limitations. Due to the complexity of snow,
the connections between its properties and whichever set of micro-parameters are
far from being fully understood. Therefore, the farther removed the derived
quantities are from the raw SMP signal the more stochastic the calculation
models become. For example, snowmicropyn does calculate the grain shapes for an
SMP signal, but learning which SMP micro-parameters are tied to a certain snow
type is left to a machine learning algorithm since this problem has not been
solved reliably by other means yet.

This page is meant to describe the modules implemented in snowmicropyn that
derive micro- and macro-parameters of the system and therefore transform a raw
SMP signal into a full simulated snow pit.

Micromechanical properties - A shot noise model
-----------------------------------------------

Löwe et al. showed with a `shot noise approach`_ that some microstructural
parameters of the snowpack can be be deduced from the analytical solution of a
stochastic model. To this end the penetration force of the SMP cone can be
interpreted as a Poisson shot noise process and can be simulated as such, giving
a statistical but principally rigorous solution.

The following quantities are commonly derived from the SMP signal and are also
computed as a first step in snowmicropyn (via statistical moments of the
dataset):

#. f_0

   The rupture strength.

#. delta

   The deflection at rupture.
   The entire one-point statistics of the penetration force F solely depend on
   the product lambda*delta. Hence, to estimate both parameters a higher order
   correlation function is chosen: the force covariance. The simplest estimate
   for delta can be inferred from the slope of the correlation function at
   origin.

#. lambda

   Intensity of the Poisson point process.

#. L
   
   The element size. This is the average distance between neighboring elements.
   Since the (projected) area of the SMP A is fixed the element size and
   intensity can be related by lambda = A/L^3. This relation quantifies
   assumptions about the spatial distribution of snow grains when propagating
   the information from the one-dimensional force characteristics to the
   three-dimensional snowpack.

In short, first the non-central moments of the SMP force are estimated in a
finite window. Second, an estimate of the cumulants can be obtained from their
relation to the non-central moments. From these, lambda*delta and f0 can be
calculated from combinations of the mean and variance, and finally delta through
the covariance of the force signal.

Macro parameters - Regression
-----------------------------

Relating stratigraphic parameters to physical properties of snow is a topic of
ongoing research. However, the importance of density and grain size as
fundamental characteristics of the snow samples become clear in many
applications, including snow models. With these two morphometric measures, key
properties such as thermal conductivity, dielectric permittivity or air
permeability can be computed.

The underlying idea of the statistical model employed here is that repeated
elastic increases of the force followed by small elastic deflections of length
delta correspond to the SMP cone breaking through snow crystals separated by air
gaps.

Ground truth measurements about density and SSA were originally sampled by means
of Micro-CT. Meanwhile however snowmicropyn offers a couple of parameterizations
that were obtained by various methods for different SMP devices and climate 
settings. In any case SMP measurements were performed at the observation sites
to calibrate the density and SSA models with.

#. Density

   The statistical model for the snow density has evolved to include more than
   just the (logarithm of) the penetration force. Snowmicropyn offers a
   comprehensive developer's API, and depending on new publications the models
   may look slightly or completely different. Which parameterization to use
   depends on the SMP device and wide-scale snow conditions. Early successfull
   attempts to estimate the density are of the bilinear form:

   aa[0] + aa[1] * np.log(F_m) + aa[2] * np.log(F_m) * LL + aa[3] * LL

   and a couple of parameter sets for this model are provided in snowmicropyn.
   See :doc:`api_reference` for further details.

#. Specific Surface Area (SSA)

   Again, snowmicropyn provides the framework to include new calibrations at
   hand, giving the option to choose from a number of publications.
   The SMP length scale L lends itself to start a regression on, and indeed
   already a direct comparison reveals a correlation to the length scales
   derived from independent measurements. To account for varying snow types
   (e. g. different densities in different climate settings) a linear regression
   for the SMP variables L and ln(F) can be used (for example).
   Read more at :doc:`api_reference`.

#. Hardness

   The force needed for the SMP's cone to break up the crystal structure and
   drive through the snow is not the same as when measuring snow hardness via
   the hand hardness index where snow is being displaced horizontally. The hand
   hardness index (from "new snow" to "ice") is estimated with a power law fit
   through a graph connecting SMP to manual hand hardness index measurements
   using a few data points from `a dedicated experiment`_.

#. Grain size

   The grain size is indirectely proportional to the SSA, so we have this
   already.

Snow grain shapes - Machine Learning
------------------------------------

Current theoretical efforts hope to find a fundamental model to connect an SMP
measurement with the observed type of snow. Until such methods are successfull
we try to simulate the model with standard machine learning techniques.

Since the micro-parameters derived by the shot noise model have a physical
meaning they are used together with the force signal to fit a machine learning
model to the data and predict the snow type, i. e. the grain shape.

Snowmicropyn allows the user to choose from a set of different machine learning
routines together with minimalistic algorithms for data pre-processing and
resampling. In the future hopefully more sophisticated functions to compare,
warp and merge profiles will be offered.

Operational application
-----------------------

A great benefit of having a "manual-like" profile at hand after performing SMP
measurements is that certain snowpack models can be started with this kind of
information. It remains to be seen how quickly a snow model driven by SMP data
will stabilize its own (potentially different) microstructure parameters and
produce reliable output in the form of macroscopical observables like the grain
shape.

Apart from a whole range of practical challenges however the path is principally
clear: we can take the SMP into the field, record some bits of meta data like
the slope angle and air temperature and feed this data to a computer.
Snowmicropyn can then produce standardized CAAML output. This together with
meteorological weather forecast data can drive climate models to analyze and
predict the snow stratigraphy for the observation site fully automatically.

Summary
-------

An SMP measurement is quick and objective, and snowmicropyn can derive the
necessary snowpack properties needed to drive operational forecasting tools
(with varying complexity and trustworthiness of the estimated parameters).

.. _shot noise approach: https://www.sciencedirect.com/science/article/abs/pii/S0165232X11001832
.. _a dedicated experiment: https://www.dora.lib4ri.ch/wsl/islandora/object/wsl%3A17105/datastream/PDF/Pielmeier-2016-Characterizing_snow_stratigraphy-%28published_version%29.pdf
.. _SnowMicroPen: https://www.cambridge.org/core/journals/annals-of-glaciology/article/constantspeed-penetrometer-for-highresolution-snow-stratigraphy/5D0A9FDD8CF4754303D1A2B09634335B
