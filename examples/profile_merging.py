import glob
from snowmicropyn import Profile
from snowmicropyn.tools import merge_profiles


# Load profiles to merge
profiles = []
match = '/Users/marcel/Dropbox/SMP/pnt_examples/*.pnt'
for f in glob.glob(match):
    profiles.append(Profile.load(f))

# Merge the profiles
merged_profile = merge_profiles(profiles)