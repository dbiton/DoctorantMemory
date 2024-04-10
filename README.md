# DoctorantMemory

DocctorantMemory is a wrapper of DynamoRIO tools, which was tailor-made for our use case with simplicity in mind.
It instruments applications to generate memory access traces. Different tools are available to analyze the traces. 

## Description

This project include a python CLI for communicating with DynamoRIO's drcachesim, which is a tool that can be used to extract the memory accesses of an application.

### Dependencies

Before you start using DoctorantMemory, you need to download DynamoRIO's binaries.
DoctorantMemory was developed with DynamoRIO version 10.0.0, although other versions might also work.
Releases can be found on DynamoRIO's site:

https://dynamorio.org/page_releases.html

Download the zip matching your OS and extract it in the folder containing doctorant_memory.py.
If you want to change DynamoRIO's release, don't forget to update its folder name in doctorant_memory.py.

Google has published traces which utilize DynamoRIO. If you want to analyze the with DoctorantMemory, you need to download them using gsutil. There is a guide for installing gsutil here:

https://cloud.google.com/storage/docs/gsutil_install#deb

You can ignore the gsinit step, since its not needed for downloading the traces.
After installing gsutil, the following command would download all of the traces to you current working directory:

```
gsutil -m cp -r \
  "gs://external-traces/CONTRIBUTING.md" \
  "gs://external-traces/LICENSE" \
  "gs://external-traces/README" \
  "gs://external-traces/charlie" \
  "gs://external-traces/delta" \
  "gs://external-traces/merced" \
  "gs://external-traces/whiskey" \
  .
```

Note that the traces are extremly large (hundreds of GB).


### Executing program

You can use the -h flag for help:

```
doctorant_memory.py -h
```

Below follows a short demonstration of using DoctorantMemory.
We have placed an executable named "HelloWorld.exe" In doctorant_memory.py's folder.
The executable prints "Hello World!" and exits. To generate a trace of the exe, we use:

```
python .\doctorant_memory.py -operation generate -app_path ./HelloWorld.exe 
```

DoctorantMemory then creates a file named DOCTORANT_MEMORY_TS, with TS being an iso timestamp of the time the trace was created, for example: DOCTORANT_MEMORY_20240410T143504Z. This file contains the output of the executable, which is also printed to the console. The trace information is written to a folder created by drcachesim in the current working directory. The folder is named by drcachesim, for example: drmemtrace.HelloWorld.exe.17564.4748.dir. You can set the path where the folder would be created, with additional folders created if needed:

 ```
python .\doctorant_memory.py -operation generate -app_path ./HelloWorld.exe -trace_path folder0/folder1/folder2
```

The folders /folder0, etc. would be created if needed. Inside /folder2 the trace folder would be created.


To analyze our trace, we could use the following command:

```
python .\doctorant_memory.py -operation parse -trace_path folder0\folder1\folder2\drmemtrace.HelloWorld.exe.02752.5578.dir
```

Your drmemtrace folder would have a different name, so make sure to change it in the command. The default parsing tool shows a cache simulation with hits, misses, etc. You can use other avaliable tools, for example:

```
python .\doctorant_memory.py -operation parse -trace_path folder0\folder1\folder2\drmemtrace.HelloWorld.exe.02752.5578.dir -parse_tool_name cache_line_histogram
```

### Documentation

Each function in this project is documented by a docstring. A docstring includes a paragraph describing what the function does, its inputs and outputs. If you prefer not going through the code, you can use pdoc to display the documentation elegantly.

```
pip install pdoc
pdoc doctorant_memory.py
```

## License

This project is licensed under the BSD License.