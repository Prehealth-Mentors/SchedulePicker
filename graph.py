# Name: graph.py
# Author: Sam Shenoi
# Description: This file defines a class for the creation of a graph based representation of
#  the times that people are availiable to meet

# Imports
from datetime import datetime, date,timedelta
import csv
import time
import random
import copy
import statistics

class Node:
    def __init__(self,email,isMentor,isOpen):
        self.email =email
        self.isMentor = isMentor
        self.isOpen = isOpen

class Graph:
    def __init__(self,filename,meeting_duration=75,weekend_meetings=False,earliest_time="8:00AM",latest_time="5:00PM"):
        # We need to construct a graphical matrix representation for the possible times and
        #  days that there could possbily be meetings for.
        self.time_format = "%I:%M%p"

        self.cutoff_score = 80



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
            "sunday":"N",
            "sun":"N",
            "n":"N"
        }
        key = key.strip()
        return hash_thing[key.lower()]

    def readfile(self,filename):
        peopleHash = {}
        num_mentors = 0
        is_first = True
        with open(filename, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in spamreader:
                if is_first:
                    is_first = False
                else:
                    # The first element of the table should be the email address of the person
                    email = row[0]

                    # The second row should be if they are a mentor or not
                    num_mentors = num_mentors + int(row[1])
                    isMentor = row[1] == '1'

                    node = Node(email,isMentor,True)
                    peopleHash[email] = node

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
                                    ti["PeopleAvailiable"].append(copy.copy(node))

        # Calculate the target group size based on the mentor mentee ratio
        self.group_size = int((len(peopleHash.keys()) - num_mentors)/num_mentors)
        print("Group Size:%s" % self.group_size)

        return peopleHash



    def find_largest_cluster(self):
        str_time = None
        key = None
        clusters = []
        for g in self.graph.keys():
          possible_times = self.graph[g]

          for e in possible_times:
              nodes = [n for n in e["PeopleAvailiable"] if n.isOpen == True]
              mentors = [n for n in nodes if n.isMentor == True]

              if len(mentors) > 0:
                  clusters.append({"str_time":e["meeting_time"],"key":g})
        return self.group_size,clusters


    def find_target_size_clusters(self,pasttries=[]):
        str_time = None
        key = None
        clusters = []
        for g in self.graph.keys():
          possible_times = self.graph[g]

          for e in possible_times:
              nodes = [n for n in e["PeopleAvailiable"] if n.isOpen == True]
              mentors = [n for n in nodes if n.isMentor == True]

              if len(nodes)- len(mentors) >= self.group_size  and {"key":key,"time":str_time} not in pasttries and len(mentors) > 0:
                  clusters.append({"str_time":e["meeting_time"],"key":g})
        return self.group_size,clusters





    def update(self,peoplelist=[],value_change=False):
        for people in peoplelist:
            val = self.peopleHash[people.email]
            val.isOpen = value_change


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
        mentees_list = [mentees[0:self.group_size]]
        mentees_list = mentees_list + [mentees[0:min(len(mentees),int(self.group_size*1.5))]]
        mentees_list = mentees_list + [mentees[0:int(self.group_size*.5)]]


        '''
        mentees_list = [mentees[i:i + self.group_size] for i in range(0, len(mentees), self.group_size)]
        larger_size = int(self.group_size * 1.5)
        mentees_list = mentees_list + [mentees[i:i + larger_size ] for i in range(0, len(mentees), larger_size )]
        '''



        best_group = None
        best_score = float('-inf')

        for me in mentees_list:
            group = {"key":key,"time":ti,"mentor":mentors[0],"mentees":me}

            # Add to the group list for now
            self.groups.append(group)
            self.update(peoplelist=[mentors[0]] + me,value_change=False)

            # Calculate score
            score = self.calculate_score()

            # Check to see if the score is better than our best
            if best_score < score or best_group == None:
                best_score = score
                best_group = group

            # Now remove from group list so that we dont contaminate
            self.groups = self.groups[0:len(self.groups) -1]
            self.update(peoplelist=[mentors[0]] + me,value_change=True)

        # Finally return the score
        return best_score,best_group

    def write_graph(self):

        for g in self.graph.keys():
            l = self.graph[g]
            for i in l:
                if len(i["PeopleAvailiable"]) > 0:
                    p = [pp.email for pp in i["PeopleAvailiable"] if pp.isOpen==True]
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

        generation = 0

        total_people = len(self.peopleHash.keys())

        print("Running optomization... This might take a while")
        self.tree = dict()
        groupnumber = 0
        while not killSwitch:
            # We are trying a generation based approach
            # To do this, we first need to find parents from the previous generation
            ids = [e for e in self.tree.keys() if self.tree[e]["generation"]+1 ==generation]


            # In order to prevent exponential running time, we need to cap the number of ids that we explore
            #  Lets randomly sample some ideas.
            ids = random.sample(ids,min(len(ids),100))


            # If we have no ids that means that we are in the first generation.
            if len(ids) == 0:
                max_people, clusters = self.find_target_size_clusters()
                clusters = random.sample(clusters,20)

                groupnumber = self.process_cluster(clusters,groupnumber,generation)

            else:
                killSwitch = True
                # Otherwise, we have to loop through all of the groups from the previous generation
                # and create the next generation based on that.
                for id in ids:
                    grp = self.tree[id]

                    # Lets first update the graph, so that we are up to date with previous versions
               
                    self.update(peoplelist=grp["total_people"],value_change=False)

                    # Now lets find the clusters that we are looking for
                    max_people, clusters = self.find_target_size_clusters()


                    # if we can't find anything with the target size, lets just try to make a few more groups
                    if len(clusters) == 0:
                        max_people,clusters = self.find_largest_cluster()

                    print(len(clusters))

                    # If we still can't find anything, this id is donzo
                    if len(clusters) != 0:
                        killSwitch = False
                        # Create new nodes for each cluster
                        groupnumber = self.process_cluster(clusters,groupnumber,generation,parent=id,prevpeople=grp["total_people"])

                    # Un-update so we don't contaminate results
                    self.update(peoplelist=grp["total_people"],value_change=True)

            # In order to prevent exponental increase, we need to prune the tree after each generation
            self.prune(generation)
            print("Completed generation %s" % generation)

            generation = generation +1

        # Find the highest scoring family and write the results
        groups,scores = self.get_highest()

        self.write_results(groups,scores)

    def get_highest(self):
        best_score = self.tree[0]["score"]
        best_group_id = 0
        for key in self.tree.keys():
            if self.tree[key]["score"] > best_score:
                best_group_id = key
                best_score =self.tree[key]["score"]
        groups = []
        scores = []
        best_group = self.tree[best_group_id]
        while best_group["generation"] > -1:
            groups.append(best_group["group"])
            scores.append(best_group["score"])
            best_group = self.tree[best_group["parent"]]
        return groups,scores


    def prune(self,generation):

        counter = generation
        while counter > -1:
            # When pruneing, we want to try to remove a lot of branches that have no path towards viability
            # Ideally, we want to limit the amount of work in the next generation. To do this, we need to treat
            # this generation and the previous generations differently
            if counter == generation:
                median_score = statistics.median([self.tree[e]["score"] for e in self.tree.keys() if self.tree[e]["generation"] == generation])


                # Lets remove everything from this generation that falls below the median
                ids = [e for e in self.tree.keys() if self.tree[e]["generation"] == generation and self.tree[e]["score"] < median_score]
                for i in ids:
                    del self.tree[i]
            else:
                # The main reason we would want to prune an earlier branch is if the likelihood that groups stemming from this generation
                #  to be a good solution are really unlikely. The following reasons might lead to this conclusion
                #   ???
                i = 2

            counter = counter -1



    def process_cluster(self,clusters,start_id,generation,parent=0,prevpeople=[]):
        groupnumber = start_id
        for cluster in clusters:

            score,group = self.make_group(cluster["str_time"],cluster["key"])
            self.tree[groupnumber] = {"parent":parent,"group": group,"score":score,"generation":generation,"total_people":group["mentees"] + [group["mentor"]] + prevpeople}
            groupnumber = groupnumber + 1
        return groupnumber
    '''
    def match_unmatched(self,unmatched):
        # We still have some leftover people. Lets see if we can find them a home


        matched = []

        for um in unmatched:
            # Get all of the times that this person is free
            times = self.peopleHash[um]
            p_nodes = self.graph[self.key_hash(times[0]["key"])][times[0]["time"]]["PeopleAvailiable"]
            p_node = [p for p in p_nodes if p.email == um][0]
            killSwitch = False

            # For each of those times, check to see if there is a group that is meeting
            for t in times:
                if not killSwitch:
                    meeting_time = self.graph[self.key_hash(t["key"])][t["time"]]["meeting_time"]

                    for g in self.groups:
                        if g["time"] == meeting_time and g["key"] == t["key"] and not killSwitch:
                            g["mentees"].append(p_node)
                            killSwitch = True
                            matched.append(p_node)
                            break

        self.update(matched)
    '''



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
            isOpen = self.peopleHash[key].isOpen
            if isOpen:
                left_over_people.append(key)

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
        #score = score + len(self.groups) * 10

        # Get 10 points for each group with a mentor in it
        score = score + len([z for z in self.groups if z["mentor"] is not None]) * 10

        # Get points based on the size of the groups
        for z in self.groups:
            group_size = len(z["mentees"])
            penalty = min(group_size % self.group_size,self.group_size - group_size)
            score = score - penalty


        # Lose points for mentees that are left over
        score = score - len(self.find_unmatched_mentees())* 10


        return score









