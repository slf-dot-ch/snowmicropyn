from snowmicropyn import loewe2012, derivatives, Profile
from snowmicropyn.match import assimilate_grainshape
from snowmicropyn.parameterizations.proksch2015 import Proksch2015
import pandas as pd
import pathlib

def build_training_data(data_folder: str):
    proksch = Proksch2015() # Fetch Löwe's moving window properties from here
    profiles = pathlib.Path(data_folder).rglob('*.pnt')
    data = pd.DataFrame()
    for file in profiles:
        pnt = str(file.resolve())
        caaml = pnt[:-3] + 'caaml'

        pro = Profile.load(pnt)
        derivs = loewe2012.calc(pro._samples, proksch.window_size, proksch.overlap)
        matched = assimilate_grainshape(derivs, caaml)
        data = pd.concat([data, matched])
    return data

if __name__ == '__main__':
    fdata = '../../data/rhossa'
    data = build_training_data(fdata)
    print(data)


