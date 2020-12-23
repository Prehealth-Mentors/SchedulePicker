# Name: main.py
# Author: Sam Shenoi
# Description: This file defines the main driver for the project

# Imports
import argparse
from graph import Graph

# Functions
def main(args):
    g = Graph(args.input_file[0],meeting_duration=args.meeting_duration,weekend_meetings=args.weekend_meetings,earliest_time=args.earliest_time,latest_time=args.latest_time,sample_size=args.sample_size)
    #g.test()
    #g.write_graph()
    g.run(generation_cap=args.max_generations)


if __name__ =="__main__":
    parser = argparse.ArgumentParser(description='Process command line options')

    parser.add_argument('--meeting_duration', metavar='-d', type=int,nargs='?', default=75,  help='the integer duration of the meetings')
    parser.add_argument('--group_size', metavar='-g', type=int,nargs='?', help='the target size of the groups. Defaults to num_mentees/num_mentors')
    parser.add_argument('--earliest_time', metavar='-e', nargs='?',default="8:00AM",  help='the earliest time for a meeting in HH:MM(AM/PM) format. Defaults to 08:00AM')
    parser.add_argument('--latest_time', metavar='-l',  nargs='?', default="5:00PM", help='the latest time for a meeting in HH:MM(AM/PM) format. Defaults to 5:00PM')
    parser.add_argument('--max_generations', metavar='-m', type=int,nargs='?', default=500, help='the maximum number of generations. Defaults to 500')
    parser.add_argument('--weekend_meetings', metavar='-w', type=bool,nargs='?', default=False,const=True, help='weekend meetings')
    parser.add_argument('--sample_size', metavar='-s', type=int,nargs='?', default=25,const=25, help='The sample size of each generation. Larger values will result in higher accuracy. Lower values will result in higher speed.')
    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument('--input_file', required=True, metavar='-i', nargs='+', help='the path to the input file')

    args = parser.parse_args()


    main(args)