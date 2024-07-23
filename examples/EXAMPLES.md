# Examples

In this folder you can find an example program, it's trace, and the outputs when parsing the trace with each of the available tools.

## Generating your own trace

If you are interested in generating your own trace, we have included an example "Hello World!" application in C. 
Before running it, you should compile it with gcc.

```commandline
gcc main.c -o HelloWorld
```

Afterwards, you can generate you own trace using:
```commandline
python ./doctorant_memory.py -operation generate -app_path examples/HelloWorld
```

## Parsing a Trace

Once you have a trace, you can parse it. The output of is determined by which tool you use. By default, a cache 
simulator tool is used, showing how much of the cache is occupied, the cache levels etc. 
```commandline
python ./doctorant_memory.py -operation parse -trace_path examples/example_trace
```

To select a different tool, you can use the -parse_tool_name option:

```commandline
python ./doctorant_memory.py -operation parse -trace_path examples/example_trace -parse_tool_name memory_accesses
```

Your drmemtrace folder could have a different name, so make sure to change it if needed.
You can use other avaliable tools, for example:

```
python .\doctorant_memory.py -operation parse -trace_path examples/example_trace -parse_tool_name cache_line_histogram
```

Each folder here is named after the tool used to generate its content.