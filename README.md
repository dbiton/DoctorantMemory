# DoctorantMemory

DoctorantMemory is a tool used for instrumenting memory accesses, which was tailor-made for our use case with simplicity in mind.
It instruments applications and generate memory access traces, which can be analyzed with multiple tools. 

## Description

DynamoRIO is an instrumentation framework for the development of program analysis tools. 
DrCacheSim is a tool in the DynamoRIO framework that collects instruction and memory access traces using its DrMemTrace component.
It feeds the traces to either an online or offline tool for analysis.
This project includes a python CLI for communicating with DynamoRIO's DrCacheSim.

Read more about DrCacheSim here: https://dynamorio.org/page_drcachesim.html.

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

Check out the examples folder

### Documentation

Each function in this project is documented by a docstring. A docstring includes a paragraph describing what the function does, its inputs and outputs. If you prefer not going through the code, you can use pdoc to display the documentation elegantly.

```
pip install pdoc
pdoc doctorant_memory.py
```

## License

This project is licensed under the BSD License.
