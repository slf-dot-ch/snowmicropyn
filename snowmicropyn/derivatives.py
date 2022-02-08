import snowmicropyn.windowing
import pandas as pd

class Parameterizations:
    def __init__(self):
        self._parameterizations = {}

    def __getitem__(self, key):
        return self.get(key)

    def register(self, author, param):
        self._parameterizations[author] = param

        rgb = lambda rr, gg, bb: '#%02x%02x%02x' % (rr, gg, bb)
        offset = 50
        param._density_color = rgb(100, 0, offset + len(self._parameterizations) * offset);
        param._ssa_color = rgb(0, offset + len(self._parameterizations) * offset, 0);

    def get(self, author):
        param = self._parameterizations.get(author)
        if not param:
            raise ValueError(author)
        return param

    def __iter__(self):
        return iter(self._parameterizations)

    def keys(self):
        return self._parameterizations.keys()

    def items(self):
        return self._parameterizations.items()

    def values(self):
        return self._parameterizations.values()

class Derivatives:
    color_density = None # will be auto-chosen in Parameterizations.register()
    color_ssa = None

    def calc_step(self, median_force, element_size):
        density = self.density(median_force, element_size)
        ssa = self.ssa(density, median_force, element_size)
        return density, ssa

    def calc_from_loewe2012(self, shotnoise_dataframe):
        """Calculate ssa and density from a pandas dataframe containing shot noise
        model values.

        :param shotnoise_dataframe: A pandas dataframe containing shot noise model values.
        :return: A pandas dataframe with the columns distance, density and ssa.
        """
        result = []
        for index, row in shotnoise_dataframe.iterrows():
            density, ssa = self.calc_step(row.force_median, row.L2012_L)
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
            density, ssa = self.calc_step(row.force_median, row.L2012_L)
            result.append((row.distance, density, ssa))
        return pd.DataFrame(result, columns=['distance', self.shortname + '_density', self.shortname + '_ssa'])

parameterizations = Parameterizations()
