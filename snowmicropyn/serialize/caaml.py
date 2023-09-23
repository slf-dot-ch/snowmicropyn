"""This file handles data serialization to the CAAML format. It packs measured SMP
forces and derived quantities to an XML. It also handles the calculations and
parameterizations necessary to build a CAAML stratigraphy profile."""

import logging
import pandas as pd
from scipy.ndimage import gaussian_filter
from scipy.optimize import curve_fit
import xml.etree.ElementTree as ET

from snowmicropyn.pyngui.globals import VERSION

log = logging.getLogger('snowmicropyn')
_ns_caaml = 'caaml' # XML namespaces
_ns_gml = 'gml'
_ns = {_ns_caaml: 'http://caaml.org/Schemas/SnowProfileIACS/v6.0.3', _ns_gml: 'http://www.opengis.net/gml'}

def _get_parameterization_name(derivatives):
    """Check the column names of a data frame to deduce which parameterization
    was used for the calculation.

    param derivatives: Pandas dataframe with derived SMP quantities.
    returns: Short name of the used parameterization (e. g. 'P2015').
    """
    flag = '_density'
    _, ax = derivatives.axes
    for col in ax:
        if len(col) > len(flag):
            if col[-len(flag):] == flag:
                return col[:-len(flag)]
    return None

def hand_hardness(smp_force, method='regression'):
    """Parameterization of the measured SMP forces to hand hardness index.

    param smp_force: Penetration force as measured by the SMP in N.
    param method: Method of parameterization as string identifier (e. g. 'regression').
    returns: Hand hardness index.
    """
    if method == 'naive':
        return hand_hardness_naive(smp_force)
    elif method == 'regression':
        return hand_hardness_regression(smp_force)

def hand_hardness_label(smp_force, method='regression'):
    """Parameterization of the measured SMP forces to hand hardness label.

    param smp_force: Penetration force as measured by the SMP in N.
    returns: Hand hardness as a text label.
    """
    idx = hand_hardness(smp_force, method)
    return _hardness_index_to_identifier(idx)

def _hardness_index_to_identifier(index):
    """Numeric hand hardness index to text label.

    param index: Hand hardness index (int or float).
    returns: Text label for hand hardness index.
    """
    id_map = {1: 'F-', 1.5: 'F+', 2: '4F', 2.5: '4F+', 3: '1F', 3.5: '1F+',
        4: 'P', 4.5: 'P+', 5: 'K', 5.5: 'K+', 6: 'I'}
    if index < 1:
        index = 1
    elif index > 6:
        index = 6
    index = round(index * 2) / 2 # round to .5
    return id_map[index]

def _get_hardness_fit(recalc=False):
    """Parameterization through regression (measured SMP force and hand hardness index).
    Data points provided by van Herwijnen, Pielmeier: Characterizing Snow Stratigraphy:
    a Comparison of SP2, Snowmicropen, Ramsonde and Hand Hardness Profiles, ISSW Proceedings 2016

    param recalc: Set to True to reproduce the fit parameters on the fly.
    returns: Fitted function as function object.
    """
    hardness_func = lambda xx, aa, bb : aa * xx**bb # use a power law fit
    if recalc:
        smp_force_kPa = [4.9303, 11.1914, 17.6419, 37.5721, 49.8849, 104.0583, 124.8842, 314.3845]
        hand_hardness = [1, 1.5, 2, 2.5, 3, 3.5, 4, 5]
        A_smp = 19.6e-6 # area of penetration of SMP as used by authors (in m^2)
        smp_force_N = [ff * A_smp * 1000 for ff in smp_force_kPa]
        (aa, bb), _ = curve_fit(hardness_func, smp_force_N, hand_hardness)
    else:
        aa = 2.780171583411649 # running the above code unmodified yields these fit parameters
        bb = 0.341486204481987

    fit_func = lambda xx : hardness_func(xx, aa, bb)
    return fit_func

