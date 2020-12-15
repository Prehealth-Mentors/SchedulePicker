# SchedulePicker
This repository creates a schedule for peer leading based on mentor/mentee availability

## Authors
 - Sam Shenoi

## Input data
The program uses a specific comma seperated value (csv) file format in order to handle multiple people being inserted at once. Please refer to the sampledata/in.txt file for an example of how the data must be formatted. There are no
checks currently to ensure that your data is in the correct format so the program will epically fail if
the data is not provided in a correct format.

Some highlights to the file format are listed below
- First row needs to be email and **only** email. The program does not accept names
- Second row is a binary (0 or 1) value specifying if the person is a mentor or mentee. 1 means mentor 0 means mentee
- The remaining rows are the days of the week and times that the person is availiable. These entries must be comma seperated and be in the following format.
   - <day of the week>:<start time>-<end time>, ...
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


