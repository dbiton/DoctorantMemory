## Getting a Trace

If you are interested in generating your own trace, we have included an example "Hello World!" application in C. 
Before running it, you should compile it with gcc.

```commandline
gcc main.c -o HelloWorld
```

Afterwards, you can generate you own trace using:
```commandline
python ./doctorant_memory.py -operation generate -app_path examples/HelloWorld
```

The trace would be created inside a folder. You can change the folder's name if you like.

We have also included the trace output in this folder, in the "example trace" folder, in case you are having troble 
generating your own trace.

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