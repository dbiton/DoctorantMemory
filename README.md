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

## License

This project is licensed under the BSD License.