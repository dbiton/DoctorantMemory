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
if os.name == "nt":
    drrun_path = "DynamoRIO-Windows-10.0.0/bin64/drrun"
else:
    drrun_path = "DynamoRIO-Linux-10.0.0/bin64/drrun"


def get_timestamp():
    """
    Returns the current timestamp

        Returns:
            timestamp (str): the current time as an iso compliant string
    """
    timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
    return timestamp


def invoke_drcachesim(args: list, folder_path = ""):
    """
    Invokes drcachesim with given arguments and writes
    the output to a file, returns the file path.

        Parameters:
            args (list): the arguments supplied to drcachesim

        Returns:
            output_path (str): the path to a file containing the invocation results
    """
    output_path = f"drcachesim_output_{get_timestamp()}.txt"
    command = [drrun_path, "-t", "drcachesim"] + args
    if len(folder_path) > 0:
        Path(folder_path).mkdir(parents=True, exist_ok=True)
        command = [drrun_path, "-t", "drcachesim"] + ["-outdir", folder_path] + args
        output_path = f"{folder_path}/{output_path}"
    output_file = open(output_path, "w")
    subprocess.run(command, stdout=output_file, stderr=output_file)
    return output_path


def generate(app_path: str, output_path: str, app_args: list, trace_path: str, additional_options: str):
    """
    Invokes an app with given arguments, writes
    the trace output to trace_path and prints it.

        Parameters:
            app_path (str): the path to the app to be executed
            app_args (list): the args that would be supplied to the app
            trace_path (str): the path trace will be written to

        Returns:
            output_path (str): the path to a file containing the invocation results
    """
    Path(trace_path).mkdir(parents=True, exist_ok=True)
    result_path = invoke_drcachesim(
        additional_options.split() + ["-offline", "-outdir", trace_path, "--", app_path] + app_args,
        output_path
    )
    return result_path


def parse(trace_path: str, output_path: str, sim_type: str, additional_options: str):
    """
    Parses a trace and processes it with requested tool,
    writes the results to a file and prints them.

        Parameters:
            sim_type (str): the name of the tool to be used
            trace_path (str): the path the trace is at

        Returns:
            result_path (str): the path to a file containing the parse results
    """
    result_path = invoke_drcachesim(additional_options.split() + ["-indir", trace_path] + sim_type.split(), output_path)
    return result_path


# wouldn't work in windows
def sort_file_in_place(path_file, reverse=False):
    if os.name == "nt":
        raise "Implement me!"
        command = ["sort", path_file, "/O", path_file]
        if reverse:
            command += ["/R"]
    else:
        command = ["sort", "-n", "-o", path_file, path_file]
        if reverse:
            command += ["-r"]
    subprocess.run(command)


def count_unique_in_sorted_file_in_place(path_file):
    tmp_file = f"COUNT_UNIQUE_{get_timestamp()}"
    if os.name == "nt":
        raise Exception("Implement for Windows!")
    else:
        command = [f"uniq -c {path_file} > {tmp_file} && mv {tmp_file} {path_file}"]
    subprocess.run(command, shell=True)


