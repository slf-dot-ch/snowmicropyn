import numpy as np

def chunkup(samples, window, overlap):
    """Combine data into chunks.

    :param samples: SMP samples
    :param window: size of moving window in mm
    :param overlap: overlap factor in percent
    """
    if not 0 <= overlap < 100:
        raise ValueError('overlap value {} invalid, must be a value >= 0 and < 100 [%]'.format(overlap))

    first = samples.distance.iloc[0] if not samples.empty else 0
    last = samples.distance.iloc[-1] if not samples.empty else 0

    step = window - (window * overlap / 100)
    center = first
    chunks = []
    while center < last:
        # Calculate where block begins and ends
        begin = center - window / 2.
        end = center + window / 2.

        # Filter for samples with a block and add it to the list of
        # blocks along with its center (the blocks center distance)
        within = np.logical_and(samples.distance >= begin, samples.distance < end)
        chunk_samples = samples[within]
        chunks.append((center, chunk_samples))

        center = center + step
    return chunks


def chunkup_numpy(distance, force, window, overlap):
    """Fast numpy-only windowing, returning index ranges.

    :param distance: 1-D numpy array of distance values (must be sorted).
    :param force: 1-D numpy array of force values.
    :param window: size of moving window in mm.
    :param overlap: overlap factor in percent.
    :return: list of (center, start_idx, end_idx) tuples.  Use
             ``force[start_idx:end_idx]`` to get the chunk.
    """
    if not 0 <= overlap < 100:
        raise ValueError('overlap value {} invalid, must be a value >= 0 and < 100 [%]'.format(overlap))

    n = len(distance)
    if n == 0:
        return []

    first = distance[0]
    last = distance[-1]
    step = window - (window * overlap / 100.)

    # Vectorised: compute all centers and their index bounds in bulk.
    centers = np.arange(first, last, step)
    begins = centers - window / 2.
    ends = centers + window / 2.
    i0s = np.searchsorted(distance, begins, side='left')
    i1s = np.searchsorted(distance, ends, side='left')
    valid = i0s < i1s
    return list(zip(centers[valid], i0s[valid], i1s[valid]))
