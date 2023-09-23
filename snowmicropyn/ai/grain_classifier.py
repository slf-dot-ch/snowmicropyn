"""This module implements grain shape classification based on machine learning algorithms.
It takes training data in the form of SMP profiles together with manual snow profiles
to combine them to a full measurement set containing the measured forces and associated
snow types. It can then apply what it has learned to standalone SMP profiles to estimate
the grain shapes at each data point.
"""
from snowmicropyn import loewe2012, derivatives, Profile
from snowmicropyn.match import assimilate_grainshape
from snowmicropyn.parameterizations.proksch2015 import Proksch2015
from snowmicropyn.serialize.caaml import preprocess_lowlevel
import logging
import pandas as pd
from pandas.api.types import is_string_dtype
from pandas.api.types import is_numeric_dtype
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

log = logging.getLogger('snowmicropyn')

class grain_classifier:
    """This object offers an interface to a machine learning workflow. It can either be initialized
    from a saved trained model state, in which case the pre-trained model will be applied to a
    SMP profile. Or it can be initialized with a path to training data, in which case the fitting
    will be done on the fly.
    It is controlled by a dictionary of user settings that is either filled by the GUI or which
    must be supplied programmatically.
    """
    # internal data:
    _grain_id = 'grain_shape' # name of grain shape column in samples
    _set = {} # user export settings
    _training_data = pd.DataFrame()
    _numeric_target = False # convert grain shape string representations to indices
    _index_codes = None # for when numeric indices must be used for the grain shape
    _index_labels = None
    _init_from_pickle = False # flag for how the class was initialized / which info we have

    # pipeline objects:
    _scaler = None
    _model = None
    _pipe = None

    # properties:
    _score = None # cache for the score calculation

    def __init__(self, user_settings: dict):
        """Class constructor. Depending on the user settings this will either load a pre-trained
        model or trigger model training on a training data folder. Have a look at the machine
        learning example in /examples/machine_learning.py to see which settings are needed/available.
        After this step the class can perform grain shape prediction and scoring.

        param user_settings: Dictionary with module settings as key/value pairs.
        """
        self._set = user_settings
        if self._set.get('use_pretrained_model', False): # load pickled Pipeline object
            input_file = pathlib.Path(self._set['trained_input_path'])
            self.load(input_file.resolve())
            self._init_from_pickle = True # no training data must be needed in this mode
        else: # fit model on the fly
            if not 'training_data_folder' in self._set:
                raise ValueError('Grain classification: To fit a model you must supply a training data location via the "training_data_folder" key.')
            # Combine SMP measurements with external information about the involved grain shapes:
            self._training_data = self.build_training_data(self._set['training_data_folder'], self._set['training_data_method'])
            self._training_data = preprocess_lowlevel(self._training_data, self._set)
            # Some models (like linear regression) expect numeric values for the parameter to estimate. Create a lookup:
            self._index_codes, self._index_labels = pd.factorize(self._training_data[self._grain_id])

            self.make_pipeline() # no fitting yet
            self.train() # now we fit
            if self._set.get('save_model', False) and self._set['trained_output_path']:
                self.save(self._set['trained_output_path'])

    def _numeric_data(self, column, numeric=True):
        """Convert grain shape column between string and index indentifiers.

        Some models require the prediction observable to be numeric. This function takes
        our string input (grain shapes like 'RG' for rounded grains) and assigns unique
        indices and vice versa (if necessary).

        :param numeric: After this function call, should 'grain_size' be numeric (default: True)?
        """
        if numeric:
            if not is_numeric_dtype(column.dtype):
                column = self._index_codes
        else: # make sure it's a string
            if not is_string_dtype(column.dtype):
                column = self._index_labels[[int(col) for col in column]]
        return column

    @staticmethod
    def build_training_data(data_folder: str, method: str):
        """Loads an SMP profile and an associated CAAML (manual) profile, calculates
        the derivatives and adds a column with the grain shape taken from the CAAML.

        param data_folder: Folder with a collection of matching SMP and CAAML profiles.
        param method: Format of training dataset / method of parsing. Can be one of the
        following:
          'exact': Finds the grain shape in a CAAML with the same base file name.
          'markers': Finds the grain shape from markers in the SMP profile.
        returns: Pandas dataframe with the grain shape added to the SMP data.
        """
        proksch = Proksch2015() # Fetch Löwe's moving window properties from here
        profiles = pathlib.Path(data_folder).rglob('*.pnt')
        data = pd.DataFrame()
        for file in profiles:
            pnt = str(file.resolve())
            pro = Profile.load(pnt)
            derivs = loewe2012.calc(pro._samples, proksch.window_size, proksch.overlap)
            matched = assimilate_grainshape(derivs, pro, method) # insert "grain_shape" column
            data = pd.concat([data, matched]) # put all training data in single container
        return data

    def split_pro_data(self):
        """Split a full dataset already containing the "grain_shape" column into X and y, i. e.
        into predictors (the dataset without "grain_shape") and target (the grain shapes).
        """
        XX = self._training_data.drop([self._grain_id], axis=1)
        yy = self._training_data[self._grain_id]
        if self._numeric_target:
            yy = self._numeric_data(yy)
        return XX, yy

    def _make_scaler(self):
        """Object factory for scaler of the machine learning model. This step of the pipeline will
        scale the measured/derived values to a range best suitable for model fitting.
        Currently available are 'standard' and 'minmax'.
        """
        if self._set['scaler'] == 'standard':
            self._scaler = ('scaler', StandardScaler())
        elif self._set['scaler'] == 'minmax':
            self._scaler = ('scaler', MinMaxScaler())
        else:
            raise ValueError(f"Grain classification: the selected scaler {self._set['scaler']} is not available.")

    def _make_model(self):
        """Object factory for the machine learning model. This part of the pipeline selects the
        algorithm to use for data fitting. Currently available are 'svc', 'lr', 'gaussiannb' and 'multinomialnb',
        which are set on class initialization via the export settings dictionary.
        Have a look at /examples/machine_learning.py for some tuning parameters you can supply.
        """
        if self._set['model'] == 'svc':
            try:
                svc_gamma = self._set['model_svc_gamma']
            except KeyError:
                svc_gamma = 'auto' # default
            self._model = ('svc', SVC(gamma=svc_gamma))
        elif self._set['model'] == 'lr':
            self._numeric_target = True
            self._model = ('LR', LinearRegression())
        elif self._set['model'] == 'gaussiannb':
            self._model = ('gaussiannb', GaussianNB())
        elif self._set['model'] == 'multinomialnb':
            try:
                multi_alpha = self._set['model_multinomialnb_alpha']
            except KeyError:
                multi_alpha = 1 # default in sklearn
            self._model = ('multinomialnb', MultinomialNB(alpha=multi_alpha, force_alpha=True))
        else:
            raise ValueError('Grain classification: the selected model is not available.')

    def make_pipeline(self, remake=False):
        """This function builds the final pipeline combining the objects we have gathered from their respective
        object factories, i. e. pre-processing and fitting modules.

        param remake: Boolean to force re-fitting the model if this was already done previously.
        """
        if not remake and self._pipe:
            return # we already did all the work
        self._make_scaler()
        self._make_model()
        self._pipe = Pipeline([self._scaler, self._model])
        log.info(f'Built pipeline: {self._pipe}')

    def save(self, model_file):
        """Save current state of pipeline (trained or not) to file system.

        param model_file: Output path for dumping the trained model.
        """
        log.info(f'Saving model state to "{model_file}"')
        pickle.dump(self._pipe, open(model_file, 'wb'))

    def load(self, model_file):
        """Load a previously trained model from the file system.

        param model_file: Path to an existing trained model.
        """
        log.info(f'Loading model state from "{model_file}"')
        self._pipe = pickle.load(open(model_file, 'rb'))

    @property
    def ready(self):
        """Check if a pipe has already been built, i. e. if the module is ready to predict."""
        return self._pipe is not None

    def score(self, percent=False, recalc=False):
        """Use the supplied training data not to fit the model but to perform a test score on the data.
        This function excludes part of the training data to afterwards check the prediction against this
        ground truth. The percentage of correct guesses is saved in the _score property of this class.

        param percent: Convert to percent and round for pretty printing (bool)?
        param recalc: Boolean to force recalculation of the score even if this was previously already done.
        """
        if self._init_from_pickle:
            raise ValueError('Grain classification: The model can not score against test data since it was initialized as pre-trained.')
        if not self._score or recalc:
            XX, yy = self.split_pro_data()
            XX_train, XX_test, yy_train, yy_test = train_test_split(XX, yy)
            self._pipe.fit(XX_train, yy_train)
            self._score = self._pipe.score(XX_test, yy_test)

        fscore = self._score
        if percent:
            fscore = round(self._score * 100)
        return fscore

    def train(self):
        """Fits the model. This function uses the full dataset for training and therefore does not provide
        a score value - use the .score property separately for this if desired."""
        XX, yy = self.split_pro_data()
        self._pipe.fit(XX, yy)

    def predict(self, samples):
        """Use the trained machine learning model to make a prediction about the grain shapes of snow
        layers based on their measured and derived microparameters.

        param samples: Pandas dataframe with SMP measurements. Usually this will be the derivatives
        and not the raw samples.
        """
        samples = preprocess_lowlevel(samples, self._set)
        yy = self._pipe.predict(samples)
        yy = self._numeric_data(yy, numeric=False) # convert back to string representation (if necessary)
        return yy

