import argparse
import subprocess
import os
from pathlib import Path

if os.name == 'nt':
    drrun_path = "DynamoRIO-Linux-10.0.0/bin/drmemory"
else:
    drrun_path = "DynamoRIO-Linux-10.0.0/bin64/drrun"


def invoke_drcachesim(args: list):
    print(subprocess.check_output([drrun_path, "-t", "drcachesim"] + args))


def generate(app_path: str, log_path: str, app_args: list):
    Path(log_path).mkdir(parents=True, exist_ok=True)
    invoke_drcachesim(["-offline", "-outdir", log_path, "--", app_path] + app_args)


def parse(log_path: str):
    invoke_drcachesim(["-indir", log_path])

def create_parser():
    parser = argparse.ArgumentParser(
        prog="DoctorantMemory",
        description="DrMemory wrapper"
    )
    parser.add_argument(
        "-operation",
        choices=["parse", "generate"],
        help="type of operation to perform."
    )
    parser.add_argument(
        "-app_path",
        help="relative or absolute to app, which would be instrumented when using generate.",
        required=False
    )
    parser.add_argument(
        "-log_path",
        default=".",
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