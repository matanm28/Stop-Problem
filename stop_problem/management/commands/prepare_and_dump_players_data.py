from django.core.management import BaseCommand

from stop_problem.ml_src.data_preperation import *


def Command():
    return PrepareAndDumpPlayersDataCommand()


class PrepareAndDumpPlayersDataCommand(BaseCommand):
    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '-o', '--outfile',
            default='datasets/site_data.json',
            help='Full path to destination file (.json)'
        )
        parser.add_argument(
            '--no-overwrite',
            action='store_false',
            dest='force',
            default=True,
            help="Don't overwrite destination file if it already exists")

    def handle(self, outfile: str, force: bool, *args, **options):
        import os
        players_dict = get_data_for_all_players()
        json_ready_players_dict = {key: numpy_arr.tolist() for key, numpy_arr in players_dict.items()}
        folder_name = os.path.dirname(outfile)
        file_path = outfile if folder_name else os.path.join(os.getcwd(), outfile)
        if force or not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                import json
                json.dump(json_ready_players_dict, f)
            print(f'Dumped {len(json_ready_players_dict)} players data to {os.path.abspath(file_path)}.')
