import os
import random
import warnings
from typing import List

import torch
from django.core.management import BaseCommand

from stop_problem.ml_src.data_preperation import *
from stop_problem.ml_src.model_utils import prepare_data_from_json, TrainingStopProblemDataset, train, test
from stop_problem.ml_src.stop_problem_dnn import StopProblemDNN


def Command():
    return TrainValidateAndSaveDnnModuleCommand()


class TrainValidateAndSaveDnnModuleCommand(BaseCommand):
    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '-d', '--data-files',
            nargs='+',
            type=str,
            action='extend',
            required=True,
            help='full path to data files for training and validation (.json)'
        )
        parser.add_argument(
            '--validation-ratio',
            type=float,
            default=0.2,
            help="Ratio of data taken for validation (valid only if 0<validation_ratio<=0.4")
        parser.add_argument(
            '--lines-to-predict',
            type=int,
            default=3,
            help="Number of lines DNN should predict (valid only if 1<=lines_to_predict<=5)")
        parser.add_argument(
            '--acceptable-validation-accuracy',
            type=float,
            default=35,
            help="Save model only if validation accuracy surpasses acceptable_validation_accuracy")
        parser.add_argument(
            '--quiet',
            action='store_false',
            dest='verbose',
            default=True,
            help="Don't print progress information")

    def handle(self, data_files: List[str], validation_ratio: float, lines_to_predict: int, acceptable_validation_accuracy: float,
               verbose: bool, *args, **options):
        warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)
        if not verbose:
            from stop_problem.ml_src import model_utils
            model_utils.VERBOSE = False
        if not 1 <= lines_to_predict <= 5:
            lines_to_predict = 3
        organized_data = []
        for data_file in data_files:
            organized_data.extend(prepare_data_from_json(data_file, lines_to_predict))
        if len(data_files)>1:
            random.seed(2)
            random.shuffle(organized_data)
        if not 0 < validation_ratio <= 0.4:
            validation_ratio = 0.2
        train_size = int(len(organized_data) * (1 - validation_ratio))
        train_set = TrainingStopProblemDataset(np.array(organized_data[0:train_size]))
        validation_set = TrainingStopProblemDataset(np.array(organized_data[train_size:len(organized_data)]))
        model = StopProblemDNN(lines_to_predict)
        train_accuracy, train_loss = train(model, train_set)
        test_accuracy, test_loss = test(model, validation_set)
        if verbose:
            print(f'Module reached {test_accuracy}% accuracy on test set')
        if test_accuracy >= acceptable_validation_accuracy:
            model_path = os.path.join('saved_models', f'model_{train_accuracy}-{test_accuracy}.pt')
            torch.save(model, model_path)
            if verbose:
                print(f'Module saved to {os.path.dirname(model_path)}')
