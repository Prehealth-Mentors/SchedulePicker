# Name: main.py
# Author: Sam Shenoi
# Description: This file defines the main driver for the project

# Imports
import argparse
from graph import Graph

# Functions
def main(input_file):
    Graph(input_file)

if __name__ =="__main__":
    parser = argparse.ArgumentParser(description='Process command line options')
    parser.add_argument('--input_file', metavar='-i', nargs='+', help='the path to the input file')
    parser.add_argument('--meeting_duration', metavar='-d', type=int,nargs='+', help='the integer duration of the meetings')

    args = parser.parse_args()

    main(args.input_file[0])