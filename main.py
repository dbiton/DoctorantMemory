import argparse
import subprocess
import os
from pathlib import Path

if os.name == 'nt':
    drrun_path = "DynamoRIO-Windows-10.0.0/bin64/drrun"
else:
    drrun_path = "DynamoRIO-Linux-10.0.0/bin64/drrun"


def invoke_drcachesim(args: list):
    command = [drrun_path, "-t", "drcachesim"] + args
    return subprocess.run(
        command, 
        text=True,
        capture_output=True
    )


def generate(app_path: str, trace_path: str, app_args: list):
    Path(trace_path).mkdir(parents=True, exist_ok=True)
    print(invoke_drcachesim(["-offline", "-outdir", trace_path, "--", app_path] + app_args).stderr)


def parse(trace_path: str, sim_type: str):
    print(invoke_drcachesim(["-indir" , trace_path]+sim_type.split()).stderr)

def parse_special(trace_path: str):
    dr_result = invoke_drcachesim(["-indir" , trace_path, "-simulator_type", "view"])
    raw_result = dr_result.stderr # unsure why it outputs to stderr instead of stdout...
    lines = raw_result.splitlines()[3:-2]
    # <record> <instr>: <tid> <record-details> 
    result = []
    for line in lines:
        timestamp = "TODO"
        tokens = line.split() 
        tid = tokens[2]
        record_details_header = tokens[3]
        if record_details_header == "ifetch":
            op = "I" #instruction
        elif record_details_header == "write":
            op = "W"
        elif record_details_header == "read":
            op = "R"
        else:
            continue # ignore markers for now
        address = tokens[7]
        size = tokens[4] # should check type after?
        assert(tokens[5] == "byte(s)")
        result.append(f"{timestamp},{tid},{address},{size},{op}")
    print (result)

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
        choices=["cache_simulator", "memory_accesses_human", "memory_accesses","cache_line_histogram"],
        default="cache_sim",
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
        "cache_sim" : "",
        "memory_accesses_human" : "-simulator_type view",
        "cacheline_histogram" : "-simulator_type histogram"
    }
    return toolnames_dict[doctorant_toolname]

if __name__ == "__main__":
    parse_special("drmemtrace.hello_world.48293.4895.dir")

    parser = create_parser()
    args = parser.parse_args()
    if args.operation == "parse":
        if args.parse_output == "memory_accesses":
            parse_special(args.trace_path)
        else:
            sim_type = doctorant_toolname_to_dynamorio_toolname(args.parse_output)
            parse(args.trace_path, sim_type)
    elif args.operation == "generate":
        generate(args.app_path, args.trace_path, args.app_args)
    else:
        print(f'invalid operation "{args.operation}"')