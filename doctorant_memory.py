import argparse
import math
import subprocess
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

"""
    DrCacheSim wrapper for easy usage
"""

# Tested on windows (nt) and linux.
if os.name == 'nt':
    drrun_path = "DynamoRIO-Windows-10.0.0/bin64/drrun"
else:
    drrun_path = "DynamoRIO-Linux-10.0.0/bin64/drrun"


def get_timestamp():
    '''
    Returns the current timestamp 

        Returns:
            timestamp (str): the current time as an iso compliant string    
    '''
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return timestamp


def invoke_drcachesim(args: list):
    '''
    Invokes drcachesim with given arguments and writes 
    the output to a file, returns the file path.

        Parameters:
            args (list): the arguments supplied to drcachesim

        Returns:
            output_path (str): the path to a file containing the invocation results    
    '''
    output_path = f"DOCTORANT_MEMORY_{get_timestamp()}"
    output_file = open(output_path, 'w')
    command = [drrun_path, "-t", "drcachesim"] + args
    subprocess.run(
        command,
        stdout=output_file,
        stderr=output_file
    )
    return output_path


def generate(app_path: str, app_args: list, trace_path: str, delete_logs: bool):
    '''
    Invokes an app with given arguments, writes 
    the trace output to trace_path and prints it.

        Parameters:
            app_path (str): the path to the app to be executed
            app_args (list): the args that would be supplied to the app
            trace_path (str): the path trace will be written to

        Returns:
            output_path (str): the path to a file containing the invocation results    
    '''
    Path(trace_path).mkdir(parents=True, exist_ok=True)
    result_path = invoke_drcachesim(["-offline", "-outdir", trace_path, "--", app_path] + app_args)
    with open(result_path, 'r') as f:
        for line in f:
            print(line)
    if delete_logs:
        os.remove(result_path)


def parse(trace_path: str, sim_type: str, delete_logs: bool):
    '''
    Parses a trace and processes it with requested tool, 
    writes the results to a file and prints them. 

        Parameters:
            sim_type (str): the name of the tool to be used
            trace_path (str): the path the trace is at

        Returns:
            result_path (str): the path to a file containing the parse results    
    '''
    result_path = invoke_drcachesim(["-indir", trace_path]+sim_type.split())
    with open(result_path, 'r') as f:
        for line in f:
            print(line)
    if delete_logs:
        os.remove(result_path)

# wouldn't work in windows
def sort_file_in_place(path_file, reverse = False):
    if os.name == 'nt':
        raise "Implement me!"
        command = ["sort", path_file, "/O", path_file]
        if reverse:
            command += ['/R']
    else:
        command = ["sort", "-n", "-o", path_file, path_file]
        if reverse:
            command += ['-r']
    subprocess.run(command)

def count_unique_in_sorted_file_in_place(path_file):
    tmp_file = f"COUNT_UNIQUE_{get_timestamp()}"
    if os.name == 'nt':
        raise Exception("Implement for Windows!")
    else:
        command = [f'uniq -c {path_file} > {tmp_file} && mv {tmp_file} {path_file}']
    subprocess.run(command, shell=True)

# ignore fetch?
def parse_special_get_hot_addresses(bytes_per_address, max_address, result_path,count_addresses_print):
    digits_per_address = int(math.log10(max_address))+1
    path_tmp = f"DOCTORANT_MEMORY_HOT_ADDRESSES_{get_timestamp()}"
    with open(path_tmp, 'w') as f_tmp:
        with open(result_path, 'r') as f:
            header = [next(f) for i in range(3)]
            for line in f:
                tokens = line.split()
                if tokens[0] == 'View':
                    break
                elif tokens[3] in ["ifetch", "write", "read"]:
                    address = int(tokens[7], 0)
                    request_size = int(tokens[4])
                    address_first = address // bytes_per_address * bytes_per_address
                    address_last = (address + request_size) // bytes_per_address * bytes_per_address
                    for address_curr in range(address_first, address_last+1, bytes_per_address):
                        # adds leading zero for sorting
                        f_tmp.write(f"{format(address_curr, f'0{digits_per_address}d')}\n")
                elif tokens[0] == 'View':
                    break
    # sort by address
    sort_file_in_place(path_tmp)
    # count accesses to each address
    count_unique_in_sorted_file_in_place(path_tmp)
    # sort by number of accesses
    sort_file_in_place(path_tmp, True)
    print("hot addresses (accesses | address):")
    count_addresses_printed = 0
    with open(path_tmp, 'r') as f_tmp:
        for line in f_tmp:
            print(line.strip())
            count_addresses_printed += 1
            if count_addresses_printed == count_addresses_print:
                break
            
    
