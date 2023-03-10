from snowmicropyn import loewe2012, derivatives, Profile
from snowmicropyn.match import assimilate_grainshape
from snowmicropyn.parameterizations.proksch2015 import Proksch2015
import pandas as pd
import pathlib
import pickle
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

class grain_classifier:

    # internal data:
    _grain_id = 'grain_shape' # name of grain shape column in samles
    _set = {} # user export settings
    _training_data = pd.DataFrame()
    _index_codes = None
    _index_labels = None
    _init_from_pickle = False # flag for how the class was initialized / which info we have

    # pipeline objects:
    _scaler = None
    _model = None
    _pipe = None

    # properties:
    _score = None # cache for the score calculation

    def __init__(self, user_settings: dict, model_file=None):
        self._set = user_settings
        if model_file:
            self.load(model_file)
            self._init_from_pickle = True # no training data must be needed in this mode
        else:
            self._training_data = self.build_training_data(self._set['training_folder'])
            self._index_codes, self._index_labels = pd.factorize(self._training_data.grain_shape)
            self.make_pipeline()
            self.train()

    def _numeric_data(self, numeric=True):
        """Convert grain shape column between string and index indentifiers.

        Some models require the prediction observable to be numeric. This function takes
        our string input (grain shapes like 'RG' for rounded grains) and assigns unique
        indices and vice versa (if necessary).
        :param numeric: After this function call, should 'grain_size' be numeric (default: True)?
        """
        if numeric:
            if self._training_data[self._grain_id].dtype == 'int64':
                return # nothing to do
            else:
                self._training_data[self._grain_id] = self._index_codes
        else: # make sure it's a string
            if self._training_data[self._grain_id].dtype == 'object':
                return # already done
            else:
                self._training_data[self._grain_id] = self._index_labels[self._training_data[self._grain_id]]

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
        XX = self._training_data.drop([self._grain_id], axis=1)
        yy = self._training_data[self._grain_id]
        return XX, yy

    def _make_scaler(self):
        if self._set['scaler'] == 'standard':
            self._scaler = ('scaler', StandardScaler())
        elif self._set['scaler'] == 'minmax':
            self._scaler = ('scaler', MinMaxScaler())
        else:
            raise ValueError('Grain classification: the selected scaler is not available.')

    def _make_model(self):
        if self._set['model'] == 'svc':
            try:
                svc_gamma = self._set['model_svc_gamma']
            except KeyError:
                svc_gamma = 'auto'
            self._model = ('svc', SVC(gamma=svc_gamma))
        elif self._set['model'] == 'lr':
            self._numeric_data(True)
            self._model = ('LR', LinearRegression())
        elif self._set['model'] == 'gaussiannb':
            self._model = ('gaussiannb', GaussianNB())
        elif self._set['model'] == 'multinomialnb':
            try:
                multi_alpha = self._set['model_multinomialnb_alpha']
            except KeyError:
                multi_alpha = 1 # default in sklearn
            self._model = ('multinomialnb', MultinomialNB(alpha=multi_alpha))
        else:
            raise ValueError('Grain classification: the selected model is not available.')

    def make_pipeline(self, remake=False):
        if not remake and self._pipe:
            return
        self._make_scaler()
        self._make_model()
        self._pipe = Pipeline([self._scaler, self._model])

    def save(self, model_file):
        """Save current state of pipeline (trained or not) to file system."""
        pickle.dump(self._pipe, open(model_file, 'wb'))

    def load(self, model_file):
        self._pipe = pickle.load(open(model_file, 'rb'))

    @property
    def ready(self):
        return self._pipe is not None

    @property
    def score(self, recalc=False):
        if self._init_from_pickle:
            raise ValueError('Grain classification: The model can not score against test data since it was initialized as pre-trained.')
        if not self._score or recalc:
            XX, yy = self.split_pro_data()
            XX_train, XX_test, yy_train, yy_test = train_test_split(XX, yy)
            self._pipe.fit(XX_train, yy_train)
            self._score = self._pipe.score(XX_test, yy_test)
        return self._score

    def train(self):
        """Use full dataset for training"""
        XX, yy = self.split_pro_data()
        self._pipe.fit(XX, yy)

    def predict(self, samples):
        yy = self._pipe.predict(samples)
        return yy

if __name__ == '__main__':
    # training
    _export_settings = {}
    _export_settings['training_folder'] = '../../data/rhossa'
    _export_settings['scaler'] = 'standard'
    _export_settings['model'] = 'svc'
    _export_settings['svc_gamma'] = 100
    classifier = grain_classifier(_export_settings)
    model_file = './trained_model.dat'
    classifier.save(model_file)
    print(f'Score: {classifier.score}')

    # prediction
    pro = Profile.load('../../examples/profiles/S37M0876.pnt')
    proksch = Proksch2015()
    derivs = loewe2012.calc(pro._samples, proksch.window_size, proksch.overlap)
    grain_shapes = classifier.predict(derivs)

    # use saved model state
    classifier_two = grain_classifier(_export_settings, model_file)
    shapes_two = classifier_two.predict(derivs)
