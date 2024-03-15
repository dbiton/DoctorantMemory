import argparse
import subprocess
import os

if os.name == 'nt':
    drcachesim_path = "DrMemory-Windows-2.6.0/bin/drmemory -t drcachesim"
else:
    drcachesim_path = "DrMemory-Linux-2.6.0/dynamorio/bin64/drrun -t drcachesim"

default_logs_folder = "logs"


def invoke_drcachesim(args: list):
    print(subprocess.check_output([drcachesim_path] + args))


def generate(app_path: str, log_path, app_args: list):
    #invoke_drcachesim(["-offline", "--", app_path] + app_args)
    invoke_drcachesim(["--", app_path] + app_args)


def parse(filepath: str):
    invoke_drcachesim()


def create_parser():
    parser = argparse.ArgumentParser(
        prog="DoctorantMemory",
        description="DrMemory wrapper"
    )
    parser.add_argument(
        "-operation",
        help="type of operation, can be parse or generate.",
    )
    parser.add_argument(
        "-app_path",
        help="relative or absolute to app, which would be instrumented when using generate.",
        required=False
    )
    parser.add_argument(
        "-log_path",
        default=default_logs_folder,
        help="relative or absolute to log, which would be parsed or written to when generating.",
    )
    parser.add_argument(
        "-app_args",
        nargs='*',
        default=[],
        help="arguments passed to your app when using generate.",
        required=False
    )
    return parser


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()
    if args.operation == "parse":
        parse(args.log_path)
    elif args.operation == "generate":
        generate(args.app_path, args.log_path, args.app_args)
    else:
        print(f'invalid operation "{args.operation}"')