def parse_special_get_hot_addresses(
        bytes_per_address,
        max_address,
        unparsed_trace_path,
        max_count_addresses_print,
        ignore_instruction_fetch,
        result_path,
        output_folder_path
):
    digits_per_address = int(math.log10(max_address)) + 1
    path_hot_addr = f"hot_addresses_{get_timestamp()}.txt"
    if len(output_folder_path) > 0:
        path_hot_addr = os.path.join(output_folder_path, path_hot_addr)
    relevant_access_types = ["write", "read"]
    if not ignore_instruction_fetch:
        relevant_access_types.append("ifetch")
    with open(path_hot_addr, "w") as f_hot_addr:
        with open(unparsed_trace_path, "r") as f_mem_access:
            header = [next(f_mem_access) for i in range(3)]
            for line in f_mem_access:
                tokens = line.split()
                if tokens[0] == "View":
                    break
                elif tokens[3] in relevant_access_types:
                    address = int(tokens[7], 0)
                    request_size = int(tokens[4])
                    address_first = address // bytes_per_address * bytes_per_address
                    address_last = (
                            (address + request_size)
                            // bytes_per_address
                            * bytes_per_address
                    )
                    for address_curr in range(
                            address_first, address_last + 1, bytes_per_address
                    ):
                        # adds leading zero for sorting
                        f_hot_addr.write(
                            f"{format(address_curr, f'0{digits_per_address}d')}\n"
                        )
                elif tokens[0] == "View":
                    break
    # sort by address
    sort_file_in_place(path_hot_addr)
    # count accesses to each address
    count_unique_in_sorted_file_in_place(path_hot_addr)
    # sort by number of accesses
    sort_file_in_place(path_hot_addr, True)
    with open(result_path, 'a') as file_out:
        print(f"# cacheline size: {bytes_per_address}", file=file_out)
        print(f"# hot addresses count: {max_count_addresses_print}", file=file_out)
        print("# hot addresses (accesses | address):", file=file_out)
        count_addresses_printed = 0
        with open(path_hot_addr, "r") as f_hot_addr:
            for line in f_hot_addr:
                print(f"# {line.strip()}", file=file_out)
                count_addresses_printed += 1
                if count_addresses_printed >= max_count_addresses_print:
                    break
    return path_hot_addr


def parse_special_collect_statistics(result_path):
    min_timestamp = float("inf")
    max_timestamp = float("-inf")
    min_address = float("inf")
    max_address = float("-inf")
    bytes_read = 0
    bytes_write = 0
    count_reads = 0
    count_writes = 0
    count_instructions = 0
    with open(result_path, "r") as f:
        header = [next(f) for i in range(3)]
        for line in f:
            tokens = line.split()
            if tokens[0] == "View":
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
                    count_reads += 1
                elif tokens[3] == "ifetch":
                    count_instructions += 1
    return (
        min_timestamp,
        max_timestamp,
        min_address,
        max_address,
        bytes_read,
        bytes_write,
        count_reads,
        count_writes,
        count_instructions,
    )


def parse_special(
        trace_path: str,
        output_folder_path: str,
        ignore_instruction_fetch: bool,
        hot_addresses_count: int,
        cacheline_size_bytes: int,
):
    """
    Parses a trace and processes it to doctorant's simulator format,
    prints the results.

        Parameters:
            trace_path (str): the path the trace is at
    """
    result_path = f"doctorant_memory_trace_{get_timestamp()}.txt"
    if len(output_folder_path) > 0:
        result_path = os.path.join(output_folder_path, result_path)
    unparsed_trace_path = invoke_drcachesim(["-indir", trace_path, "-simulator_type", "view"], output_folder_path)
    (
        min_timestamp,
        max_timestamp,
        min_address,
        max_address,
        bytes_read,
        bytes_write,
        count_reads,
        count_writes,
        count_instructions,
    ) = parse_special_collect_statistics(unparsed_trace_path)

    hot_addresses_path = parse_special_get_hot_addresses(
        cacheline_size_bytes,
        max_address,
        unparsed_trace_path,
        hot_addresses_count,
        ignore_instruction_fetch,
        result_path,
        output_folder_path
    )

    if ignore_instruction_fetch:
        count_instructions = 0
    with open(result_path, 'a') as f_tmp:
        print("# max address:", max_address - min_address, file=f_tmp)
        print("# max timestamp:", (max_timestamp - min_timestamp) / 1000, file=f_tmp)
        print("# bytes read:", bytes_read, file=f_tmp)
        print("# bytes write:", bytes_write, file=f_tmp)
        print(
            f"# read requests: {round(100 * count_reads / (count_reads + count_instructions + count_writes), 2)}%",
            file=f_tmp
        )
        print(
            f"# write requests: {round(100 * count_writes / (count_reads + count_instructions + count_writes), 2)}%",
            file=f_tmp
        )
        if not ignore_instruction_fetch:
            print(
                f"# instruction fetch requests: {round(100 * count_instructions / (count_reads + count_instructions + count_writes), 2)}%",
                file=f_tmp
            )
    cur_timestamp = None
    with open(result_path, 'a') as f_tmp:
        with open(unparsed_trace_path, "r") as f:
            header = [next(f) for i in range(3)]
            for line in f:
                tokens = line.split()
                if tokens[0] == "View":
                    break
                tid = tokens[2]
                record_details_header = tokens[3]
                if record_details_header == "ifetch":
                    if ignore_instruction_fetch:
                        continue
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
                assert tokens[5] == "byte(s)"
                entry = [cur_timestamp, tid, curr_address, size, op]
                entry[0] = (entry[0] - min_timestamp) / 1000
                entry[2] = entry[2] - min_address
                output_line = ",".join([str(v) for v in entry])
                print(output_line, file=f_tmp)
    return hot_addresses_path, unparsed_trace_path, result_path


