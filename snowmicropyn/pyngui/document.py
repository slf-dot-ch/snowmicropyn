from snowmicropyn.derivatives import parameterizations as params

class Document:

    def __init__(self, profile):
        self._profile = profile
        self._derivatives = {}
        self._drift = None
        self._offset = None
        self._noise = None
        self._fit_x = None
        self._fit_y = None

    @property
    def profile(self):
        return self._profile

    @property
    def derivatives(self):
        return self._derivatives

    def recalc_derivatives(self):
        samples = self.profile.samples

        surface = self.profile.marker('surface', samples.distance.iloc[0])
        ground = self.profile.marker('ground', samples.distance.iloc[-1])

        samples = samples[samples.distance.between(surface, ground)]

        # A dictionary is built with the parameterization's shortname as the key,
        # and a pandas dataframe containing the (distance, parameters) datapoints
        # for this parameterization:
        self._derivatives = {}
        for key, par in params.items():
            self._derivatives[key] = par.calc(samples)
