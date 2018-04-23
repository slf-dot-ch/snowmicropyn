from pandas import np as np


def chunkup(samples, window, overlap_factor):
    block_length = window * overlap_factor

    blocks = []
    center = samples.distance.iloc[0]
    while center < samples.distance.iloc[-1]:
        # Calculate where block begins and ends
        begin = center - block_length / 2.
        end = center + block_length / 2.

        # Filter for samples with a block and add it to the list of
        # blocks along with its center (the blocks center distance)
        within_block = np.logical_and(samples.distance >= begin, samples.distance < end)
        block_samples = samples[within_block]
        blocks.append((center, block_samples))

        center = center + window
    return blocks


DEFAULT_WINDOW = 2.5
DEFAULT_WINDOW_OVERLAP = 1.2


def agg_force_windows(samples, window, overlap, agg=np.median):
    """
    :param samples:
    :param window: Window size in Millimeter. Default to 2.5 mm.
    :param overlap: Overlap length in Millimeter. Default to 0.5 mm.
    :param agg: Aggregation function, default is ```np.median``.
    :return:
    """

    distance_arr = samples[:, 0]

    # Calculate average step size
    block_length = window * overlap
    block_center = distance_arr[0]

    blocks = []
    while block_center < distance_arr[-1]:
        block_begin = block_center - block_length / 2.
        block_end = block_center + block_length / 2.
        within_block = np.logical_and(distance_arr >= block_begin,
                                      distance_arr < block_end)
        d = block_center
        f = agg(samples[within_block][:, 1])
        blocks.append((d, f))
        block_center = block_center + window
    return np.array(blocks)