def hand_hardness_regression(smp_force):
    """Parameterization method for hand hardness index.
    See above for implementation details.

    param smp_force: The measured force in N.
    returns: Hand hardness index.
    """
    fit_func = _get_hardness_fit()
    return fit_func(smp_force)

def hand_hardness_naive(force):
    """Parameterization method for hand hardness index.
    Mapping of N to hand hardness according to ICSSG p. 6. This can not
    be used directly with an SMP measurement.

    param force: Penetration force measured by hand (not with an SMP).
    returns: Hand hardness index.
    """
    if force <= 50:
        return 1 # fist
    elif force <= 175:
        return 2 # 4 fingers
    elif force <= 390:
        return 3 # 1 finger
    elif force <= 715:
        return 4 # pencil
    elif force <= 1200:
        return 5 # knife
    else:
        return 6 # ice (sometimes "-")

def optical_thickness(ssa):
    """Calculation of a snow grain's diameter via the specific surface area as explained in
    `Representation of a nonspherical ice particle by a collection of independent spheres for
    scattering and absorption of radiation <https://doi.org/10.1029/1999JD900496>`_ by
    Thomas C. Grenfell and Stephen G. Warren publicised in `Journal of Geophysical
    Research <https://agupubs.onlinelibrary.wiley.com/doi/abs/10.1029/1999JD900496>`_,
    Volume 104, 1999.

    param ssa: Specific surface area in m^2/kg.
    returns: Optical thickness ("diameter") of particle in m.
    """
    DENSITY_ICE = 917.
    d_eff = 6 / (DENSITY_ICE * ssa) # r_eff=3V/A ==> d_eff=6/(rho_ice*SSA)
    return d_eff

def force_smoothing(derivatives, sigma):
    """Signal smoothing for the measured forces.

    param derivatives: Pandas dataframe with derived SMP quantities (including the
    median force).
    param sigma: Standard deviation for Gaussian kernel.
    returns: Pandas dataframe with derivatives where the force values were smoothed.
    """
    mod_derivs = derivatives.copy(deep=True) # make clear it is not a view (silences warning)
    mod_derivs.force_median = gaussian_filter(mod_derivs.force_median, sigma=sigma)
    return mod_derivs

def noise_threshold(derivatives, thresh):
    """Signal cutoff for the measured forces. Be aware that low-density snow types can have
    a poor signal to noise ratio.

    param derivatives: Pandas dataframe with derived SMP quantities.
    thresh: Threshold below which data is dropped in N.
    returns: Pandas dataframe with derivatives where low force values were removed.
    """
    derivatives = derivatives[derivatives.force_median > thresh]
    return derivatives

def remove_negatives(derivatives):
    """Remove measurements that contain negative values. This concerns parameters that we
    output which would not fit the CAAML standard if negative (force, density, SSA).

    param derivatives: Pandas dataframe with derived SMP quantities.
    returns: Pandas dataframe with rows removed where any observable is negative.
    """
    grain_col = pd.Series(dtype=float)
    if 'grain_shape' in derivatives: # we can not ask 'int >= str?'
        grain_col = derivatives.grain_shape # so we keep a copy of the shapes if available
        derivatives = derivatives.drop('grain_shape', axis=1) # and work the rest without
    valid_pos = (derivatives >= 0).all(axis = 1)
    derivatives = derivatives[valid_pos]
    derivatives.reset_index(drop=True, inplace=True)
    if len(grain_col) > 0: # re-append grain shapes
        grain_col = grain_col[valid_pos]
        grain_col.reset_index(drop=True, inplace=True)
        derivatives = pd.concat([derivatives, grain_col.to_frame()], axis=1)
    return derivatives

