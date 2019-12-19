## Database Usage 

### Preface and Requirements
This README.md is not a tutorial for using mongo. All commands and specifications are specific to usage with the mongo instance installed on Poshyvanyk's semeru server. However, associated files have also been tested on a localhost community edition mongo database (4.0.10) and, to the best of our knowledge, should also work there. 

Related python packages can be found in the `requirements.txt` file of the `preparation` folder, however the only database specific package is `pymongo`.

### Configuration of Semeru Server
The mongo configuration on the Semeru Server is as such
```
MongoDB shell version v4.2.1
git version: edf6d45851c0b9ee15548f0f847df141764a317e
OpenSSL version: OpenSSL 1.1.1  11 Sep 2018
allocator: tcmalloc
modules: none
build environment:
    distmod: ubuntu1804
    distarch: x86_64
    target_arch: x86_64
```
Command Line Options for the database are as follows:

```
{
	"argv" : [
		"/usr/bin/mongod",
		"--config",
		"/etc/mongod.conf"
	],
	"parsed" : {
		"config" : "/etc/mongod.conf",
		"net" : {
			"bindIp" : "127.0.0.1",
			"port" : 27017
		},
		"processManagement" : {
			"timeZoneInfo" : "/usr/share/zoneinfo"
		},
		"storage" : {
			"dbPath" : "/scratch/mongodb-data/",
			"journal" : {
				"enabled" : true
			}
		},
		"systemLog" : {
			"destination" : "file",
			"logAppend" : true,
			"path" : "/var/log/mongodb/mongod.log"
		}
	},
	"ok" : 1
}
```
### Intro to Using the PyMongo wrapper 

For a basic testcase using the pymongo wrapper class, see `/main/src/preparation/database/minimal_test_case.py`

Included in this file is a connecting to a database, creating a document, inserting the document, and then querying the database. 

For more information, see the documentation at https://api.mongodb.com/python/current/tutorial.html#

### Format of Database
The database has the following format, with the outer level representing an instance, the second level databases, and the inner collections:
```
.
└── mongo instance [instance]
    ├── admin [database]
    ├── config
    ├── local
    ├── test
    ├── file_level
    │   ├── cpp [collection]
    │   ├── java
    │   ├── js
    │   ├── py
    │   └── scala
    ├── file_level_testbed
    │   ├── cpp
    │   ├── java
    │   ├── js
    │   ├── py
    │   └── scala
    ├── method_level
    │   ├── cpp
    │   ├── java
    │   ├── js
    │   ├── py
    │   └── scala
    └── method_level_testbed
        ├── cpp
        ├── java
        ├── js
        ├── py
        └── scala
```

All documents are collected into the `file_level` initialy, and should then be parsed and placed into the `method_level` database. The testbed databases should contain 100 files or methods that do not run. 

Inside of the `file_level` database, a single document has the following fields:
* `_id`: an object id, assigned by mongo, each document has a unique id.
* `repo_name`: string, the user or group name and the repository name, in the format `"username_reponame"`, for example `"caged_microsis"`. 
* `path_in_repo`: string, the path to the file in the original repository. This field is included for traceability. For example, `"ThumbnailGenerator/ImageProcessor.java"`
* `url`: string, the url where the file was downloaded from. These should be raw git hub urls, for example `"https://raw.githubusercontent.com/galaxycats/nostromo/master/ThumbnailGenerator/ImageProcessor.java"`
* `file_name`: string, the name of the file, for example `"ImageProcessor.java"`
* `file_contents`: string, the entire contents of the file
* `partition`: string, from [null, "train", "test", "validation", "bpe"]. If the partition is null the file has not been placed in a partition yet

All of the documents in the `method_level` database have the same fields, except with a `method_contents` field (a string), a  `method_name` field (a string) and a `method_number` field (an integer, used only to distinguish one method from another, they are arbitrary). 

