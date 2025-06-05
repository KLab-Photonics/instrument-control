# Instrument Control

This repository contains Python scripts and device drivers for automated control and data acquisition from a spectrometer and a motorized delay stage.

## Directory Structure

    instrument-control/
    │
    ├── Device_Drivers/
    │       ├── stellarnet_driverLibs -> Drivers for the spectrometer
    │       ├── __init__.py           -> For Package Import Statements
    │       ├── lockin_driver.py      -> Driver File Created For The UHFLI
    │       └── move_stage_driver.py  -> Driver File Created For The DL225 Move Stage
    │
    ├── lockin/
    │       ├── lockinlive.py         -> Main Script For The Lockin Experiments + Live Graping Of Data
    │       └── lockinV1.py           -> Main Script For The Lockin Experiments
    │
    ├── spec_test/
    │       ├── connectiontest.py     -> Script To Test The Connection Of Devices Using Stellarnet Driver (after setup.py is ran)
    │       └── setup.py              -> One Time Setup To Use The Python Drivers For The Spectrometers
    │
    ├── spectrometer/
    │       ├── driver_functions.py   -> A List Of Python Driver Functions From The Stellarnet Python Driver Documentation
    │       └── spectrometerV1.py     -> Main Script For Spectrometer Experiments
    │
    └── requirements.txt          -> List Of All Python Packages Needed For Functionality


## Requirements

- Python 3.12.9 (Currently)

Install dependencies with:

- pip install -r requirements.txt (On Command Line/Powershell)

## Customization

- I Recommend to edit the driver files in `Device_Drivers/` (such as for the UHFLI or Move Stage) to add new commands or features.

- By adding to these drivers, you can easily add more advanced or custom functionality to the main experiment scripts for additional instruments or experimental procedures as needed.

## Usage

To install the file from github, navigate to command prompt / powershell and follow these steps:

1. Navigate to your desktop using the cd command  ( you should see C:\Users\your-name\Desktop\ )

2. Run the command -> git clone https://github.com/KLab-Photonics/instrument-control.git
    
    This will clone the file to your desktop where you can now run the scripts

**Recommended:**  
I recommend to open the folder after cloning from the github in Visual Studio Code.
VSCode will let you see all the files/scripts and the live data being collected.
It also keeps everything in one place and organized in a terminal while there is no GUI implemented at this time.

**Alternatively, to run from the command line (without VS Code):**

1. Open Command Prompt or PowerShell.


2. Navigate to the project directory:
   
   cd C:\Users\your-name\Desktop\instrument-control
   

3. Install dependencies:
   
   pip install -r requirements.txt
   

4. Run the desired script, for example:
   
   python spectrometer/spectrometerV1.py
   
   or
   
   python lockin/lockinV1.py
   

