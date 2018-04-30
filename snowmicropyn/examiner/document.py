class Document:

    def __init__(self, profile):
        self._profile = profile
        self._ssa_density_df = profile.model_ssa()

    @property
    def profile(self):
        return self._profile

    @profile.setter
    def profile(self, value):
        self._profile = value

    @property
    def ssa_density_df(self):
        return self._ssa_density_df

    @ssa_density_df.setter
    def ssa_density_df(self, value):
        pass
