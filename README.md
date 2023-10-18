A sample script to import data into the hiaudio platform. 


# Install

```bash
git clone git@gitlab.enst.fr:idsinge/hiaudio/hiaudio_import.git
cd hiaudio_import

# inside a venv recommanded
pip install -e . 
```

This will install a `hiaudio_import` script in the PATH of the venv. This script only runs the `main()` function of the 'hiaudio_import/hiimport.py` file which can be edited without reinstalling the package. 


# Usage

The basic idea is to provide the script with patterns on how to find collections, compositions and tracks to import. 

```
$ hiaudio_import -h
usage: hiaudio_import [-h] [--loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}] [--endpoint ENDPOINT] [--token-var TOKEN_VAR] --dataset-path DATASET_PATH [--parent-collection PARENT_COLLECTION] [--collections-pattern COLLECTIONS_PATTERN] [--compositions-pattern COMPOSITIONS_PATTERN]
                      [--tracks-pattern TRACKS_PATTERN]

An import script for hiaudio.fr

options:
  -h, --help            show this help message and exit
  --loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Global log level
  --endpoint ENDPOINT   the endpoint location of the platform
  --token-var TOKEN_VAR
                        the environment variable containing the JWT for API requests
  --dataset-path DATASET_PATH
                        the main folder containing the dataset
  --parent-collection PARENT_COLLECTION
                        an option collection name for everything that will be imported
  --collections-pattern COLLECTIONS_PATTERN
                        the pattern to find collections folders, relative to dataset root [default: no collections]
  --compositions-pattern COMPOSITIONS_PATTERN
                        the pattern to find compositions [default: %(collection_path)s/*]
  --tracks-pattern TRACKS_PATTERN
                        the pattern to find tracks [default: %(composition_path)s/*]
```


# Examples

