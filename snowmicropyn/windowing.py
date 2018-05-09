from pandas import np as np

DEFAULT_WINDOW = 2.5
DEFAULT_WINDOW_OVERLAP = 1.2


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


def iterwindows(samples, window_length, overlap_factor):
    block_length = window_length * float(overlap_factor)
    half_block = block_length / 2
    center = samples.distance.iloc[0]
    while center < samples.distance.iloc[-1]:
        begin = center - half_block
        end = center + half_block
        within = np.logical_and(samples.distance >= begin, samples.distance < end)
        yield samples[within]
        center += window_length
