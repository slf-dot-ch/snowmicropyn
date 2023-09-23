"""This module performs layer matching between profiles."""
from snowmicropyn.serialize import caaml
import re

def match_layers_exact(samples, shapes):
    """Align a SMP profile with a manual one by comparing penetration depth
    with measured top of layer.

    param samples: Pandas dataframe with measured SMP forces.
    param shapes: List of grain shapes (one entry per SMP data row).
    returns: Pandas dataframe with a new column containing the grain shapes.
    """
    shape_list = []
    data = samples
    idx = 0
    for ii in range(len(samples.distance)):
        if samples.distance[ii] > shapes.depthTop[idx] + shapes.thickness[idx]:
            if idx < len(shapes.depthTop) - 1:
                idx = idx + 1
        shape_list.append(shapes.grainFormPrimary[idx])

    data['grain_shape'] = shape_list
    return data

def match_layers_markers(samples, pro):
    """Extract the grain shapes from manually set markers on the profile.

    param samples: Pandas dataframe with measured SMP forces.
    param pro: snowmicropyn Profile to parse
    returns: Pandas dataframe with a new column containing the grain shapes.
    """
    data = samples
    data['grain_shape'] = 'NOt_labelled' # n/a value of dataset
    # sort by sample distance and convert to sorted container for index access:
    markers = list(sorted(pro.markers.items()))
    for ii in range(len(markers)):
        label = markers[ii][0]
        nr = re.search(r'(.*)(\d+)$', label)
        if nr is not None: # we consider any marker that ends with a number to be a layer (e. g. "rg1")
            grain_type = nr.group(1) # marker name without number
            # Markers are read through the config parser as lower case, so in accordance to
            # the ICSSG we must capitalize the main form (first 2 letters):
            grain_type = grain_type[0:2].upper() + grain_type[2:]
            pos = markers[ii][1]
            if (ii == len(markers) - 1):
                nextpos = float(data.tail(1).distance)
            else:
                nextpos = markers[ii + 1][1]
            data.loc[(data.distance >= pos) & (data.distance < nextpos), 'grain_shape'] = grain_type

    data = data[data.grain_shape != 'NOt_labelled'] # remove unclassified rows
    return data

def assimilate_grainshape(samples, pro, method: str):
    """Add grain shape taken from an external (manual) snow profile to the SMP dataset.

    param samples: Recorded SMP samples as pandas dataframe.
    param caaml_file: Path to corresponding (manual) CAAML snow profile containing
    grain shapes.
    returns: SMP samples with assimlated grain shapes.
    """
    if method == 'exact':
        caaml_file = str(pro._pnt_file.resolve())[:-3] + 'caaml'
        grain_shapes = caaml.parse_grainshape(caaml_file)
        data = match_layers_exact(samples, grain_shapes)
    elif method == 'markers':
        data = match_layers_markers(samples, pro)
    else:
        raise ValueError(f'Layer matching method "{method}" is not available.')
    return data
