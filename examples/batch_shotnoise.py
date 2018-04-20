import glob

from snowmicropyn import Profile

# Use a blob to get all a pnt files in directory
match = './some_directory/*.pnt'

for f in glob.glob(match):
    print('Processing file ' + f)
    p = Profile.load(f)
    sn = p.model_shotnoise(save_to_file=True)