def _chunkup_derivs(derivatives, grain_shapes, similarity_percent):
    """Split up SMP data into regions where we can make a guess that the snow type is the same.
    Data rows are deemed to belong to the same layer if a) the grain shape is the same and
    b) no low-level derivative differs too greatly.

    param derivatives: Pandas dataframe with derived SMP quantities.
    param grain_shapes: List of grain shapes (one entry per SMP data row).
    param similarity_percent: The quantities that are compared may be +/- this many percent
    compared to the previous data row in order to belong to the same layer.
    returns:
      - List of pandas dataframes where each entry represents a layer in the stratigraphy
        profile and contains a block of the original derivatives.
      - List of grain shapes associated with each layer.
    """
    chunks = []
    shapes = []
    layer_start = 0

    for ii in range(1, len(derivatives)): # run through rows (1st is always in 1st layer)
        new = False

        if len(grain_shapes) > 0 and grain_shapes[ii] != grain_shapes[ii - 1]: # grain shape different --> different layer
            new = True

        if not new: # same grain shape - check microparameters
            all_within = True # are all values within a few % of their predecessors?
            for jj in range(1, len(derivatives.columns)):
                if derivatives.iat[ii, jj] < derivatives.iat[ii - 1, jj] * (100 - similarity_percent) / 100:
                    all_within = False
                    break
                if derivatives.iat[ii, jj] > derivatives.iat[ii - 1, jj] * (100 + similarity_percent) / 100:
                    all_within = False
                    break
            if not all_within: # at least 1 value is outside of our allowed range --> different layer
                new = True

        if new or ii == len(derivatives) - 1:
            chunks.append(derivatives.iloc[layer_start:ii]) # start of last layer to previous element
            if len(grain_shapes) > 0:
                shapes.append(grain_shapes[ii - 1]) # keep one list entry for the grain shape for each layer
            layer_start = ii # current element is start of new layer

    log.info(f'CAAML export: Reduced sample size from {len(derivatives)} to {len(chunks)} by merging layers')
    return chunks, shapes

def merge_layers(derivatives, grain_shapes, similarity_percent):
    """Merge multiple SMP data rows to single snow profile layers.
    Data rows are deemed to belong to the same layer if a) the grain shape is the same and
    b) low-level derivatives do not differ too greatly.

    param derivatives: Pandas dataframe with derived SMP quantities.
    param grain_shapes: List of grain shapes (one entry per SMP data row).
    param similarity_percent: The quantities that are compared may be +/- this many percent
    returns:
      - Pandas dataframe in the shape of the original derivatives, but resampled via
        averaging over each separate layer.
      - List of grain shapes associated with each layer.
      - Penetration depth at the end of the profile (in order to be able to calculate the
        thickness of the last layer).
    """
    chunks, shapes = _chunkup_derivs(derivatives, grain_shapes, similarity_percent)
    merged = pd.DataFrame()
    for chunk in chunks:
        top = chunk.iloc[0].distance
        med = chunk.median() # average all measured values (use median like for the force)...
        med.distance = top # ... except for the distance, which will now represent "top of layer"
        merged = pd.concat([merged, med.to_frame().T], ignore_index=True) # rebuild single data frame
    bottom = chunks[-1].iloc[-1].distance # throw away chunks but remember the full profile depth
    return merged, shapes, bottom

def discard_thin_layers(derivatives, grain_shapes, profile_bottom, min_thickness):
    """Exclude layers below a certain thickness.

    param derivatives: Pandas dataframe with derived SMP quantities.
    param grain_shapes: List of grain shapes (one entry per SMP data row).
    param profile_bottom: Depth of last SMP measurement (which may now me merged into some layer).
    param min_thickness: Minimal allowed thickness of the layer.
    returns:
      - Pandas dataframe with the derivatives excluding thin layers.
      - List of grain shapes associated with each layer.
      - Depth at the end of the profile (bottom layers may have been merged/removed).
    """
    drop_indices = [] # list of indices to drop in the end
    update_bottom = False # can only become True in last iteration
    for idx, row in derivatives.iterrows():
        if idx == len(derivatives) - 1: # last layer
            thickness = profile_bottom - row.distance
            update_bottom = True # if the layer is removed we will move the bottom
        else:
            thickness = derivatives['distance'][idx + 1] - row.distance
        if thickness < min_thickness:
            drop_indices.append(idx)
            if update_bottom:
                profile_bottom = row.distance # it was the last layer
    derivatives.drop(drop_indices, inplace=True)
    derivatives.reset_index(inplace=True)
    return derivatives, grain_shapes, profile_bottom

