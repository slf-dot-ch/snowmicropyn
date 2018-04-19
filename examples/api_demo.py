from snowmicropyn import Profile
import pandas as pd

pd.set_option('display.max_rows', 10)

# Load a profile
# Note: In case a correlating INI file is found, its content is loaded too
p = Profile.load('/Users/marcel/Dropbox/SMP/pnt_examples/S31M0067.pnt')

# Access some meta data of profile
print(p.name)
print(p.timestamp)
print(p.coordinates)
print(p.smp_serial)

# Export profile data
p.export_meta(include_pnt_header=False)
p.export_samples()

# Access measurements as pandas dataframe
samples = p.samples

print('--- samples ---')
print(samples)

# Access measurements as numpy array
array = p.samples.values

print('--- array ---')
print(array)

# Detect ground and surface.
# Those are convenience methods, you also can call
# snowmicropyn.analysis.detect_ground(p.samples) and save the marker
# yourself using p.set_marker('surface', value)
p.detect_surface()
p.detect_ground()

# Set some other markers. A marker must have a unique name. The
# names "surface" and "ground" are used to mark begin and end of
# the snowpack.
p.set_marker('slab_begin', p.surface)
p.set_marker('slab_end', p.surface + 200)
p.export_meta(include_pnt_header=True)

# Save, so markers are not lost
# This saves an ini file named same as the pnt file
p.save()

# Get samples within a specified range.
some_samples = p.samples_within_distance(begin=200,
                                         end=400,
                                         relativize=True)

print('--- some_samples ---')
print(some_samples)

# Get samples from surface to ground
snowpack = p.samples_within_snowpack(relativize=True)

print('--- snowpack ---')
print(snowpack)

# Run shot noise model, returns a pandas data frame.
# When parameter save_to_file is set to True, model output is written
# to a CSV file.
shotnoise = p.model_shotnoise(save_to_file=True)

print('--- shotnoise ---')
print(shotnoise)

ssa = p.model_ssa()

print('--- ssa ---')
print(ssa)

model = pd.concat([shotnoise, ssa], axis=1)
model.to_csv(p.default_filename(suffix='model'), index=False)

