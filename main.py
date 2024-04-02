import argparse
import subprocess
import os
from pathlib import Path
from datetime import datetime, timezone

if os.name == 'nt':
    drrun_path = "DynamoRIO-Windows-10.0.0/bin64/drrun"
else:
    drrun_path = "DynamoRIO-Linux-10.0.0/bin64/drrun"


def timestamp():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def invoke_drcachesim(args: list, output_path=timestamp()):
    output_file = open(output_path, 'w')
    command = [drrun_path, "-t", "drcachesim"] + args
    subprocess.run(
        command,
        stdout=output_file,
        stderr=output_file
    )
    return output_path


def generate(app_path: str, trace_path: str, app_args: list):
    Path(trace_path).mkdir(parents=True, exist_ok=True)
    result_path = invoke_drcachesim(["-offline", "-outdir", trace_path, "--", app_path] + app_args)
    with open(result_path, 'r') as f:
        for line in f:
            print(line)


def parse(trace_path: str, sim_type: str):
    result_path = invoke_drcachesim(["-indir", trace_path]+sim_type.split())
    with open(result_path, 'r') as f:
        for line in f:
            print(line)

def parse_special(trace_path: str):
    result_path = invoke_drcachesim(["-indir", trace_path, "-simulator_type", "view"])
    min_timestamp = float('inf')
    max_timestamp = float('-inf')
    min_address = float('inf')
    max_address = float('-inf')
    with open(result_path, 'r') as f:
        header = [next(f) for i in range(3)]
        for line in f:
            tokens = line.split()
            if tokens[0] == 'View':
                break
            elif tokens[3] == "<marker:":
                if tokens[4] == "timestamp":
                    timestamp = int(tokens[5][:-1])
                    min_timestamp = min(timestamp, min_timestamp)
                    max_timestamp = max(timestamp, max_timestamp)
                continue
            elif tokens[3] in ["ifetch", "write", "read"]:
                address = int(tokens[7], 0)
                min_address = min(address, min_address)
                max_address = max(address, max_address)
    
    cur_timestamp = None
    with open(result_path, 'r') as f:
        header = [next(f) for i in range(3)]
        for line in f:
            tokens = line.split()
            if tokens[0] == 'View':
                break
            tid = tokens[2]
            record_details_header = tokens[3]
            if record_details_header == "ifetch":
                op = "I"  # instruction
            elif record_details_header == "write":
                op = "W"
            elif record_details_header == "read":
                op = "R"
            elif record_details_header == "<marker:":
                if tokens[4] == "timestamp":
                    cur_timestamp = int(tokens[5][:-1])
                continue
            else:
                continue  # fix here, check other possible options
            curr_address = int(tokens[7], 0)
            size = tokens[4]  # should check type after?
            assert (tokens[5] == "byte(s)")
            entry = [cur_timestamp, tid, curr_address, size, op]
            entry[0] = (entry[0] - min_timestamp) / 1000
            entry[2] = entry[2] - min_address
            output_line = ','.join([str(v) for v in entry])
            print(output_line)


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
    # this is more like analyze, output of parse should be the dude's special format thing
    parser.add_argument(
        "-parse_output",
        choices=["cache_simulator", "memory_accesses_human",
                 "memory_accesses", "cache_line_histogram"],
        default="cache_simulator",
        help="relative or absolute to app, which would be instrumented when using generate.",
        required=False
    )
    parser.add_argument(
        "-trace_path",
        default=".",
        help="relative or absolute to trace, which would be written to when generating and read from when parsing.",
    )
    parser.add_argument(
        "-app_args",
        nargs='*',
        default=[],
        help="arguments passed to your app when using generate.",
        required=False
    )
    return parser


def doctorant_toolname_to_dynamorio_toolname(doctorant_toolname: str):
    toolnames_dict = {
        "cache_simulator": "",
        "memory_accesses_human": "-simulator_type view",
        "cache_line_histogram": "-simulator_type histogram"
    }
    return toolnames_dict[doctorant_toolname]


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()
    if args.operation == "parse":
        if args.parse_output == "memory_accesses":
            parse_special(args.trace_path)
        else:
            sim_type = doctorant_toolname_to_dynamorio_toolname(
                args.parse_output)
            parse(args.trace_path, sim_type)
    elif args.operation == "generate":
        generate(args.app_path, args.trace_path, args.app_args)
    else:
        print(f'invalid operation "{args.operation}"')