def preprocess_lowlevel(derivatives, export_settings):
    """Basic signal pre-processing before layer merging. Depending on the export settings
    this can be to remove negative forces and derivatives, set a noise threshold, or
    perform data smoothing.

    param derivatives: Pandas dataframe with derived SMP quantities.
    param export_settings: Dictionary with export settings. Relevant to this routine are
    the settings/dictionary keys 'remove_negative_data' (bool), 'remove_noise', (bool)
    'noise_threshold' (float) and 'smoothing' (bool).
    returns: Pandas dataframe with the pre-processed derivatives.
    """
    if export_settings.get('remove_negative_data', False):
        derivatives = remove_negatives(derivatives)
    if export_settings.get('remove_noise', False) and export_settings['noise_threshold']:
        derivatives = noise_threshold(derivatives, float(export_settings['noise_threshold']))
    if export_settings.get('smoothing', False):
        derivatives = force_smoothing(derivatives, sigma=0.5)
    return derivatives

def preprocess_layers(derivatives, grain_shapes, export_settings):
    """Advanced signal pre-processing based on layer identification. Depending on the export
    settings this can be to merge layers, or to remove thin layers.

    param derivatives: Pandas dataframe with derived SMP quantities.
    param grain_shapes: List of grain shapes (one entry per SMP data row).
    param export_settings: Dictionary with export settings. Relevant to this routine are
    the settings 'merge_layers' (bool), 'discard_thin_layers' (bool)
    and 'discard_layer_thickness' (float).
    returns:
      - Pandas dataframe with the pre-processed derivatives.
      - List of grain shapes associated with each layer.
      - Depth at the end of the profile (bottom layers may have been merged/removed).
    """
    profile_bottom = derivatives.iloc[-1].distance # if nothing is merged/removed this will be the bottom
    if export_settings.get('merge_layers', False):
        sim_percent = float(export_settings.get('similarity_percent', 500))
        derivatives, shapes, profile_bottom = merge_layers(derivatives, grain_shapes, sim_percent)
    if export_settings.get('discard_thin_layers', False) and export_settings['discard_layer_thickness']:
        derivatives, grain_shapes, profile_bottom = discard_thin_layers(derivatives, grain_shapes,
            profile_bottom, float(export_settings['discard_layer_thickness']))
    return derivatives, grain_shapes, profile_bottom

