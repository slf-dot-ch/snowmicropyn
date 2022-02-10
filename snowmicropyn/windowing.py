import numpy as np

def chunkup(samples, window, overlap):
    """Combine data into chunks.

    :param samples: SMP samples
    :param window: size of moving window in mm
    :param overlap: overlap factor in percent
    """
    if 0 < overlap >= 100:
        raise ValueError('overlap value {} invalid, must be a value between 0 and 100 [%]'.format(overlap))

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
