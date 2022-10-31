from datetime import datetime
from email.policy import default
from importlib import invalidate_caches
import subprocess
import shutil
import time
import os
from xmlrpc.client import INVALID_ENCODING_CHAR
import json

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

# with cd ("./"):
#     subprocess.run(["module", "load", "pandas"])

import pandas as pd

def non_negative_int_userInput(prompt, not_negative=True, max=-1, allow_blank=False):
    """
    Get integer input with different boundaries from user
    """
    while True:
        user_input = input(f"{prompt}\n--> ")
        # Allow blank user inputs to show no entry is wanted
        if user_input=="" and allow_blank:
            value = None
            break
        else: 
            try:
                value = int(user_input)
                if value <= 0 and not_negative:
                    print("Sorry, this cannot be a negative number. Please try again.")
                    continue
                elif (max!=-1 and value>max):
                    print(f"Sorry this number is above the maximum value of {max}. Please try again.")
                else:
                    break
            except ValueError:
                print("Sorry, this is not an integer. Please try again.")
                continue
    return value

def y_n_userInput(prompt):
    """
    Get y/n user input to confirm or deny
    """
    while True:
        try:
            y_n = str(input(f"{prompt}\n--> "))
        except ValueError:
            print("Sorry, I didn't understand this.")
            continue
        if y_n == "y":
            output = True
            break
        elif y_n == "n":
            output = False
            break
        else:
            print("Sorry this input was invalid. Please enter either 'y' or 'n'")
    return output

def cumulativeSum(arr):
    """
    Calculate the cumulative sum of an 1xn array of numbers
    """
    total = 0
    cArr = []
    for i in arr:
        total += i
        cArr.append(total)
    return cArr

def display(settings, descriptions):
    # Combine default settings and descriptions ino one array
    displayArr=[]
    
    for i, section in enumerate(settings):
        [displayArr.append([0, key , section[key], descriptions[i][key]]) for key in section.keys()]
    for i in range(len(displayArr)):
        displayArr[i][0]=i+1
    
    # Create and style a dataframe to view this data
    df = pd.DataFrame(displayArr, columns=["Num", "Variable name", "Val", "Description"])
    df.set_index("Num", inplace=True)
    with pd.option_context('display.expand_frame_repr', True, 'max_colwidth', -1, 'display.colheader_justify', 'left'): 
        print(df)
        print("\n")

def interface(settings, run):
    # This function allows the user to choose the settings to be used on this run. 
    # Variable descriptions
    sbatch_descriptions = {
            "cores": "How many CPU cores to run the simulation on (no hyperthreading)?",
            "max_server_time_hours": "Maximum time allowed for the simulation to run on the server. (less than 99)",
            "email_destination": "Which email address to notify when a run is complete",
            "ISCA_queue": "Which queue to send the job to.",
            "research_project": "Which research project to assign to job to. ",
            "memory_usage": "How much memory to give the simulation. (minimum 6GB for 256x256, 10 for 512x512, 20 for 1024x2014)",
            "plot_file_source": "Which plotting file to use (e.g. whole disc or single plot)",
            "framerate": "What framerate to render the animation at. "
        }
    simulation_descriptions = {
            "sim_resolution_x": "x axis resolution to run the simulation at. ",
            "sim_resolution_y": "y axis resolution to run the simulation at.",
            "max_sim_time_iterations": "Maximum number of 100s of iterations",
            "Reynolds": "",
            "Schmidt": "",
            "shear": "",
            "St0": "",
            "Lambda": "",
            "bd0": "",
            "eta": "",
            "timestep_dt": "Timestep of the simulation. Decrease to slowdown the time evolution of the system. "
    }
    plotting_descriptions = {
        "dpi": "DPI of the plot.",
        "color_map": "Which colours to plot density map with. ",
    }
    section_len = [len(section) for section in settings]
    section_cumulativeSum = cumulativeSum(section_len)
    section_min_index = [0 if i==0 else val - section_len[i] for i, val in enumerate(section_cumulativeSum)]
    max=section_cumulativeSum[-1]

    while True:
        print(f"\nRun #{run} settings.\n")
        display(settings, [sbatch_descriptions, simulation_descriptions, plotting_descriptions])
        Num = non_negative_int_userInput(f"To change a setting please choose a Num. between 1-{max}. If you don't want to change any settings press enter.", max=max , allow_blank=True)

        if Num!=None:
            for i, cVal in enumerate(section_cumulativeSum):
                if Num<=cVal:
                    section_num = i
                    break            
            Variable = list(settings[section_num].keys())[Num-section_min_index[section_num]-1]
            new_val = input(f"What value would you like to change {Variable} to?\n--> ")
            settings[section_num][Variable] = new_val
        else:
            break
    return settings

