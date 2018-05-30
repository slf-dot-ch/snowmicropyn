import glob

from snowmicropyn import Profile

match = 'profiles/*.pnt'

for f in glob.glob(match):
    print('Processing file ' + f)
    p = Profile.load(f)
    p.export_samples()
    p.export_meta(include_pnt_header=True)
    p.export_derivatives()
