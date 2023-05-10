from pathlib import Path

from argparse import ArgumentParser

from .commands import split, translate
from .settings import AzureSettings, ProjectSettings
from .utils import function_utils
from .utils.log import Log


def main():
    Log.init()

    commands = [
        translate,
        split,
    ]
    command_map = {Path(command.__name__).suffix[1:]: command for command in commands}

    parser = ArgumentParser(prog="srt_translator")
    subparsers = parser.add_subparsers(dest="subcommand")

    for name, command in command_map.items():
        description = getattr(command.Command, "description", "")
        subparser = subparsers.add_parser(name, description=description, help=description)
        command.Inputs.add_arguments(subparser)

    args = parser.parse_args()

    chosen_command = command_map[args.subcommand]

    inputs = chosen_command.Inputs(**args.__dict__)
    project_settings = ProjectSettings()
    azure_settings = AzureSettings(_env_file=f"{project_settings.root_dir}/.env")

    function_utils.forward_partial_args(chosen_command.Command().start)(
        inputs=inputs,
        project_settings=project_settings,
        azure_settings=azure_settings,
    )


if __name__ == "__main__":
    main()
