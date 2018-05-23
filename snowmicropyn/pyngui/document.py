from snowmicropyn import proksch2015


class Document:

    def __init__(self, profile):
        self._profile = profile
        self._derivatives = None
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

    def recalc_derivatives(self, window_size, overlap_factor):
        samples = self.profile.samples

        surface = self.profile.marker('surface', samples.distance.iloc[0])
        ground = self.profile.marker('ground', samples.distance.iloc[-1])

        samples = samples[samples.distance.between(surface, ground)]

        self._derivatives = proksch2015.calc(samples, window_size, overlap_factor)
