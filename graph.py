# Name: graph.py
# Author: Sam Shenoi
# Description: This file defines a class for the creation of a graph based representation of
#  the times that people are availiable to meet

# Imports
from datetime import datetime, date,timedelta
import csv
import time
import random

class Node:
    def __init__(self,email,isMentor,isOpen):
        self.email =email
        self.isMentor = isMentor
        self.isOpen = isOpen

class Graph:
    def __init__(self,filename,meeting_duration=75,weekend_meetings=False,earliest_time="8:00AM",latest_time="5:00PM",group_size=10):
        # We need to construct a graphical matrix representation for the possible times and
        #  days that there could possbily be meetings for.
        self.time_format = "%I:%M%p"

        self.cutoff_score = 80

        self.group_size = group_size

        # To do this, lets first create a dictionary with all of the days of the week
        self.graph = {
            "M":[],
            "T" :[],
            "W":[],
            "R":[],
            "F":[],
            "S":[],
            "N":[]
        }
        if weekend_meetings:
            self.graph["S"] = []
            self.graph["N"] = []

        # Now for each day of the week, we need to create enough spots for all of the possible times
        duration_hours = int(meeting_duration/60)
        duration_minutes = meeting_duration - (duration_hours * 60)


        meeting_time = datetime.strptime(earliest_time, self.time_format)
        while meeting_time + timedelta(hours=duration_hours,minutes=duration_minutes) < datetime.strptime(latest_time, self.time_format):
            for g in self.graph.keys():
                self.graph[g].append({"meeting_time":meeting_time.strftime(self.time_format),"PeopleAvailiable":[], "beginning":meeting_time,"ending":meeting_time + timedelta(hours=duration_hours,minutes=duration_minutes)})
            meeting_time = meeting_time + timedelta(minutes=15)

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
                isMentor = row[1] == '1'

                # The final rows should be the times that the person is availiable
                for z in row[2:]:
                    # First get the day
                    sp = z.split(":")

                    if len(sp) > 1:
                        day = sp[0]

                        # Now get the times

                        times = ":".join(sp[1:]).split("-")
                        beginning = datetime.strptime(times[0], self.time_format)
                        ending = datetime.strptime(times[1], self.time_format)

                        # Bad news is that this is a range, so we have to check to see which durations we can fit in
                        for g in range(0,len(self.graph[self.key_hash(day)])):
                            ti = self.graph[self.key_hash(day)][g]
                            if ti["beginning"] >= beginning and ti["ending"] <= ending:
                                ti["PeopleAvailiable"].append(Node(email,isMentor,True))
                                if email not in peopleHash.keys():
                                    peopleHash[email] = []
                                peopleHash[email].append({"key":day.strip(),"time":g})
        return peopleHash



    def find_largest_cluster(self,pasttries=[]):
        # Find the largest cluster of people in the graph first. We can then makes groups out of
        #  these people
        max_people = 0
        str_time = None
        key = None

        for g in self.graph.keys():
          possible_times = self.graph[g]
          better_nodes = []

          for e in possible_times:
              nodes = [n for n in e["PeopleAvailiable"] if n.isOpen == True]
              mentors = [n for n in nodes if n.isMentor == True]

              if len(nodes) > max_people and {"key":key,"time":str_time} not in pasttries and len(mentors) > 0:
                  max_people = len(nodes)
                  str_time = e["meeting_time"]
                  key = g

        return max_people,str_time,key

    def find_target_size_cluster(self,pasttries=[]):
        str_time = None
        key = None
        for g in self.graph.keys():
          possible_times = self.graph[g]

          for e in possible_times:
              nodes = [n for n in e["PeopleAvailiable"] if n.isOpen == True]
              mentors = [n for n in nodes if n.isMentor == True]

              if len(nodes) == self.group_size - len(mentors) and {"key":key,"time":str_time} not in pasttries and len(mentors) > 0:
                  str_time = e["meeting_time"]
                  key = g
                  break
        return self.group_size,str_time,key



    def update(self,peoplelist=[],value_change=False):
        for people in peoplelist:
            vals = self.peopleHash[people.email]
            for v in vals:
                time_slot = self.graph[self.key_hash(v["key"])][v["time"]]["PeopleAvailiable"]
                for t in time_slot:
                    if t.email == people.email:
                        t.isOpen = value_change

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
        mentors = [n for n in obj["PeopleAvailiable"] if n.isMentor == True and n.isOpen == True]

        # Split the mentees into equal group sizes. TODO: possibly shuffling the people around might increase the score
        mentees = [n for n in obj["PeopleAvailiable"] if n.isMentor == False]

        mentees = [m for m in mentees if m.isOpen == True]

        # Shuffle up the mentees so that we get a better version
        random.shuffle(mentees)

        mentees_list = [mentees[i:i + self.group_size] for i in range(0, len(mentees), self.group_size)]
        larger_size = int(self.group_size * 1.5)
        mentees_list = mentees_list + [mentees[i:i + larger_size ] for i in range(0, len(mentees), larger_size )]



        best_group = None
        best_score = float('-inf')
        for m in mentors:
          for me in mentees_list:
            group = {"key":key,"time":ti,"mentor":m,"mentees":me}

            # Add to the group list for now
            self.groups.append(group)
            self.update(peoplelist=[m] + me,value_change=False)

            # Calculate score
            score = self.calculate_score()

            # Check to see if the score is better than our best
            if best_score < score:
                best_score = score
                best_group = group

            # Now remove from group list so that we dont contaminate
            self.groups = self.groups[0:len(self.groups) -1]
            self.update(peoplelist=[m] + me,value_change=True)

        # Now we take the best group and we update all of the instances of the people to not be open
        self.update(peoplelist=[best_group["mentor"]] + best_group["mentees"])

        # Finally return the score
        return best_score,best_group

    def write_graph(self):
        print("----------------")
        for g in self.graph.keys():
            l = self.graph[g]
            for i in l:
                if len(i["PeopleAvailiable"]) > 0:
                    p = [pp.email for pp in i["PeopleAvailiable"] ]
                    print(g,i["meeting_time"]," ".join(p))
    def run(self):
        # Lets use a greedy approach at the beginning in order to find groups. We will look for the largest clusters
        #  in the graph and remove them.
        # First, we need to define a condition to kill the learning. We want this condition to happen when we hit an
        # acceptable score.

        # Create an array to hold the groups that we created
        self.groups = []

        # To do this, lets set up an array that will hold the scores over each run
        scores = []
        # Next define a kill switch that will activate if the scores don't seem to be improving
        killSwitch = False

        # Define an array that holds the past tries for this
        past_trys = []

        score_ndx = 0

        iteration = 1

        total_people = len(self.peopleHash.keys())

        print("Running optomization... This might take a while")
        while not killSwitch:
            past_trys = []

            max_people, str_time, key = self.find_target_size_cluster()
            if key == None:
                max_people, str_time, key = self.find_largest_cluster()
            if key == None:
                killSwitch = True
            else:
                score,group = self.make_group(str_time,key)
                self.groups.append(group)
                scores.append(score)

            # After 20 iteration lets the user know that we are still going
            if iteration % 5 == 0:
                percent = ((iteration * self.group_size)/total_people) * 100
                print("About %f\% complete" % percent)
            iteration = iteration + 1

        self.match_unmatched()
        self.write_results(self.groups,scores)
    def match_unmatched(self):
        # We still have some leftover people. Lets see if we can find them a home
        unmatched = self.find_unmatched_mentees()

        matched = []

        for um in unmatched:
            # Get all of the times that this person is free
            times = self.peopleHash[um]
            p_nodes = self.graph[times[0]["key"]][times[0]["time"]]["PeopleAvailiable"]
            p_node = [p for p in p_nodes if p.email == um][0]
            killSwitch = False

            # For each of those times, check to see if there is a group that is meeting
            for t in times:
                if not killSwitch:
                    meeting_time = self.graph[t["key"]][t["time"]]["meeting_time"]

                    for g in self.groups:
                        if g["time"] == meeting_time and g["key"] == t["key"] and not killSwitch:
                            g["mentees"].append(p_node)
                            killSwitch = True
                            matched.append(p_node)
                            break

        self.update(matched)



    def write_results(self,groups,scores):
        f = open("groups.csv","w")
        f.write("Meeting Day, Meeting Time, Mentor,Mentees\n")
        for g in groups:
            mentee_list = " ".join([z.email for z in g["mentees"]])
            f.write("%s,%s,%s,%s\n" % (g["key"],g["time"],g["mentor"].email,mentee_list))
        f.close()
        f = open("unmatched.csv","w")
        unmatched = self.find_unmatched_mentees()
        f.write("Email\n")
        for u in unmatched:
            f.write(u + "\n")
        f.close()




    def find_unmatched_mentees(self):
        left_over_people = []
        for key in self.peopleHash.keys():
            if key in left_over_people:
                continue
            one_time = self.peopleHash[key][0]
            people = self.graph[self.key_hash(one_time["key"])][one_time["time"]]["PeopleAvailiable"]
            left_over = [p.email for p in people if p.isOpen == True]
            left_over_people = left_over_people + left_over
        return list(set(left_over_people))




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
        score = score + sum([10 - min(len(z["mentees"]) % self.group_size,10-len(z["mentees"])) for z in self.groups])

        # Lose points for mentees that are left over
        score = score - len(self.find_unmatched_mentees())* 10


        return score









