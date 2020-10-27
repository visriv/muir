""" Find the best-performing network from parameter search trials, train it
again, and write out the model parameters """

import glob
import os
import sys
sys.path.append('..')
import utils
import cPickle as pickle
import train_network
import numpy as np

BASE_DATA_DIRECTORY = 'data/'
RESULTS_PATH = 'parameter_trials'
MODEL_PATH = 'best_model'


def get_best_trial(results_path):
    """ Get the hyperparameter setting and epoch corresponding to the lowest
    objective value.

    Parameters
    ----------
    results_path : str
        Path to trial result .pkl files

    Returns
    -------
    best_params : dict
        Hyperparameter dictionary for the lowest-objective epoch
    best_epoch : dict
        Epoch result for the lowest-objective epoch across all trials
    """
    # Load in all trial results pickle files
    trials = []
    for trial_file in glob.glob(os.path.join(results_path, '*.pkl')):
        with open(trial_file) as f:
            trial = pickle.load(f)
            # Ignore failed trials
            if not np.isnan(trial['best_epoch']['validate_objective']):
                trials.append(trial)

    # Find the trial with the smallest validate objective
    trials.sort(key=lambda x: x['best_epoch']['validate_objective'])
    return trials[0]['params'], trials[0]['best_epoch']


if __name__ == '__main__':

    train_list = list(glob.glob(os.path.join(
        BASE_DATA_DIRECTORY, 'train', '*.npz')))
    valid_list = list(glob.glob(os.path.join(
        BASE_DATA_DIRECTORY, 'valid', '*.npz')))
    # Load in the data
    (X_train, Y_train, X_validate, Y_validate) = utils.load_data(
        train_list, valid_list)
    # Convert to data dict
    # TODO: Do this in utils
    data = {}
    data['X_train'] = X_train
    data['X_validate'] = X_validate
    data['Y_train'] = Y_train
    data['Y_validate'] = Y_validate

    best_params, best_epoch = get_best_trial(RESULTS_PATH)
    print best_params
    print 'Expected objective: {}'.format(best_epoch['validate_objective'])

    # Train a network with this data
    best_epoch, X_params, Y_params = train_network.objective(best_params, data)
    # Write out the network params
    if not os.path.exists(MODEL_PATH):
        os.makedirs(MODEL_PATH)
    with open(os.path.join(MODEL_PATH, 'X_params.pkl'), 'wb') as f:
        pickle.dump(X_params, f)
    with open(os.path.join(MODEL_PATH, 'Y_params.pkl'), 'wb') as f:
        pickle.dump(Y_params, f)
