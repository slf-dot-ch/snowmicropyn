# Unit test for low-level derivatives calculation

import pandas as pd
import snowmicropyn as smp

pro = smp.Profile.load('../examples/profiles/S37M0876.pnt')
p2015 = smp.proksch2015.calc(pro.samples)
p2015 = smp.params['P2015'].calc(pro.samples)
cr2020 = smp.params['CR2020'].calc(pro.samples)

fp_ref = './P2015_ref.csv'
fcr_ref = './CR2020_ref.csv'

write_refs = False
if write_refs:
    fmt = '%.6f' # must match atol below
    p2015.to_csv(fp_ref, header=True, index=False, float_format=fmt)
    cr2020.to_csv(fcr_ref, header=True, index=False, float_format=fmt)
    quit()

p2015_ref = pd.read_csv(fp_ref)
cr2020_ref = pd.read_csv(fcr_ref)

pd.testing.assert_frame_equal(p2015, p2015_ref, atol=1e-6)
pd.testing.assert_frame_equal(cr2020, cr2020_ref, atol=1e-6)

