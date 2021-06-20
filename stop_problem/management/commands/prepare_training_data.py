from django.core.management import BaseCommand

from stop_problem.ml_src.model_utils import main


def Command():
    return PrepareTrainingData()


class PrepareTrainingData(BaseCommand):
    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)

    def handle(self, *args, **options):
        main()