def create_parser():
    """
    Configures an ArgumentParser that takes input using a CLI,
    allowing the user to communicate with DoctorantMemory.

        Returns:
            parser (argparse.ArgumentParser): the ArgumentParser we configure
    """
    parser = argparse.ArgumentParser(
        prog="DoctorantMemory", description="DrMemory wrapper"
    )
    parser.add_argument(
        "-operation",
        choices=["parse", "generate"],
        help="type of operation to perform.",
    )
    parser.add_argument(
        "-app_path",
        help="relative or absolute to app, which would be instrumented when using generate.",
        required=False,
    )
    parser.add_argument(
        "-parse_tool_name",
        choices=[
            "cache_simulator",
            "memory_accesses_drcachesim",
            "memory_accesses",
            "cache_line_histogram",
        ],
        default="cache_simulator",
        help="relative or absolute to app, which would be instrumented when using generate.",
        required=False,
    )
    parser.add_argument(
        "-trace_path",
        default=".",
        help="relative or absolute to trace, which would be read from when parsing.",
    )
    parser.add_argument(
        "-output_path",
        default=".",
        help="relative or absolute to a folder which would be created if needed, to which we will write the output.",
    )
    parser.add_argument(
        "-additional_options",
        default="",
        help="additional options passed directly to drcachesim",
    )
    parser.add_argument(
        "-parse_ignore_inst",
        action="store_true",
        help="ignore memory accesses caused by fetching instructions in memory_accesses's parse tool",
    )
    parser.add_argument(
        "-app_args",
        nargs="*",
        default=[],
        help="arguments passed to your app when using generate.",
        required=False,
    )
    parser.add_argument(
        "-parse_hot_addresses_count",
        default=10,
        help="how many hot addresses to include in the header of the memory_accesses parse tool.",
        type=int,
    )
    parser.add_argument(
        "-parse_alignment_size",
        default=16,
        help="The alignment size used in memory_accesses in bytes. For example, if set to 3 an access to address 30 and address 31 would be grouped together",
        type=int,
    )
    return parser


def translate_toolname(doctorant_toolname: str):
    """
    Converts the names we use for our tools, to the names used by drcachesim.
        Parameters:
            doctorant_toolname(str): our name for the tool
        Returns:
            drcachesim_toolname (str): drcachesim's name for the tool
    """
    toolnames_dict = {
        "cache_simulator": "",
        "memory_accesses_drcachesim": "-simulator_type view",
        "cache_line_histogram": "-simulator_type histogram",
    }
    drcachesim_toolname = toolnames_dict[doctorant_toolname]
    return drcachesim_toolname


def run():
    parser = create_parser()
    args = parser.parse_args()
    if args.operation == "parse":
        if args.parse_tool_name == "memory_accesses":
            hot_addresses_path, unparsed_trace_path, result_path = parse_special(
                args.trace_path,
                args.output_path,
                args.parse_ignore_inst,
                args.parse_hot_addresses_count,
                args.parse_alignment_size,
            )
            print(hot_addresses_path, unparsed_trace_path, result_path)
        else:
            sim_type = translate_toolname(args.parse_tool_name)
            result_path = parse(args.trace_path, args.output_path, sim_type, args.additional_options)
            print(result_path)
    elif args.operation == "generate":
        result_path = generate(args.app_path, args.output_path, args.app_args, args.trace_path, args.additional_options)
        print(result_path)
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)


if __name__ == "__main__":
    run()
