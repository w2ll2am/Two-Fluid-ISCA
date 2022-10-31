# Two-Fluid-ISCA
Script to automate script submission for two fluid simulation on ISCA for Exeter University.

# Instructions for use
Install with git using: 
```console
git clone https://github.com/w2ll2am/Two-Fluid-ISCA
```
This uses pandas for the table in the shell, this must be loaded on ISCA. To do this use
```console
module load pandas
```
Then run the script using 
```console
python3 hpc_script.py
```

# Adding new variable
To add a new variable please add it to the dictionary that contains default values and value descriptions. Each of the dictionaries in the list are for different files, so find whether your variable is in 'ISCA_Submission.sh', 'Hight_Normalisation_(KHH).py', and add accordingly. In your target files, replace the value with an identifyer in the format '$00', '$01', '$02', ... etc. These are counted from 0-n where n is the number of variables that needs to be changed in that file -1 (as it couts from 0).
