# SnowMicroPyn Example: shotnoise_batch.py
#
# Batch processing of profiles loaded using a glob (wildcard chars).
# Each profile is loaded, its shot nose parameters are calculated and
# written to a csv file.

import glob

from snowmicropyn import Profile

match = '/Users/marcel/Dropbox/SMP/pnt_examples/*.pnt'

for f in glob.glob(match):
    print('Processing file ' + f)
    p = Profile.load(f)
    sn = p.model_shotnoise(save_to_file=True)