def parse_special_collect_statistics(result_path):
    min_timestamp = float('inf')
    max_timestamp = float('-inf')
    min_address = float('inf')
    max_address = float('-inf')
    bytes_read = 0
    bytes_write = 0
    count_reads = 0
    count_writes = 0
    count_instructions = 0
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
                request_size = int(tokens[4])
                min_address = min(address, min_address)
                max_address = max(address, max_address)
                if tokens[3] == "write":
                    bytes_write += request_size
                    count_writes += 1
                elif tokens[3] == "read":
                    bytes_read += request_size
                    count_reads+=1
                elif tokens[3] == "ifetch":
                    count_instructions += 1
    return min_timestamp, max_timestamp,min_address,max_address,bytes_read,bytes_write,count_reads,count_writes,count_instructions

def parse_special(trace_path: str, delete_logs: bool):
    '''
    Parses a trace and processes it to doctorant's simulator format, 
    prints the results.

        Parameters:
            trace_path (str): the path the trace is at
    '''
    result_path = invoke_drcachesim(["-indir", trace_path, "-simulator_type", "view"])
    min_timestamp, max_timestamp,min_address,max_address,bytes_read,bytes_write,count_reads,count_writes,count_instructions = parse_special_collect_statistics(result_path)
    parse_special_get_hot_addresses(64, max_address, result_path, 10)
    print("max address:", max_address-min_address)
    print("max timestamp:", (max_timestamp - min_timestamp) / 1000)
    print("bytes read:", bytes_read)
    print("bytes write:", bytes_write)
    print(f"read requests: {round(100*count_reads / (count_reads + count_instructions + count_writes), 2)}%")
    print(f"write requests: {round(100*count_writes / (count_reads + count_instructions + count_writes), 2)}%")
    print(f"instruction fetch requests: {round(100*count_instructions / (count_reads + count_instructions + count_writes), 2)}%")
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
    if delete_logs:
        os.remove(result_path)


def create_parser():
    '''
    Configures an ArgumentParser that takes input using a CLI,
    allowing the user to communicate with DoctorantMemory.

        Returns:
            parser (argparse.ArgumentParser): the ArgumentParser we configure
    '''
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
        "-parse_tool_name",
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
        "-delete_logs",
        action="store_true",
        help="delete files containing app output and parse results after printing them to the console"
    )
    parser.add_argument(
        "-app_args",
        nargs='*',
        default=[],
        help="arguments passed to your app when using generate.",
        required=False
    )
    return parser


def translate_toolname(doctorant_toolname: str):
    '''
    Converts the names we use for our tools, to the names used by drcachesim.
        Parameters:
            doctorant_toolname(str): our name for the tool
        Returns:
            drcachesim_toolname (str): drcachesim's name for the tool
    '''
    toolnames_dict = {
        "cache_simulator": "",
        "memory_accesses_human": "-simulator_type view",
        "cache_line_histogram": "-simulator_type histogram"
    }
    drcachesim_toolname = toolnames_dict[doctorant_toolname]
    return drcachesim_toolname


def run():
    parser = create_parser()
    args = parser.parse_args()
    if args.operation == "parse":
        if args.parse_tool_name == "memory_accesses":
            parse_special(args.trace_path, args.delete_logs)
        else:
            sim_type = translate_toolname(args.parse_tool_name)
            parse(args.trace_path, sim_type, args.delete_logs)
    elif args.operation == "generate":
        generate(args.app_path, args.app_args, args.trace_path, args.delete_logs)
    if len(sys.argv)==1:
        parser.print_help(sys.stderr)

if __name__ == "__main__":
    run()
