"""This module performs layer matching between profiles."""
from snowmicropyn.serialize import caaml

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

def match_layers_rhossa(samples, pro):
    """Extract the grain shapes from manually set markers on the profile.

    param samples: Pandas dataframe with measured SMP forces.
    param pro: snowmicropyn Profile to parse
    returns: Pandas dataframe with a new column containing the grain shapes.
    """
    print(pro.markers)
    data = samples
    return data

def assimilate_grainshape(samples, pro, method: str):
    """Add grain shape taken from an external (manual) snow profile to the SMP dataset.

    param samples: Recorded SMP samples as pandas dataframe.
    param caaml_file: Path to corresponding (manual) CAAML snow profile containing
    grain shapes.
    returns: SMP samples with assimlated grain shapes.
    """
    if method == 'exact':
        caaml = pro._pnt_file.resolve()[:-3] + 'caaml'
        grain_shapes = caaml.parse_grainshape(caaml_file)
        data = match_layers_exact(samples, grain_shapes)
    elif method.upper() == 'RHOSSA':
        data = match_layers_rhossa(samples, pro)
    else:
        raise ValueError(f'Layer matching method "{method}" is not available.')
    return data
