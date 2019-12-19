## Data Preprocessing

### Set-Up
The project runs in virtual environments created with venv.<br/>
To create the environment for this section run `python3 -m venv ea-venv`<br/>
To activate the environment run `source ea-venv/bin/activate`<br/>
To install all necessary packages run `pip install -r requirements.txt` from within the environment <br/>

After setup the environment can be activated at any time from `main/src/preprocessing/` with `source ea-venv/bin/activate` and exited with `deactivate`


### Exploratory Analysis
In order to run the jupyter notebooks for Exploratory Analysis from this virtual environment, the venv must be installed as a kernel (See preparation/README.md for instructions on setting up your venv). This can be done by:

```
# Activate your venv if not already activated
`source ea-venv/bin/activate`

# Add the venv to Jupyter as a new kernel
python -m ipykernel install --user --name=ea-venv

#Launch the notebook
jupyter notebook
```

Once in the jupyter notebook you will have to set the kernel to your new `ea-venv` kernel. Do this by clicking `Kernel` in the menu, hovering over `Change kernel` and then selecting `ea-venv`.

### The Data

For ease of navigation, below is a preview of the inside of the pandas dataframe pickles that can be loaded from `main/data/dataframes`. `data_level` will be `file` or `function`, and `partition` will be `test`, `training`, `validation` or `bpe`.

ID | data_level | language | partition | repository | file_name | contents
------------ | ------------- | ------------ | ------------ | ------------ | ------------ | ------------
0 | file | cpp | test | BillyIII_Recorder | Exceptions.cpp | #include "stdafx.h"\n#include "Exceptions.h"\n...
1 | file | cpp | test | BillyIII_Recorder | Log.cpp | #include "StdAfx.h"\n#include "Log.h"\n\nHANDL...
2 | file | cpp | test | BillyIII_Recorder | StateNotify.cpp | #include "StdAfx.h"\n#include "StateNotify.h"\...
... | ... | ... | ... | ... | ... | ...
1732 | file | cpp | test | vburchik_psi | src_profiledlg.cpp | #include <cppunit/Portability.h>\n#include <cp...
1733 | file | cpp | test | vburchik_psi | src_profiledlg.cpp | #include <cppunit/TestFailure.h>\n#include <cp...
