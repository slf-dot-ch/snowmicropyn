import pandas as pd
import xml.etree.ElementTree as ET

_ns_caaml = 'caaml'
_ns_gml = 'gml'
_ns = {_ns_caaml: 'http://caaml.org/Schemas/SnowProfileIACS/v6.0.3', _ns_gml: 'http://www.opengis.net/gml'}

def hand_hardness(force):
    # ICSSG p. 6
    if force <= 50:
        return 'F'
    elif force <= 175:
        return '4F'
    elif force <= 390:
        return '1F'
    elif force <= 715:
        return 'P'
    elif force <= 1200:
        return 'K'
    else:
        return 'I'

def export(settings, samples, derivatives, grain_shapes, parameterization,
    location, prof_id, timestamp, smp_serial, longitude, latitude, outfile):

    mm2cm = lambda mm : mm / 10

    # Meta data:
    root = ET.Element(f'{_ns_caaml}:SnowProfile')
    root.set(f'xmlns:{_ns_caaml}', _ns[_ns_caaml])
    root.set(f'xmlns:{_ns_gml}', _ns[_ns_gml])
    root.set(f'{_ns_gml}:id', prof_id)

    meta_data = ET.SubElement(root, f'{_ns_caaml}:metaData')

    time_ref = ET.SubElement(root, f'{_ns_caaml}:timeRef')
    rec_time = ET.SubElement(time_ref, f'{_ns_caaml}:recordTime')
    time_inst = ET.SubElement(rec_time, f'{_ns_caaml}:TimeInstant')
    time_pos = ET.SubElement(time_inst, f'{_ns_caaml}:timePosition')
    time_pos.text = timestamp.isoformat()

    src_ref = ET.SubElement(root, f'{_ns_caaml}:srcRef')
    src_per = ET.SubElement(src_ref, f'{_ns_caaml}:Operation')
    src_per.set(f'{_ns_gml}:id', 'SMP_serial')
    src_name = ET.SubElement(src_per, f'{_ns_caaml}:name')
    src_name.text = smp_serial

    loc_ref = ET.Element(f'{_ns_caaml}:locRef')
    loc_ref.set(f'{_ns_gml}:id', 'LOC_ID')
    loc_name = ET.SubElement(loc_ref, f'{_ns_caaml}:name')
    loc_name.text = location
    obs_sub = ET.SubElement(loc_ref, f'{_ns_caaml}:obsPointSubType')
    obs_sub.text = 'SMP profile location'
    root.append(loc_ref)
    point_loc = ET.SubElement(loc_ref, f'{_ns_caaml}:pointLocation')
    point_pt = ET.SubElement(point_loc, f'{_ns_gml}:Point')
    point_pt.set(f'{_ns_gml}:id', 'pointID')
    point_pt.set(f'srsName', 'urn:ogc:def:crs:OGC:1.3:CRS84')
    point_pt.set(f'srsDimension', '2')
    point_pos = ET.SubElement(point_pt, f'{_ns_gml}:pos')
    point_pos.text = f'{longitude} {latitude}'

    # Stratigraphy profile:
    snow_prof = ET.SubElement(root, f'{_ns_caaml}:snowProfileResultsOf')
    snow_prof_meas = ET.SubElement(snow_prof, f'{_ns_caaml}:SnowProfileMeasurements')
    snow_prof_meas.set('dir', 'top down')
    strat_prof = ET.SubElement(snow_prof_meas, f'{_ns_caaml}:stratProfile')
    strat_meta = ET.SubElement(strat_prof, f'{_ns_caaml}:stratMetaData')

    for idx, row in derivatives.iterrows():
        layer = ET.SubElement(strat_prof, f'{_ns_caaml}:Layer')
        depth_top = ET.SubElement(layer, f'{_ns_caaml}:depthTop')
        depth_top.set('uom', 'cm')
        depth_top.text = str(row['distance'])
        if len(grain_shapes) > 0:
            grain_primary = ET.SubElement(layer, f'{_ns_caaml}:grainFormPrimary')
            grain_primary.text = grain_shapes[idx]
        grain_size = ET.SubElement(layer, f'{_ns_caaml}:grainSize')
        grain_size.set('uom', 'mm')
        grain_components = ET.SubElement(grain_size, f'{_ns_caaml}:Components')
        grain_sz_avg = ET.SubElement(grain_components, f'{_ns_caaml}:avg')
        grain_sz_avg.text = "1"
        grain_hardness = ET.SubElement(layer, f'{_ns_caaml}:hardness')
        grain_hardness.set('uom', '')
        grain_hardness.text = hand_hardness(row['force_median'])

    # Density profile:
    dens_prof = ET.SubElement(snow_prof_meas, f'{_ns_caaml}:densityProfile')
    dens_meta = ET.SubElement(dens_prof, f'{_ns_caaml}:densityMetaData')
    dens_meth = ET.SubElement(dens_meta, f'{_ns_caaml}:methodOfMeas')
    dens_meth.text = "other"

    for idx, row in derivatives.iterrows():
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
    for idx, row in derivatives.iterrows():
        tuple_list = tuple_list + str(row['distance']) + "," + str(row[f'{parameterization}_ssa']) + " "
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
    for idx, row in samples.iterrows():
        tuple_list = tuple_list + str(row['distance']) + "," + str(row['force']) + " "
    hard_tuple.text = tuple_list

