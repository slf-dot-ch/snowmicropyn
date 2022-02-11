"""Showcase for how to programmatically use different
parameterizations."""

import os
import snowmicropyn as smp

EX_PATH = '../examples/profiles/S37M0876'

pro = smp.Profile.load('../examples/profiles/S37M0876.pnt')
# Output with default Proksch 2015 parameterization:
pro.export_derivatives()
os.rename(EX_PATH + '_derivatives.csv', EX_PATH + '_derivatives_P2015.csv')

# Switch to Calonne/Richter parameterization:
pro.export_derivatives(parameterization='CR2020')
os.rename(EX_PATH + '_derivatives.csv', EX_PATH + '_derivatives_CR2020.csv')

# Now with King 2020b, but as an experiment we change
# a few properties before calculation, namely the size of the
# moving window and the overlap factor:
smp.params['K2020b'].window_size = 2.5
smp.params['K2020b'].overlap = 70
pro.export_derivatives(parameterization='K2020b')
os.rename(EX_PATH + '_derivatives.csv', EX_PATH + '_derivatives_K2020x.csv')
