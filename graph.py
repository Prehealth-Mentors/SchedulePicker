# Name: graph.py
# Author: Sam Shenoi
# Description: This file defines a class for the creation of a graph based representation of
#  the times that people are availiable to meet

# Imports
from datetime import datetime, date,timedelta
import csv
import time
class Node:
    def __init__(self,email,isMentor,isOpen):
        self.email =email
        self.isMentor = isMentor
        self.isOpen = isOpen

class Graph:
    def __init__(self,filename,meeting_duration=75,weekend_meetings=False,earliest_time="8:00",latest_time="17:00",group_size=10):
        # We need to construct a graphical matrix representation for the possible times and
        #  days that there could possbily be meetings for.
        self.time_format = "%H:%M"

       self.cutoff_score = 80

       self.group_size = group_size

        # To do this, lets first create a dictionary with all of the days of the week
        self.graph = {
            "M":[],
            "T" :[],
            "W":[],
            "R":[],
            "F":[]
        }
        if weekend_meetings:
            self.graph["S"] = []
            self.graph["N"] = []

        # Now for each day of the week, we need to create enough spots for all of the possible times
        timedelt = datetime.strptime(latest_time, self.time_format) - datetime.strptime(earliest_time, self.time_format)
        seconds = timedelt.total_seconds()
        meeting_duration_seconds = meeting_duration * 60
        total_meeting_times = int(seconds/meeting_duration_seconds)



        duration_hours = int(meeting_duration/60)
        duration_minutes = meeting_duration - (duration_hours * 60)
        meeting_duration_string = "%d:%d" % (duration_hours,duration_minutes)


        meeting_time = datetime.strptime(earliest_time, self.time_format)
        for m in range(0,total_meeting_times):
            for g in self.graph.keys():
                self.graph[g].append({"meeting_time":meeting_time.strftime(self.time_format),"PeopleAvailiable":[], "beginning":meeting_time,"ending":meeting_time + timedelta(hours=duration_hours,minutes=duration_minutes)})
            meeting_time = meeting_time + timedelta(hours=duration_hours,minutes=duration_minutes)

        # After we have constructed the graph object, lets read in all of the data to the graph
        self.peopleHash = self.readfile(filename)


    def key_hash(self,key):
        # Since users mess up, (all the time) lets define a function that allows us to use differnt day names
        #  and still hash to the same key
        hash_thing = {
            "monday":"M",
            "mon":"M",
            "m":"M",
            "tuesday":"T",
            "tues":"T",
            "t":"T",
            "wednesday":"W",
            "wed":"W",
            "w":"W",
            "thursday":"R",
            "thurs":"R",
            "r":"R",
            "friday":"F",
            "fri":"F",
            "f":"F",
            "saturday":"S",
            "sat":"S",
            "s":"S",
            "Sunday":"N",
            "Sun":"N",
            "n":"N"
        }
        key = key.strip()
        return hash_thing[key.lower()]

    def readfile(self,filename):
        peopleHash = {}

        with open(filename, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in spamreader:
                # The first element of the table should be the email address of the person
                email = row[0]

                # The second row should be if they are a mentor or not
                isMentor = row[1]

                # The final rows should be the times that the person is availiable
                for z in row[2:]:
                    # First get the day
                    sp = z.split(":")
                    if len(sp) > 1:
                        day = sp[0]

                        # Now get the times

                        times = ":".join(sp[1:]).split("-")


                        # Bad news is that this is a range, so we have to check to see which durations we can fit in
                        for g in range(0,len(self.graph[self.key_hash(day)])):
                            beginning = datetime.strptime(times[0], self.time_format)
                            ending = datetime.strptime(times[1], self.time_format)
                            ti = self.graph[self.key_hash(day)][g]
                            if beginning >= ti["beginning"] and ending <= ti["ending"]:
                                ti["PeopleAvailiable"].append(Node(email,isMentor,True))
                                if email not in peopleHash.keys():
                                    peopleHash[email] = []
                                peopleHash[email].append({"key":day,"time",g})
        return peopleHash



    def find_largest_cluster(self,pasttries=[]):
        # Find the largest cluster of people in the graph first. We can then makes groups out of
        #  these people
        max_people = 0
        str_time = ""
        key = ""

        for g in self.graph.keys():
          possible_times = self.graph[g]
          better_nodes = []
          for e in possible_times:
              nodes = [n for n in e["PeopleAvailiable"] if n.isOpen == True]
              mentors = [n for n in e["PeopleAvailiable"] if n.isMentor == True]
              if len(nodes) > max_people and {"key":key,"time":str_time} not in pasttries and len(mentors) > 0:
                  max_people = len(nodes)
                  str_time = e["meeting_time"]
                  key = g

        return max_people,str_time,key

    def update(self,peoplelist=[],value_change=False):
        print("Hi")
    def make_group(self,ti,key):
        times = self.graph[key]
        obj = None
        for t in times:
            if t["meeting_time"] == ti:
                obj = t
                break

        # Now we have to make a group. This is kinda difficult because we have to figure out
        #  how big to make the groups. We can try differnt values in order to maximize the score
        #  from the scoring function
        mentors = [n for n in obj["PeopleAvailiable"] if n.isMentor == True]

        # Split the mentees into equal group sizes. TODO: possibly shuffling the people around might increase the score
        mentees = [n for n in obj["PeopleAvailiable"] if n.isMentor == False]
        mentees = [mentees[i:i + self.group_size] for i in range(0, len(mentees), self.group_size)]

        best_group = None
        best_score = -1
        for m in mentor:
            for me in mentees
            group = {"key":key,"time":ti,"mentor":m,"mentees":me}

            # Add to the group list for now
            self.groups.append(group)

            # Calculate score
            score = self.calculate_score()

            # Check to see if the score is better than our best
            if best_score < score:
                best_score = score
                best_group = group

            # Now remove from group list so that we dont contaminate
            self.groups = self.groups[0:len(self.groups) -1]

        # Now we take the best group and we update all of the instances of the people to not be open
        self.update(peoplelist=[best_group["mentor"]] + best_group["mentees"])

        # Finally return the score
        return best_score

    def run(self)
      # Lets use a greedy approach at the beginning in order to find groups. We will look for the largest clusters
      #  in the graph and remove them.
      # First, we need to define a condition to kill the learning. We want this condition to happen when we hit an
      # acceptable score.

      # Create an array to hold the groups that we created
      self.groups = []

      # To do this, lets set up an array that will hold the scores over each run
      scores = [0]
      # Next define a kill switch that will activate if the scores don't seem to be improving
      killSwitch = False

      # Define an array that holds the past tries for this
      past_trys = []

      score_ndx = 0

      while not killSwitch and score[len(score) - 1] < self.cutoff_score:
          # First, lets check to see that our previous score is an improvement
          if len(scores) > 1 and scores[score_ndx - 1] < scores[score_ndx - 2]:
              # If its not an improvement, lets pop off the last group and check again
              last_group = self.groups[len(self.groups) -1]
              self.groups = self.groups[0:len(self.groups) -1]
              max_people, str_time, key = self.find_largest_cluster(pasttries=past_trys)
              self.makegroup(str_time,key)



          # Lets find the largest cluster in the group




    def calculate_score(self):
        # The score is used to see how close to a solution we have gotten to
        # The program is trying to optimize the score that it recieves per move
        # So in a way it is "learning" how to make better groups
        # Our scoring function will take the following things into account
        #   Penalities
        #      - left over mentees : the program will receive a penalty for each leftover mentee
        #      - unbalanced group sizes : for each deviation away from the target group size, the program will receive a penalty
        #   Points
        #      - 1 mentor per group: the program will recieve a bonus if it matches exactly one mentor per group
        #      - group created : the program will recieve points for every group that it creates

        score  = 0

        # Get 10 points for each group created
        score = score + len(self.groups) * 10

        # Get 10 points for each group with a mentor in it
        score = score + len([z for z in self.groups if z["mentor"] is not None]) * 10

        # Get points based on the size of the groups
        score = score + sum([10 - (z["mentee"] % self.group_size) for z in self.groups])

        # Lose points for mentees that are left over
        for key in self.peopleHash.keys():
            one_time = self.peopleHash[key][0]
            isOpen = self.graph[one_time["key"]]one_time["time"]
            if isOpen:
                score = score - 1

        return score









