"""This is a showcase program for snowmicropyn's machine learning API."""
from snowmicropyn import loewe2012, derivatives, Profile
from snowmicropyn.ai.grain_classifier import grain_classifier
from snowmicropyn.parameterizations.proksch2015 import Proksch2015
import os
from random import randrange

# First we need some training data. For this the program will search a
# given folder for .pnt and .caaml files that have the same name and combine
# them to assimilate grain shapes from the CAAML to the SMP profile.
# A helper script to get you started with a subset of the RHOSSA dataset
# is provided in /tools/download_rhossa.py:
#os.system('cd ../tools && python3 download_rhossa.py')

# Next we must build a dictionary with export settings. The GUI is a good
# place to check to see what's available.
export_settings = {}

# Training. To fit the model we must tell where the training data is located,
# as well as which kind of dataest we have:
export_settings['training_data_folder'] = '../data/rhossa'
export_settings['training_data_method'] = 'exact'
#export_settings['training_data_folder'] = '../data/rhossa_markers/'
#export_settings['training_data_method'] = 'markers'

# And we must choose which algorithms to use for the learning process:
export_settings['scaler'] = 'standard' # pre-processing: data scaling
export_settings['model'] = 'svc' # use a Support Vector Machine
export_settings['model_svc_gamma'] = 100 # parameter specific to SVM model

# Initialize a grain shape classifier, in this case with the location
# of training data in our settings:
classifier = grain_classifier(export_settings)

# Now we want to save this trained model for later use.
# We could set some user settings to do this automatically after training
# (like the GUI does), but of course we can also just call the methods for it:
model_file = './trained_model.dat' # output file name
classifier.save(model_file)

# Validation. Reading the 'score' property will trigger re-using the training
# data but setting some of it aside to check the prediction against:
score = classifier.score(percent=True)
print(f'Score: {score} % of validation data was classified correctly by a Support Vector Machine.')

# Prediction. We want to use the derived values where some Physics are
# contained as additional information. Also, of course we must use data in the
# same shape as was used for training. So we load the profile and calculate
# the derivatives after which we can predict through the classfier object:
pro = Profile.load('./profiles/S37M0876.pnt')
proksch = Proksch2015()
derivs = loewe2012.calc(pro._samples, proksch.window_size, proksch.overlap)
grain_shapes = classifier.predict(derivs)

# If we want to use a pre-trained model we need to set the following flags:
export_settings_two = {} # just to show that we don't need model settings
export_settings_two['use_pretrained_model'] = True
export_settings_two['trained_input_path'] = './trained_model.dat'
classifier_two = grain_classifier(export_settings_two)
shapes_two = classifier_two.predict(derivs)
rand_shape = shapes_two[randrange(len(derivs))]
print(f'Random classified grain shape from 2nd go: "{rand_shape}."')

# Let's try with a different machine learning model:
export_settings['model'] = 'multinomialnb'
export_settings['scaler'] = 'minmax'
export_settings['model_multinomialnb_alpha'] = 1
bayes_classifier = grain_classifier(export_settings)
score = bayes_classifier.score(percent=True)
print(f'Score: {score} % of validation data was classified correctly by a Naive Bayes classifier.')
