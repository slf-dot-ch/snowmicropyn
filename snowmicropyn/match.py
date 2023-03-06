from snowmicropyn.serialize import caaml

def match_layers_strict(samples, shapes):
    """Align a SMP profile with a manual one by comparing penetration depth
    with measured top of layer.
    """
    shape_list = []
    data = samples
    idx = 0
    for ii in range(len(samples.distance)):
        if samples.distance[ii] > shapes.depthTop[idx] + shapes.thickness[idx]:
            if idx < len(shapes.depthTop) - 1:
                idx = idx + 1
        shape_list.append(shapes.grainFormPrimary[idx])

    data["grain_shape"] = shape_list
    return data

def match_layers(samples, shapes, method="strict"):
    if method == "strict":
        data = match_layers_strict(samples, shapes)
    else:
        raise ValueError(f'Layer matching method "{method}" is not available.')
    return data

def assimilate_grainshape(samples, caaml_file):
    """Add grain shape taken from a manual snow profile to the SMP dataset"""
    grain_shapes = caaml.parse_grainshape(caaml_file)
    data = match_layers(samples, grain_shapes)
    return data
