from snowmicropyn import proksch2015


class Document:

    def __init__(self, profile):
        self._profile = profile
        self._model_df = None
        self._drift = None
        self._offset = None
        self._noise = None
        self._fit_x = None
        self._fit_y = None

    @property
    def profile(self):
        return self._profile

    @property
    def model_df(self):
        return self._model_df

    def recalc_model(self, window_size, overlap_factor):
        self._model_df = proksch2015.model_ssa_and_density(self._profile.samples, window_size, overlap_factor)