def replace_inplace(filename, find, replace):
    with open(filename, 'r') as file :
        filedata = file.read()

    # Replace the target string
    for i, val in enumerate(replace):
        filedata = filedata.replace(find[i], replace[i])

    # Write the file out again
    with open(filename, 'w') as file:
        file.write(filedata)

def write_settings(simulation_DIR, settings):
    file = json.dumps(settings, indent=2)
    with open(f'{simulation_DIR}/settings.json', 'w') as f:
        f.write(file)

def dedalusPipeline(simulation_DIR):  
    """
    Launch sbatch submission script to run the simulation. Once this is run this script passes all control onto the .sh file. 
    """
    with cd (simulation_DIR):  
        result = subprocess.run(["sbatch", f"ISCA_Submission.sh"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def scheduler(run, settings, run_time):
    PH_DIR = "placeholder_files"
    run_name = f"{run_time}_run-{run}"
    simulation_DIR = f"./Simulations/{run_name}"
    fileToEdit_names = ["ISCA_Submission.sh", "Hight_Normalisation_(KHH).py", ""] # NOTE: Final entry here is to be replaced with user input for the name of plotting file  

    shutil.copytree(PH_DIR, simulation_DIR)

    for i, section in enumerate(settings):
        if i==2:
            fileToEdit_name = settings[0]["plot_file_source"]         
        else: 
            fileToEdit_name = fileToEdit_names[i] 
        # Iterate through values and replace them in the file
        find = []
        values = []
        for j, key in enumerate(section.keys()):
            values.append(str(section[key]))
            if j<10:
                find.append(f"$0{j}")
            else:
                find.append(f"${j}")

        replace_inplace(f"{simulation_DIR}/{fileToEdit_name}", find, values)  

    write_settings(simulation_DIR, settings)
    time.sleep(1)
    dedalusPipeline(simulation_DIR)
    print(f"Simulation {run_name} has been submitted")


def main():
    default_params = [
        {
            "cores": 16,
            "max_server_time_hours": 35,
            "email_destination": "wb310@exeter.ac.uk",
            "ISCA_queue": "pq",
            "research_project": "Research_Project-CEMPS-00006",
            "memory_usage": 28,
            "plot_file_source": "Plot_Single.py",
            "framerate": 50
        },
        {
            "sim_resolution_x": 1024,
            "sim_resolution_y": 1024,
            "max_sim_time_iterations": 8000,
            "Reynolds": 2e-6,
            "Schmidt": 1.0,
            "shear": 1.5,
            "St0": 0.05,
            "Lambda": 0.05,
            "bd0": 0.1,
            "eta": 5e-2,
            "timestep_dt": 1.25e-3
        },
        {
            "dpi": 180,
            "color_map": "gray",
        }
    ]
    time_now = datetime.now()
    run_time = time_now.strftime(f"%d-%m-%y_%H-%M-%S")
    run = 1

    settings = default_params.copy()
    while True:
        print("\n")
        settings = interface(settings, run)
        scheduler(run, settings, run_time)
        another = y_n_userInput("\nWould you like to do another run? Please type 'y' or 'n'")
        if another:
            run += 1
            continue
        else:
            break

if __name__=="__main__":
    main()