def export(settings, derivatives, grain_shapes, prof_id, timestamp, smp_serial,
    longitude, latitude, altitude, outfile):
    """CAAML export of an SMP snow profile with forces and derived values. This routing writes
    a CAAML XML file containing:
      - A stratigraphy profile with layers as would be contained in a manual snow profile.
        The observables in here are parameterized by means of regressions and machine learning.
      - A density profile. The values are parameterized from a shot noise model for the SMP forces.
      - A specific surface are profile. The values are parameterized from a shot noise model for the
        SMP forces.
      - A hardness profile. These are the directly measured SMP forces (but resampled and pre-processed).

    param settings: Dictionary with export settings. Relevant to this routine are the settings/dictionary
    keys 'location_name', 'altitude', 'slope_exposition' and 'slope_angle'. In addition, please have a
    look at the subroutines that are called.
    param derivatives: Pandas dataframe with derived SMP quantities.
    param grain_shapes: List of grain shapes (one entry per SMP data row).
    param prof_id: Profile id which will be written in the 'id' attribute.
    param timestamp: Date and time of measurement.
    param smp_serial: Serial number of the SMP device.
    param longitude: Longitude of point of measurement.
    param latitude: Latitude of point of measurement.
    param outfile: Filename to save to.
    """
    mm2cm = lambda mm : mm / 10
    m2mm = lambda m : m * 1000
    cm2m = lambda cm : cm / 100
    parameterization = _get_parameterization_name(derivatives)

    # We keep two sets of derivatives: one for the stratigraphy profile with merged layers and
    # one with only basic pre-processing for the embedded density, SSA and hardness profiles
    # (because we don't want only 1 data point per thick layer for the embedded profiles):
    derivatives = preprocess_lowlevel(derivatives, settings)
    layer_derivatives, grain_shapes, profile_bottom = preprocess_layers(derivatives,
        grain_shapes, settings)

    # Meta data:
    root = ET.Element(f'{_ns_caaml}:SnowProfile')
    root.set(f'xmlns:{_ns_caaml}', _ns[_ns_caaml])
    root.set(f'xmlns:{_ns_gml}', _ns[_ns_gml])
    root.set(f'{_ns_gml}:id', prof_id)

    meta_data = ET.SubElement(root, f'{_ns_caaml}:metaData')
    _addGenericComments(meta_data, parameterization)

    time_ref = ET.SubElement(root, f'{_ns_caaml}:timeRef')
    rec_time = ET.SubElement(time_ref, f'{_ns_caaml}:recordTime')
    time_inst = ET.SubElement(rec_time, f'{_ns_caaml}:TimeInstant')
    time_pos = ET.SubElement(time_inst, f'{_ns_caaml}:timePosition')
    time_pos.text = timestamp.isoformat()

    src_ref = ET.SubElement(root, f'{_ns_caaml}:srcRef')
    src_oper = ET.SubElement(src_ref, f'{_ns_caaml}:Operation')
    src_oper.set(f'{_ns_gml}:id', 'SMP_serial')
    src_name = ET.SubElement(src_oper, f'{_ns_caaml}:name')
    src_name.text = smp_serial

    loc_ref = ET.SubElement(root, f'{_ns_caaml}:locRef')
    loc_ref.set(f'{_ns_gml}:id', 'LOC_ID')
    loc_name = ET.SubElement(loc_ref, f'{_ns_caaml}:name')
    loc_name.text = settings.get('location_name', 'SMP observation point')
    obs_sub = ET.SubElement(loc_ref, f'{_ns_caaml}:obsPointSubType')
    obs_sub.text = 'SMP profile location'
    if altitude: # SMP altitude is in cm
        altitude = cm2m(altitude)
    else: # if no altitude is recorded by the SMP we insert the user chosen one
        altitude = settings.get('altitude')
    if altitude:
        valid_elevation = ET.SubElement(loc_ref, f'{_ns_caaml}:validElevation')
        val_el_pos = ET.SubElement(valid_elevation, f'{_ns_caaml}:ElevationPosition')
        val_el_pos.set('uom', 'm')
        caaml_position = ET.SubElement(val_el_pos, f'{_ns_caaml}:position')
        caaml_position.text = str(altitude)
    valid_aspect = ET.SubElement(loc_ref, f'{_ns_caaml}:validAspect')
    aspect_pos = ET.SubElement(valid_aspect, f'{_ns_caaml}:AspectPosition')
    caaml_aspect = ET.SubElement(aspect_pos, f'{_ns_caaml}:position')
    caaml_aspect.text = str(settings.get('slope_exposition', 0))
    valid_slope_angle = ET.SubElement(loc_ref, f'{_ns_caaml}:validSlopeAngle')
    valid_slope_angle = ET.SubElement(valid_slope_angle, f'{_ns_caaml}:SlopeAnglePosition')
    valid_slope_angle.set('uom', 'deg')
    caaml_angle = ET.SubElement(valid_slope_angle, f'{_ns_caaml}:position')
    caaml_angle.text = str(settings.get('slope_angle', 0))

    point_loc = ET.SubElement(loc_ref, f'{_ns_caaml}:pointLocation')
    point_pt = ET.SubElement(point_loc, f'{_ns_gml}:Point')
    point_pt.set(f'{_ns_gml}:id', 'pointID')
    point_pt.set('srsName', 'urn:ogc:def:crs:OGC:1.3:CRS84')
    point_pt.set('srsDimension', '2')
    point_pos = ET.SubElement(point_pt, f'{_ns_gml}:pos')
    point_pos.text = f'{longitude} {latitude}'

    # Stratigraphy profile:
    snow_prof = ET.SubElement(root, f'{_ns_caaml}:snowProfileResultsOf')
    snow_prof_meas = ET.SubElement(snow_prof, f'{_ns_caaml}:SnowProfileMeasurements')
    snow_prof_meas.set('dir', 'top down')
    strat_prof = ET.SubElement(snow_prof_meas, f'{_ns_caaml}:stratProfile')
    strat_meta = ET.SubElement(strat_prof, f'{_ns_caaml}:stratMetaData')

    for idx, row in layer_derivatives.iterrows():
        layer = ET.SubElement(strat_prof, f'{_ns_caaml}:Layer')
        depth_top = ET.SubElement(layer, f'{_ns_caaml}:depthTop')
        depth_top.set('uom', 'cm')
        depth_top.text = str(mm2cm(row['distance']))
        thickness = ET.SubElement(layer, f'{_ns_caaml}:thickness')
        thickness.set('uom', 'cm')
        if idx == len(layer_derivatives) - 1:
            layer_thickness = profile_bottom - row.distance
        else:
            layer_thickness = layer_derivatives.distance[idx + 1] - row.distance
        thickness.text = str(mm2cm(layer_thickness))
        if len(grain_shapes) > 0: # we have grain classification available
            grain_primary = ET.SubElement(layer, f'{_ns_caaml}:grainFormPrimary')
            grain_primary.text = grain_shapes[idx]
        grain_size = ET.SubElement(layer, f'{_ns_caaml}:grainSize')
        grain_size.set('uom', 'mm')
        grain_components = ET.SubElement(grain_size, f'{_ns_caaml}:Components')
        grain_sz_avg = ET.SubElement(grain_components, f'{_ns_caaml}:avg')
        grain_sz_avg.text = str(m2mm(optical_thickness(row[f'{parameterization}_ssa'])))
        grain_hardness = ET.SubElement(layer, f'{_ns_caaml}:hardness')
        grain_hardness.set('uom', '')
        grain_hardness.text = hand_hardness_label(row['force_median'])

    # Density profile:
    dens_prof = ET.SubElement(snow_prof_meas, f'{_ns_caaml}:densityProfile')
    dens_meta = ET.SubElement(dens_prof, f'{_ns_caaml}:densityMetaData')
    dens_meth = ET.SubElement(dens_meta, f'{_ns_caaml}:methodOfMeas')
    dens_meth.text = "other"

    for _, row in derivatives.iterrows():
        layer = ET.SubElement(dens_prof, f'{_ns_caaml}:Layer')
        depth_top = ET.SubElement(layer, f'{_ns_caaml}:depthTop')
        depth_top.set('uom', 'cm')
        depth_top.text = str(mm2cm(row['distance']))
        density = ET.SubElement(layer, f'{_ns_caaml}:density')
        density.set('uom', 'kgm-3')
        density_val = row[f'{parameterization}_density']
        density.text = str(density_val)

    # Specific surface area profile:
    ssa_prof = ET.SubElement(snow_prof_meas, f'{_ns_caaml}:specSurfAreaProfile')
    ssa_meta = ET.SubElement(ssa_prof, f'{_ns_caaml}:specSurfAreaMetaData')
    ssa_meth = ET.SubElement(ssa_meta, f'{_ns_caaml}:methodOfMeas')
    ssa_meth.text = "other"
    ssa_comp = ET.SubElement(ssa_prof, f'{_ns_caaml}:MeasurementComponents')
    ssa_comp.set('uomDepth', 'cm')
    ssa_comp.set('uomSpecSurfArea', 'm2kg-1')
    ssa_depth = ET.SubElement(ssa_comp, f'{_ns_caaml}:depth')
    ssa_res = ET.SubElement(ssa_comp, f'{_ns_caaml}:specSurfArea')
    ssa_meas = ET.SubElement(ssa_prof, f'{_ns_caaml}:Measurements')
    ssa_tuple = ET.SubElement(ssa_meas, f'{_ns_caaml}:tupleList')

    tuple_list = ''
    for _, row in derivatives.iterrows():
        tuple_list = tuple_list + str(mm2cm(row['distance'])) + "," + str(row[f'{parameterization}_ssa']) + " "
    ssa_tuple.text = tuple_list

    # Hardness profile:
    hard_prof = ET.SubElement(snow_prof_meas, f'{_ns_caaml}:hardnessProfile')
    hard_meta = ET.SubElement(hard_prof, f'{_ns_caaml}:hardnessMetaData')
    hard_meth = ET.SubElement(hard_meta, f'{_ns_caaml}:methodOfMeas')
    hard_meth.text = "SnowMicroPen"
    hard_comp = ET.SubElement(hard_prof, f'{_ns_caaml}:MeasurementComponents')
    hard_comp.set('uomDepth', 'cm')
    hard_comp.set('uomHardness', 'N')
    hard_depth = ET.SubElement(hard_comp, f'{_ns_caaml}:depth')
    hard_res = ET.SubElement(hard_comp, f'{_ns_caaml}:penRes')
    hard_meas = ET.SubElement(hard_prof, f'{_ns_caaml}:Measurements')
    hard_tuple = ET.SubElement(hard_meas, f'{_ns_caaml}:tupleList')

    tuple_list = ''
    for _, row in derivatives.iterrows():
        tuple_list = tuple_list + str(mm2cm(row['distance'])) + "," + str(mm2cm(row['force_median'])) + " "
    hard_tuple.text = tuple_list

    tree = ET.ElementTree(root)
    ET.indent(tree, space="\t", level=0) # human-readable CAAML
    tree.write(outfile, encoding="UTF-8", xml_declaration=True)

