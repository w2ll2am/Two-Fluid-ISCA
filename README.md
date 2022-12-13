# Two-Fluid-ISCA
This repository contains a script to automate submission for the two fluid simulation on ISCA for Exeter University. This is a highly specialised software, and therefore cannot be generalised accross other HPCs. I highly recomend changing the settings to meet your needs, as you may need lower resolutions or different colour profiles for your purposes.

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

# Resuts
This script will generate animations of each simulation automatically. An example from over 100GB of simulation data can be seen below.

https://user-images.githubusercontent.com/16038228/207194402-3e266a30-bb43-4163-b18c-b9183a7fd196.mp4

This also generates still images at any given DPI. Allowing for images such as below

![plot0321 (1)](https://user-images.githubusercontent.com/16038228/207419390-1c50b6cd-866e-4ca5-ab02-e99de978c754.png)


# Adding new variable
To add a new variable please add it to the dictionary that contains default values and value descriptions. Each of the dictionaries in the list are for different files, so find whether your variable is in 'ISCA_Submission.sh', 'Hight_Normalisation_(KHH).py', and add accordingly. In your target files, replace the value with an identifyer in the format '$00', '$01', '$02', ... etc. These are counted from 0-n where n is the number of variables that needs to be changed in that file -1 (as it couts from 0).
