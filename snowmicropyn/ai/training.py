from snowmicropyn import loewe2012, derivatives, Profile
from snowmicropyn.match import assimilate_grainshape
from snowmicropyn.parameterizations.proksch2015 import Proksch2015
import pandas as pd
import pathlib
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

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

def split_pro_data(data):
    XX = data.drop(['grain_shape'], axis=1)
    yy = data['grain_shape']
    return XX, yy

def make_pipeline():
    pipe = Pipeline([('scaler', StandardScaler()), ('svc', SVC(gamma=100))])
    return pipe

def score(data):
    XX, yy = split_pro_data(data)
    XX_train, XX_test, yy_train, yy_test = train_test_split(XX, yy)
    pipe = make_pipeline()
    pipe.fit(XX_train, yy_train)
    score = pipe.score(XX_test, yy_test)
    return score

def train(data):
    """Use full dataset for training"""
    XX, yy = split_pro_data(data)
    pipe = make_pipeline()
    pipe.fit(XX, yy)
    return pipe

if __name__ == '__main__':
    fdata = '../../data/rhossa'
    data = build_training_data(fdata)
    sc = score(data)
    print(f'Score: {sc}')