def _addGenericComments(cmt_root, parameterization: str):
    caaml_cmt = ET.SubElement(cmt_root, f'{_ns_caaml}:comment')
    cmt = f'This file was generated by snowmicropyn v{VERSION}: https://snowmicropyn.readthedocs.io/en/latest/. '
    cmt = cmt + f'All observables except for the SMP force and meta data are derived. Parameterization for density/SSA: "{parameterization}". '
    cmt = cmt + 'The SMP force signal contained here is preprocessed and downsampled (median force over a rolling window). Use csv export to obtain the raw SMP signal.'
    caaml_cmt.text = cmt

def parse_grainshape(caaml_file: str):
    """Get the layers entered in a (manual) CAAML snow profile.

    param caaml_file: Path to the CAAML file to parse.
    returns: List of layers. Each item is itself a list containing information about
    the depth and thickness of the layer as well as its grain shape.
    """
    tree = ET.parse(caaml_file)
    root = tree.getroot()
    strat = root.find(f"{_ns_caaml}:snowProfileResultsOf", _ns)
    strat = strat.find(f"{_ns_caaml}:SnowProfileMeasurements", _ns)
    strat = strat.find(f"{_ns_caaml}:stratProfile", _ns)

    extract_list = ["depthTop", "thickness", "grainFormPrimary"]
    layer_list = []
    for layer in strat.findall(f"{_ns_caaml}:Layer", _ns): # iterate through each snow layer
        attr_list = []
        for attr in extract_list:
            val = layer.find(f"{_ns_caaml}:{attr}", _ns).text
            try:
                val = float(val) # store as float if it's a number
            except:
                pass
            attr_list.append(val)
        layer_list.append(attr_list)

    return pd.DataFrame(layer_list, columns=extract_list)

