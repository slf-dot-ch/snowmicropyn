import pandas as pd
from snowmicropyn.profile import Profile

pd.set_option("display.max_rows", 12)

p = Profile.load('/Users/marcel/Dropbox/SMP/pnt_examples/S31M0067.pnt')

df = pd.DataFrame(p.samples, columns=('distance', 'force'))

print(df.distance)
print(df.force)

df.to_csv('file.csv', index=False, float_format='%.3f')

