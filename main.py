# Name: main.py
# Author: Sam Shenoi
# Description: This file defines the main driver for the project

# Imports
import argparse
from graph import Graph
from emailer import Emailer

# Functions
def main(args):
    g = Graph(args.input_file[0],meeting_duration=args.meeting_duration,earliest_time=params[""],latest_time=args.latest_time,sample_size=args.sample_size,group_size=args.group_size,time_delta=args.time_delta)
    # Set the score arguements
    g.set_score_args(args.unmatched_weight,args.groupsize_weight,args.num_groups_weight,args.feature_weight)
    best_score,final_groups,unmatched = g.run(generation_cap=args.max_generations,mentors_per_group=args.mentors_per_group)

    if len(best_score) > 0:
        print("Best Score: %f" % best_score[0])
        if args.send_emails or best_score[0] >= args.emails_theshold:
            print("Sending emails",best_score[0],args.emails_theshold)
            #e = Emailer()
            #e.send_email()
            #e.close()


if __name__ =="__main__":
    parser = argparse.ArgumentParser(description='Process command line options')

    # Optional Args
    parser.add_argument('--meeting_duration', metavar='-d', type=int,nargs='?', default=75,  help='the integer duration of the meetings')
    parser.add_argument('--group_size', metavar='-g', default=None, type=int,nargs='?', help='the target size of the groups. Defaults to num_mentees/num_mentors')
    parser.add_argument('--earliest_time', metavar='-e', nargs='?',default="8:00AM",  help='the earliest time for a meeting in HH:MM(AM/PM) format. Defaults to 08:00AM')
    parser.add_argument('--latest_time', metavar='-l',  nargs='?', default="5:00PM", help='the latest time for a meeting in HH:MM(AM/PM) format. Defaults to 5:00PM')
    parser.add_argument('--max_generations', metavar='-m', type=int,nargs='?', default=500, help='the maximum number of generations. Defaults to 500')
    parser.add_argument('--weekend_meetings', metavar='-w', type=bool,nargs='?', default=False,const=True, help='weekend meetings')
    parser.add_argument('--sample_size', metavar='-s', type=int,nargs='?', default=25,const=25, help='The sample size of each generation. Larger values will result in higher accuracy. Lower values will result in higher speed.')
    parser.add_argument("--mentors_per_group",metavar='-mpg',type=int,nargs='?',default=1,const=1,help="The number of mentors per group")
    parser.add_argument("--time_delta",metavar='-td',type=int,nargs='?',default=15,const=15,help="The time delta between groups")

    # Email Arguments
    emailargs = parser.add_argument_group('email args')
    emailargs.add_argument('--send_emails', metavar='-se', type=bool,nargs='?', default=False,const=True, help='Send emails immediately after running the program. (Not recommended)')
    emailargs.add_argument('--emails_theshold', metavar='-et', type=float,nargs='?', default=100,const=90, help='Send emails if the final score is greater than or equal to a threshold.')


    # Score args
    scoreargs = parser.add_argument_group('score args')
    scoreargs.add_argument('--unmatched_weight',metavar='-uw',type=float,nargs='?',default=.45,const=.45,help="The weight of having unmatched people. Must be 0-1 and total arguments of score arguements must equal 1")
    scoreargs.add_argument('--groupsize_weight',metavar='-gsw',type=float,nargs='?',default=.15,const=.15,help="The weight of the group size Must be 0-1 and total arguments of score arguements must equal 1")
    scoreargs.add_argument('--num_groups_weight',metavar='-ngw',type=float,nargs='?',default=.25,const=.25,help="The weight of num groups. Must be 0-1 and total arguments of score arguements must equal 1")
    scoreargs.add_argument('--feature_weight',metavar='-fw',type=float,nargs='?',default=.15,const=.15,help="The weight of additional features. Must be 0-1 and total arguments of score arguements must equal 1")

    # Required arguments
    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument('--input_file', required=True, metavar='-i', nargs='+', help='the path to the input file')

    args = parser.parse_args()


    main(args)