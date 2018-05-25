from pandas import np as np

DEFAULT_WINDOW = 2.5
DEFAULT_WINDOW_OVERLAP = 50


def chunkup(samples, window, overlap):
    if 0 < overlap >= 100:
        raise ValueError('overlap value {} invalid, must be a value between 0 and 100 [%]'.format(overlap))

    step = window - (window * overlap / 100)
    center = samples.distance.iloc[0]
    chunks = []
    while center < samples.distance.iloc[-1]:
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
