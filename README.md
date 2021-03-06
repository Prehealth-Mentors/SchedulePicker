# SchedulePicker
This repository creates a schedule for peer leading based on mentor/mentee availability

## Authors
 - Sam Shenoi

## Input data
The program uses a specific comma seperated value (csv) file format in order to handle multiple people being inserted at once. Please refer to the **sampledata/sample.txt** file for an example of how the data must be formatted.
There are no checks currently to ensure that your data is in the correct format so the program will epically fail if
the data is not provided in a correct format.

Some highlights to the file format are listed below
- First row needs to be email and **only** email. The program does not accept names
- Second row is a binary (0 or 1) value specifying if the person is a mentor or mentee. 1 means mentor 0 means mentee
- The program allows for optional binary features to be inserted here. These features can be things such as onlineOnly, or isTransfer student. The program will try to optimize these features if possible.

- The remaining rows are the days of the week and times that the person is availiable. These entries must be comma seperated and be in the following format.
   - day of the week:start time-end time, ...
   - Ex: M:2:00PM-4:00PM,T:10:0AM-5:00PM

## How to run
- To run this program first clone the repository.
     - Go to https://github.com/Prehealth-Mentors/SchedulePicker
     - Click on the green **Code** button
     - There are two options to download this folder: git or zip
     - If you have git installed on your computer, copy the link in the box and type in the following command in your terminal `git clone <link>`
     - Otherwise just download the zip file.
- Now that the repository is cloned. Make sure that you have python3 installed on your computer.(https://www.python.org/downloads/)
- Now that python is installed, navigate to the folder that you just cloned in your terminal.
    - `cd <path to folder>`
- Finally, run the program using the following command
    - `python3 main.py --input_file <path to file>`
    - For a full list of the options that this program provides run
    - `python3 main.py -h`

## Output
The program outputs to two files: **groups.csv** and **unmatched.csv**. The groups.csv file contains the Meeting Day, Meeting Time, Mentor,Mentees for each group. This file is csv file which can then be opened in excel. Unmatched.csv
contains people who the program was unable to find a group for based on their availibility.

## Additional Cool Stuff
In order to test the program with sample data, there is a python program included that will generate random data.
It is called `datagen.py`. In order to run it, simply run `python3 datagen.py`

There is also a file that will send emails based on the results of groups.csv called emailer.py. It can be run either by running `python3 emailer.py` or by specifiying the `--send_emails` flag when running main.py. The emailer requires a gmail account credentials in order to run. For security purposes, this information must be stored in the config.txt which is not included in version control. The first time you run the emailer program, this file will be created for you. Please just fill it out.

## FAQs
There might be some issues with the commands listed in this document. This program and commands were written based on
the MacOS operating system. Some common issues are listed below.

- git is not a recognized command
  - if you are on windows install git bash. Google it, it's pretty easy to install
  - if you are on macos install xcode. If you dont want to wait 8 hours for xcode to download
      google how to install the xcode-command line tools.

- python3 is not a recognized command
  - Make sure that python is installed. Try replacing python3 with python and see if that works.
  - Installing python on windows is a pain sometimes. If it doesn't work go find somebody with a mac and xcode installed

- program crashes
  - your data is in the incorrect format or the program writers messed up. Check your data first and if it still doesn't work then send an email to whoever is in charge of this to get it fixed.

- Package not installed error
  - All of the packages used in this project should be installed in a default python installation. However, just in case a requirements.txt file is provided. To use it run the following commands
      - Install pip: https://pip.pypa.io/en/stable/installing/
      - Install virtualenv: `pip3 install virtualenv`
      - Create the virtualenv: `virtualenv venv`
      - Start the vritualenv: `source venv/bin/activate`
      - Install packages: `pip3 install -r requirements.txt`
      - Run the program normally