## The following is an alternative method of specifying SMP data in CAAML which works
## analogous to the stratigraphy profile, but which niViz can't read.
#        hard_prof = ET.SubElement(snow_prof_meas, f'{_ns_caaml}:hardnessProfile')
#        hard_meta = ET.SubElement(hard_prof, f'{_ns_caaml}:hardnessMetaData')
#        hard_meth = ET.SubElement(hard_meta, f'{_ns_caaml}:methodOfMeas')
#        hard_meth.text = "SnowMicroPen"
#        negative_counter = 0
#        for idx, row in samples.iterrows():
#            layer = ET.SubElement(hard_prof, f'{_ns_caaml}:Layer')
#            depth_top = ET.SubElement(layer, f'{_ns_caaml}:depthTop')
#            depth_top.set('uom', 'cm')
#            depth_top.text = str(row['distance'])
#            hardness = ET.SubElement(layer, f'{_ns_caaml}:hardness')
#            hardness.set('uom', 'N')
#            hardness_val = row['force']
#            if hardness_val < 0:
#                hardness_val = 0
#                negative_counter = negative_counter + 1
#            hardness.text = str(hardness_val)
#        log.info(f'Set {negative_counter} negative values to zero.')

    tree = ET.ElementTree(root)
    ET.indent(tree, space="\t", level=0) # human-readable CAAML
    tree.write(outfile, encoding="UTF-8", xml_declaration=True)

def parse_grainshape(caaml_file: str):
    tree = ET.parse(caaml_file)
    root = tree.getroot()
    strat = root.find(f"{_ns_caaml}:snowProfileResultsOf", _ns)
    strat = strat.find(f"{_ns_caaml}:SnowProfileMeasurements", _ns)
    strat = strat.find(f"{_ns_caaml}:stratProfile", _ns)

    extract_list = ["depthTop", "thickness", "grainFormPrimary"]
    layer_list = []
    for layer in strat.findall(f"{_ns_caaml}:Layer", _ns):
        attr_list = []
        for attr in extract_list:
            val = layer.find(f"{_ns_caaml}:{attr}", _ns).text
            try:
                val = float(val)
            except:
                pass
            attr_list.append(val)
        layer_list.append(attr_list)

    return pd.DataFrame(layer_list, columns=extract_list)

if __name__ == "__main__":
    caaml_file = "../../data/rhossa/TraditionalProfiles/20151130/5wj-20151130_niViz6_81339.caaml"
    grain_samples = parse_grainshape(caaml_file)
    print(grain_samples)
