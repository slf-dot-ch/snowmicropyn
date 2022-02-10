"""Backend for "custom" parameterizations.

An important design goal is to offer a most easy to use interface to add new
parameterizations with as little effort as possible. The functions here are
housekeeping for this to keep the core code short.
On startup, we auto-load all modules in 'parameterizations' giving us a list
of the available processing elements. In here we handle this list and offer
some generic/common functionality.
Neither the end user nor the parameterization developer should need to interact
with this.
"""

import snowmicropyn.windowing
import pandas as pd
import numpy as np

class Parameterizations:
    def __init__(self):
        self._parameterizations = {}

    def __getitem__(self, key):
        return self.get(key)

    def register(self, param):
        """Make a new parameterization available.

        :param param: An instance of a ready-to-use parameterization class.

        If there is a parameterization class Proksch2015() available, then
        an instance of it can be registered here to be available throughout
        snowmicropyn, cf. the examples.
        """
        self._parameterizations[param.shortname] = param

        # auto-choose a color depending on the number of similar plots:
        rgb = lambda rr, gg, bb: '#%02x%02x%02x' % (rr, gg, bb)
        offset = 25
        param._density_color = rgb(100, 0, len(self._parameterizations) * offset);
        param._ssa_color = rgb(0, offset + len(self._parameterizations) * offset, 0);

    def get(self, author): # get by .shortname property
        param = self._parameterizations.get(author)
        if not param: # this parameterization is not known
            raise ValueError(author)
        return param

    def __iter__(self): # delegate calls to make iterable
        return iter(self._parameterizations)

    def keys(self):
        return self._parameterizations.keys()

    def items(self):
        return self._parameterizations.items()

    def values(self):
        return self._parameterizations.values()

class Derivatives:
    """Base class for all parameterizations.

    In this class we collect code common to all parameterizations, e. g. the
    stepping through the samples to calculate derivatives.
    """
    color_density = None # will be auto-chosen in Parameterizations.register()
    color_ssa = None

    def calc_step(self, force_median, element_size, lamb, f0, delta):
        density = self.density(force_median, element_size, lamb, f0, delta)
        # Calculation of the SSA is optional. We check it this way so that someone
        # writing a new parameterization does not have to set it to Null or something:
        if hasattr(self, 'ssa'):
            ssa = self.ssa(density, force_median, element_size, lamb, f0, delta)
        else:
            ssa = np.nan
        return density, ssa

    def calc_from_loewe2012(self, shotnoise_dataframe):
        """Calculate ssa and density from a pandas dataframe containing shot noise
        model values.

        :param shotnoise_dataframe: A pandas dataframe containing shot noise model values.
        :return: A pandas dataframe with the columns distance, density and ssa.
        """
        result = []
        for index, row in shotnoise_dataframe.iterrows():
            density, ssa = self.calc_step(row.force_median, row.L2012_L, row.L2012_lambda,
                row.L2012_f0, row.L2012_delta)
            result.append((row.distance, density, ssa))
        return pd.DataFrame(result, columns=['distance', self.shortname + '_density', self.shortname + '_ssa'])

    def calc(self, samples):
        """Calculate ssa and density from a pandas dataframe containing the samples
        of a SnowMicroPen recording.

        :param samples: A pandas dataframe containing the columns 'distance' and 'force'.
        :param window: Size of window in millimeters.
        :param overlap: Overlap factor in percent.
        :return: A pandas dataframe with the columns distance, density and ssa.
        """
        sn = snowmicropyn.loewe2012.calc(samples, self.window_size, self.overlap)
        result = []
        for index, row in sn.iterrows():
            density, ssa = self.calc_step(row.force_median, row.L2012_L, row.L2012_lambda,
                row.L2012_f0, row.L2012_delta)
            result.append((row.distance, density, ssa))
        return pd.DataFrame(result, columns=['distance', self.shortname + '_density', self.shortname + '_ssa'])

parameterizations = Parameterizations() # access throughout SMPyn via this