The following examples are based on the [DSD100 sample](https://www.loria.fr/~aliutkus/DSD100subset.zip) dataset which has the following file structure:

```
$ tree DSD100subset
DSD100subset
├── Mixtures
│   ├── Dev
│   │   ├── 055 - Angels In Amplifiers - I'm Alright
│   │   │   └── mixture.wav
│   │   └── 081 - Patrick Talbot - Set Me Free
│   │       └── mixture.wav
│   └── Test
│       ├── 005 - Angela Thomas Wade - Milk Cow Blues
│       │   └── mixture.wav
│       └── 049 - Young Griffo - Facade
│           └── mixture.wav
├── Sources
│   ├── Dev
│   │   ├── 055 - Angels In Amplifiers - I'm Alright
│   │   │   ├── bass.wav
│   │   │   ├── drums.wav
│   │   │   ├── other.wav
│   │   │   └── vocals.wav
│   │   └── 081 - Patrick Talbot - Set Me Free
│   │       ├── bass.wav
│   │       ├── drums.wav
│   │       ├── other.wav
│   │       └── vocals.wav
│   └── Test
│       ├── 005 - Angela Thomas Wade - Milk Cow Blues
│       │   ├── bass.wav
│       │   ├── drums.wav
│       │   ├── other.wav
│       │   └── vocals.wav
│       └── 049 - Young Griffo - Facade
│           ├── bass.wav
│           ├── drums.wav
│           ├── other.wav
│           └── vocals.wav
├── dsd100.xlsx
└── dsd100subset.txt

14 directories, 22 files
```


Here are some script commands to import the data, depending on the wanted resulting structure:

```bash

# first add the JWT token to the environment variables for API call
export JWT="myjwtoken"

# for localhost testing add "--endpoint https://localhost:7007" to all commands


# import all compositions in Sources/, wether they are in Dev/ or in Test/, into a flat hierarchy
hiaudio_import  --dataset-path ../DSD100subset/ --compositions-pattern "Sources/*/*"


# import all compositions in Sources/, wether they are in Dev/ or in Test/, all under a parent collection (with debug level logging)
hiaudio_import --loglevel DEBUG --dataset-path ../DSD100subset/ --compositions-pattern "Sources/*/*" --parent-collection "DSD100subset" 


# import compositions in Sources dir, following the directory structure for collections 
# (the default values for compositions and tracks patterns will find the right data here)
hiaudio_import --dataset-path ../DSD100subset/ --collections-pattern "Sources/*"

```

Sample run of the last example: 

```
2023-10-18 16:00:21 [hiaudio_import.hiimport:MainThread] INFO: [1/2] Found collection 'Dev' at Sources/Dev
2023-10-18 16:00:21 [hiaudio_import.hiimport:MainThread] INFO:  [1/2] Found composition 055 - Angels In Amplifiers - I'm Alright
2023-10-18 16:00:21 [hiaudio_import.hiimport:MainThread] INFO:          [1/4] Adding track: bass.wav
2023-10-18 16:00:21 [hiaudio_import.hiimport:MainThread] INFO:          [2/4] Adding track: drums.wav
2023-10-18 16:00:21 [hiaudio_import.hiimport:MainThread] INFO:          [3/4] Adding track: other.wav
2023-10-18 16:00:21 [hiaudio_import.hiimport:MainThread] INFO:          [4/4] Adding track: vocals.wav
2023-10-18 16:00:22 [hiaudio_import.hiimport:MainThread] INFO:  [2/2] Found composition 081 - Patrick Talbot - Set Me Free
2023-10-18 16:00:22 [hiaudio_import.hiimport:MainThread] INFO:          [1/4] Adding track: bass.wav
2023-10-18 16:00:22 [hiaudio_import.hiimport:MainThread] INFO:          [2/4] Adding track: drums.wav
2023-10-18 16:00:22 [hiaudio_import.hiimport:MainThread] INFO:          [3/4] Adding track: other.wav
2023-10-18 16:00:22 [hiaudio_import.hiimport:MainThread] INFO:          [4/4] Adding track: vocals.wav
2023-10-18 16:00:22 [hiaudio_import.hiimport:MainThread] INFO: [2/2] Found collection 'Test' at Sources/Test
2023-10-18 16:00:22 [hiaudio_import.hiimport:MainThread] INFO:  [1/2] Found composition 005 - Angela Thomas Wade - Milk Cow Blues
2023-10-18 16:00:22 [hiaudio_import.hiimport:MainThread] INFO:          [1/4] Adding track: bass.wav
2023-10-18 16:00:23 [hiaudio_import.hiimport:MainThread] INFO:          [2/4] Adding track: drums.wav
2023-10-18 16:00:23 [hiaudio_import.hiimport:MainThread] INFO:          [3/4] Adding track: other.wav
2023-10-18 16:00:23 [hiaudio_import.hiimport:MainThread] INFO:          [4/4] Adding track: vocals.wav
2023-10-18 16:00:23 [hiaudio_import.hiimport:MainThread] INFO:  [2/2] Found composition 049 - Young Griffo - Facade
2023-10-18 16:00:23 [hiaudio_import.hiimport:MainThread] INFO:          [1/4] Adding track: bass.wav
2023-10-18 16:00:23 [hiaudio_import.hiimport:MainThread] INFO:          [2/4] Adding track: drums.wav
2023-10-18 16:00:24 [hiaudio_import.hiimport:MainThread] INFO:          [3/4] Adding track: other.wav
2023-10-18 16:00:24 [hiaudio_import.hiimport:MainThread] INFO:          [4/4] Adding track: vocals.wav
2023-10-18 16:00:24 [hiaudio_import.hiimport:MainThread] INFO: Imported 2 collections, 4 compositions, 16 tracks.
```


# TODO

- handle multiple level of collections
- handle privacy parameter (for now everything is set to private)
- extract description
- extract more metadata when the platform supports it (artist, instrument, etc.)
- add options to upload raw metadata for unsupported fields (may be used in postprocessing)
- test with more data volume and more datasets
