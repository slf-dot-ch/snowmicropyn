from snowmicropyn import loewe2012, derivatives, Profile
from snowmicropyn.match import assimilate_grainshape
from snowmicropyn.parameterizations.proksch2015 import Proksch2015
import pandas as pd
import pathlib
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


class grain_classifier:

    _training_folder = None
    _set = {} # user export settings
    _data = pd.DataFrame()
    _score = None
    _pipe = None

    def __init__(self, training_folder: str):
        self._training_folder = training_folder
        self._data = self.build_training_data(self._training_folder)

    @staticmethod
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

    def split_pro_data(self):
        XX = self._data.drop(['grain_shape'], axis=1)
        yy = self._data['grain_shape']
        return XX, yy

    def make_pipeline(self, remake=False):
        if not self._pipe or remake:
            pipe_scaler = ('scaler', StandardScaler())
            pipe_svc = ('svc', SVC(gamma=100))
            self._pipe = Pipeline([pipe_scaler, pipe_svc])

    @property
    def score(self, recalc=False):
        if not self._score or recalc:
            XX, yy = self.split_pro_data()
            XX_train, XX_test, yy_train, yy_test = train_test_split(XX, yy)
            self.make_pipeline()
            self._pipe.fit(XX_train, yy_train)
            self._score = self._pipe.score(XX_test, yy_test)
        return self._score

    def train(self, data):
        """Use full dataset for training"""
        XX, yy = self._split_pro_data()
        self.make_pipeline()
        self._pipe.fit(XX, yy)

if __name__ == '__main__':
    fdata = '../../data/rhossa'
    classifier = grain_classifier(fdata)
    sc = classifier.score
    print(f'Score: {sc}')

