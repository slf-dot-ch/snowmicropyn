from snowmicropyn import loewe2012, derivatives, Profile
from snowmicropyn.ai.grain_classifier import grain_classifier
from snowmicropyn.derivatives import parameterizations as params
from snowmicropyn.parameterizations.proksch2015 import Proksch2015
from snowmicropyn.serialize import caaml
import pathlib
import os
import atexit
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
import numpy as np


def _compute_loewe2012(samples, window_size, overlap):
    """Worker function for process pool.

    Runs loewe2012.calc in a separate process, which avoids the
    non-reentrant np.errstate(divide='raise') issue.
    """
    return loewe2012.calc(samples, window_size, overlap)


_EXECUTOR = None


def _shutdown_executor():
    global _EXECUTOR
    if _EXECUTOR is not None:
        _EXECUTOR.shutdown(wait=False)
        _EXECUTOR = None


def _get_executor():
    global _EXECUTOR
    if _EXECUTOR is None:
        _EXECUTOR = ProcessPoolExecutor(max_workers=max(1, os.cpu_count() or 1))
        atexit.register(_shutdown_executor)
    return _EXECUTOR

class Document:

    def __init__(self, profile):
        self._profile = profile
        self._derivatives = {}
        self._drift = None
        self._offset = None
        self._noise = None
        self._fit_x = None
        self._fit_y = None
        self._loewe_cache_signature = None
        self._loewe_cache_results = {}

    @property
    def profile(self):
        return self._profile

    @property
    def derivatives(self):
        return self._derivatives

    def recalc_derivatives_old(self, relativize=False):
        print("Calculating derivatives ... ", end="")
        samples = self._profile.samples_within_snowpack(relativize)
        for key, par in params.items():
            self._derivatives[key] = par.calc(samples)



    def recalc_derivatives(self, relativize=False):
        print("Calculating derivatives ... ", end="")
        samples = self._profile.samples_within_snowpack(relativize)

        # Group parameterizations by (window_size, overlap) so we compute
        # the expensive Löwe 2012 shot noise model only once per unique pair.
        groups = defaultdict(list)
        for key, par in params.items():
            groups[(par.window_size, par.overlap)].append((key, par))

        # Compute Löwe 2012 across groups.
        # ProcessPoolExecutor avoids the np.errstate reentrancy issue
        # (each process has its own numpy error state).
        loewe_results = {}
        group_keys = list(groups.keys())

        # Lightweight signature for cache invalidation.
        profile = self._profile
        if samples.empty:
            first_distance = 0.0
            last_distance = 0.0
        else:
            first_distance = float(samples.distance.iloc[0])
            last_distance = float(samples.distance.iloc[-1])
        signature = (
            bool(relativize),
            len(samples),
            first_distance,
            last_distance,
            float(profile.marker('surface', fallback=0) or 0),
            float(profile.marker('ground', fallback=0) or 0),
            float(getattr(profile, '_force_drift', 0.0)),
            float(getattr(profile, '_force_offset', 0.0)),
        )

        if signature != self._loewe_cache_signature:
            self._loewe_cache_signature = signature
            self._loewe_cache_results = {}

        missing_groups = [g for g in group_keys if g not in self._loewe_cache_results]

        def _store_and_warn(key, result):
            self._loewe_cache_results[key] = result
            if np.isinf(result['L2012_lambda']).any():
                loewe2012.log.warning(
                    'Constant signal - could not compute intensity of Poisson process'
                )
                if len(loewe2012.log.handlers) > 1:  # we are in the GUI
                    loewe2012.log.handlers[1].toTop()

        # For one group, avoid process/serialization overhead and run inline.
        if len(missing_groups) == 1:
            ws, ov = missing_groups[0]
            _store_and_warn((ws, ov), _compute_loewe2012(samples, ws, ov))
        elif len(missing_groups) > 1:
            executor = _get_executor()
            futures = {}
            for (ws, ov) in missing_groups:
                futures[(ws, ov)] = executor.submit(_compute_loewe2012, samples, ws, ov)
            for grp, future in futures.items():
                _store_and_warn(grp, future.result())

        for grp in group_keys:
            loewe_results[grp] = self._loewe_cache_results[grp]

        # Apply parameterization formulas (lightweight) using shared Löwe 2012 results
        self._derivatives = {}
        for (ws, ov), param_list in groups.items():
            sn = loewe_results[(ws, ov)]
            for key, par in param_list:
                self._derivatives[key] = par.calc_from_loewe2012(sn)
        print("done.")


    def export_caaml(self, outfile=None, parameterization='P2015', export_settings={}, binary=False):

        # Prepare samples:
        samples = self._profile.samples_within_snowpack()

        # Prepare derivatives:
        #param = params[parameterization]
        #loewe2012_df = loewe2012.calc(samples, param.window_size, param.overlap)
        #derivatives = loewe2012_df
        #derivatives = derivatives.merge(param.calc_from_loewe2012(loewe2012_df))

        derivatives = self._profile.calc_derivatives(snowpack_only=True, parameterization=parameterization,
            hand_hardness=True, optical_thickness=True, names_with_units=False)

        if not binary:
            # add _smp flag to file name in order to (hopefully) not overwrite hand profiles:
            stem = f'{self._profile._pnt_file.stem}_smp'
            if outfile:
                outfile = pathlib.Path(outfile) # full file name was given
                if outfile.is_dir(): # folder name was given -> choose filename
                    outfile = pathlib.Path(f'{outfile}/{stem}.caaml')
            else: # no name was given --> choose full path
                outfile = self._profile._pnt_file.with_name(stem).with_suffix('.caaml')

        loewe_derivs = derivatives[['distance', 'force_median', 'L2012_lambda', 'L2012_f0', 'L2012_delta', 'L2012_L']]

        grain_shapes = {}
        if export_settings.get('export_grainshape', False): # start machine learning process
            classifier = grain_classifier(export_settings)
            grain_shapes = classifier.predict(loewe_derivs)

        content = caaml.export(export_settings, derivatives, grain_shapes,
            self._profile.name, self._profile._timestamp, self._profile._smp_serial,
            self._profile._longitude, self._profile._latitude, self._profile._altitude, outfile,
            binary)
        return content
