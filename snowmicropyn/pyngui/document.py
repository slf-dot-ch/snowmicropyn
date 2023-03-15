from snowmicropyn import loewe2012, derivatives, Profile
from snowmicropyn.ai.grain_classifier import grain_classifier
from snowmicropyn.derivatives import parameterizations as params
from snowmicropyn.parameterizations.proksch2015 import Proksch2015
from snowmicropyn.serialize import caaml
import pathlib

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

    def recalc_derivatives(self, relativize=False):
        samples = self._profile.samples_within_snowpack(relativize)

        # A dictionary is built with the parameterization's shortname as the key,
        # and a pandas dataframe containing the (distance, parameters) datapoints
        # for this parameterization:
        self._derivatives = {}
        for key, par in params.items():
            self._derivatives[key] = par.calc(samples)

    def export_caaml(self, outfile=None, parameterization='P2015', export_settings={}):

        # Prepare samples:
        samples = self._profile.samples_within_snowpack()

        # Prepare derivatives:
        param = params[parameterization]
        loewe2012_df = loewe2012.calc(samples, param.window_size, param.overlap)
        derivatives = loewe2012_df
        derivatives = derivatives.merge(param.calc_from_loewe2012(loewe2012_df))

        if outfile:
            outfile = pathlib.Path(outfile)
        else:
            # add _smp flag to file name in order to (hopefully) not overwrite hand profiles:
            outfile = self._profile._pnt_file.with_name(f'{self._profile._pnt_file.stem}_smp').with_suffix('.caaml')

        grain_shapes = {}
        if export_settings.get('export_grainshape', False):
            classifier = grain_classifier(export_settings)
            grain_shapes = classifier.predict(loewe2012_df)

        caaml.export(export_settings, derivatives, grain_shapes,
            self._profile._pnt_file.stem, self._profile._timestamp, self._profile._smp_serial,
            self._profile._longitude, self._profile._latitude, outfile)
        return outfile
