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
from io import StringIO
import re

class Node:
    def __init__(self,email,isMentor,isOpen):
        self.email = email
        self.isMentor = isMentor
        self.isOpen = isOpen
        self.feature_dict = dict()
    def toString(self):
        print(self.email,self.isMentor,self.isOpen)
    def __str__(self):
        return "%s,%s,%s" % (self.email,self.isMentor,self.isOpen)

class Graph:
    def __init__(self,filename,meeting_duration=75,weekend_meetings=False,earliest_time="8:00AM",latest_time="5:00PM",sample_size=25,group_size=None,time_delta=15,contents=None):
        # We need to construct a graphical matrix representation for the possible times and
        #  days that there could possbily be meetings for.
        self.time_format = "%I:%M%p"

        self.sample_size = sample_size

        self.group_split_size = 10

        # Set default score breakdown
        self.uw = .45
        self.gsw = .15
        self.ngw = .25
        self.fw = .15


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
        self.weekend_meetings = weekend_meetings
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
            meeting_time = meeting_time + timedelta(minutes=time_delta)

        # After we have constructed the graph object, lets read in all of the data to the graph
        self.peopleHash = self.readfile(filename,contents=contents)
        if group_size != None:
            self.group_size = group_size

        # For some reason weekend meetings are appearing so delete them
        if not weekend_meetings:
            del self.graph["S"]
            del self.graph["N"]

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


    # This function cleans up a strings so that they work with the program
    def regexClean(self,value):
        value = re.sub(":\([0-9]\):",":0\1:",value)
        value = re.sub("-\([0-9]\):","-0\1::",value)
        value = re.sub("Times.*","Times",value)
        value = value.replace('\r', '')
        return value

    def firstrow(self,row):
        feature_dict = dict()
        is_first = False
        counter = 0

        for r in row:
            if r is not None:
                feature_dict[r.lower().strip()] = counter
                counter  = counter + 1

        # Check to make sure that times is the last field in the header row. Since
        #  there can be more than one time, this must be the case
        assert(feature_dict["times"] == counter - 1)
        return feature_dict, is_first


    def dataRow(self,feature_dict,row):
        # The first element of the table should be the email address of the person

        email = row[feature_dict["email"]]

        # The second row should be if they are a mentor or not
        self.num_mentors = self.num_mentors + int(row[feature_dict["ismentor"]])
        isMentor = int(row[feature_dict["ismentor"]]) == 1

        # Finally check to see if there are any additional features that we need to be aware of
        node = Node(email,isMentor,True)

        key_list =  [key for key in feature_dict.keys() if key != "email" and key != "times" and key != "ismentor"]

        for key in key_list:
            node.feature_dict[key] = int(row[feature_dict[key]])  == 1
        self.peopleHash[email] = node

        # The final rows should be the times that the person is availiable
        for z in row[feature_dict["times"]:]:
            # First get the day
            if z is not None:
                sp = z.split(":")

                if len(sp) > 1:
                    day = sp[0]

                    # Now get the times
                    times = ":".join(sp[1:]).split("-")
                    try:
                        beginning = datetime.strptime(times[0], self.time_format)
                        ending = datetime.strptime(times[1], self.time_format)
                    except:
                        print("Error: Improper time format",row)
                    # Bad news is that this is a range, so we have to check to see which durations we can fit in
                    for g in range(0,len(self.graph[self.key_hash(day)])):
                        ti = self.graph[self.key_hash(day)][g]
                        if ti["beginning"] >= beginning and ti["ending"] <= ending and self.weekend_check(day):
                            ti["PeopleAvailiable"].append(node)
                            assert(node == ti["PeopleAvailiable"][len(ti["PeopleAvailiable"])-1])

    def readfile(self,filename,contents=None):
        self.peopleHash = {}
        self.num_mentors = 0
        is_first = True

        spamreader = contents

        # If we have the contents of the file instead of the filename, convert file to something we can use
        if contents is  None:
            csvfile = open(filename, newline='')
            spamreader = csvfile.read()
            csvfile.close()

        # Lets clean up the input file using some regex so that we can eliminate some common errors
        spamreader = self.regexClean(spamreader)

        spamreader = spamreader.split()

        feature_dict = None
        for row in spamreader:
            row = row.split(",")
            if is_first:
                feature_dict, is_first = self.firstrow(row)
            else:
                # If this is an empty row, we out boiz
                if len(row)< len(feature_dict.keys()):
                    break
                else:
                    self.dataRow(feature_dict,row)

        # Calculate the target group size based on the mentor mentee ratio
        self.group_size = int((len(self.peopleHash.keys()) - self.num_mentors)/self.num_mentors) + 1

        return self.peopleHash

    def weekend_check(self,day):
        good = True
        if self.weekend_meetings is False and (self.key_hash(day) == "s" or self.key_hash(day) == "n"):
            good = False
        return good


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
            if people != "None":
                people.isOpen = value_change


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
        mentees = [n for n in obj["PeopleAvailiable"] if n.isMentor == False and n.isOpen == True]

        # Shuffle up the mentees so that we get a better version
        random.shuffle(mentees)
        random.shuffle(mentors)
        mentees_list = [mentees[0:self.group_size]]

        # We want to experiment with differing group sizes to get a better score

        # Lets pick group_split_size number of samples
        for i in range(0,self.group_split_size):
            end_size = int(self.group_size * 1.5)
            if end_size > len(mentees):
                end_size = len(mentees)
            mentees_list = mentees_list + [random.sample(mentees,random.randint(0,end_size))]

        #mentees_list = mentees_list + [mentees[0:min(len(mentees),int(self.group_size*1.5))]]
        #mentees_list = mentees_list + [mentees[0:int(self.group_size*.5)]]


        best_group = None
        best_score = float('-inf')

        for me in mentees_list:
            mentor = [Node("None",True,False)]
            peoplelist = me
            if len(mentors) > 0:
                mentor = mentors[0:self.mentors_per_group]
                peoplelist = peoplelist + mentor

            group = {"key":key,"time":ti,"mentor":mentor,"mentees":me}

            # Add to the group list for now
            self.groups.append(group)
            self.update(peoplelist=peoplelist,value_change=False)

            # Calculate score
            score = self.calculate_score()

            # Check to see if the score is better than our best
            if best_score < score or best_group == None:
                best_score = score
                best_group = group

            # Now remove from group list so that we dont contaminate
            self.groups = self.groups[0:len(self.groups) -1]
            self.update(peoplelist=peoplelist,value_change=True)

        # Lets add in the score for our special features to the group object. Just so that we can save it
        if len(best_group["mentees"]) > 0:
            feature_keys = best_group["mentees"][0].feature_dict
            if len(feature_keys) > 0:
                for key in feature_keys:
                    feature_score =  sum([m.feature_dict[key] for m in best_group["mentees"]])
                    #feature_score = feature_score + best_group["mentor"].feature_dict[key]
                    feature_score = feature_score/(len(best_group["mentees"]) + 1)
                    best_group[key] = feature_score

        # Finally return the score
        return best_score,best_group

    def test(self,people=[]):
        k = self.peopleHash.keys()
        a = [p for p in k if self.peopleHash[p].isOpen == False]
        assert(len(people) ==len(a))


    def write_graph(self):
        for g in self.graph.keys():
            l = self.graph[g]
            for i in l:
                if len(i["PeopleAvailiable"]) > 0:
                    p = [pp.email for pp in i["PeopleAvailiable"] if pp.isOpen==True]
                    print(g,i["meeting_time"]," ".join(p))

    def run(self,generation_cap=500,mentors_per_group=1,web=False):
        print(self.uw,self.gsw,self.ngw,self.fw )
        # Lets use a greedy approach at the beginning in order to find groups. We will look for the largest clusters
        #  in the graph and remove them.
        # First, we need to define a condition to kill the learning. We want this condition to happen when we hit an
        # acceptable score.
        self.mentors_per_group = mentors_per_group

        # Group size has to change if we have multiple mentors per group
        self.group_size = self.group_size * self.mentors_per_group

        # Create an array to hold the groups that we created
        self.groups = []


        # Next define a kill switch that will activate if the scores don't seem to be improving
        killSwitch = False

        generation = 0

        total_people = len(self.peopleHash.keys())

        print("Running optomization targeting a group size of %d... This might take a while" % self.group_size)

        self.tree = dict()
        groupnumber = 0

        while not killSwitch and generation < generation_cap:
            # We are trying a generation based approach
            # To do this, we first need to find parents from the previous generation
            ids = [e for e in self.tree.keys() if self.tree[e]["generation"]+1 ==generation]


            # In order to prevent exponential running time, we need to cap the number of ids that we explore
            #  Lets randomly sample some ideas.
            ids = random.sample(ids,min(len(ids),self.sample_size))


            # If we have no ids that means that we are in the first generation.
            if generation == 0:
                max_people, clusters = self.find_target_size_clusters()
                clusters = random.sample(clusters,min(len(clusters),self.sample_size))

                groupnumber = self.process_cluster(clusters,groupnumber,generation,parent=-1)
            else:
                # Otherwise, we have to loop through all of the groups from the previous generation
                # and create the next generation based on that.

                for id in ids:
                    grp = self.tree[id]

                    # Lets first update the graph, so that we are up to date with previous versions
                    z = list(set(grp["total_people"]))

                    self.update(peoplelist=grp["total_people"])

                    self.groups, _ = self.get_group(id)

                    # Now lets find the clusters that we are looking for
                    max_people, clusters = self.find_target_size_clusters()

                    # if we can't find anything with the target size, lets just try to make a few more groups
                    if len(clusters) == 0:
                        max_people,clusters = self.find_largest_cluster()

                    clusters = random.sample(clusters,min(len(clusters),20))

                    # If we still can't find anything, this id is donzo
                    if len(clusters) != 0:
                        killSwitch = False
                        # Create new nodes for each cluster
                        groupnumber = self.process_cluster(clusters,groupnumber,generation,parent=id,prevpeople=grp["total_people"])



                    # Un-update so we don't contaminate results
                    self.update(peoplelist=grp["total_people"],value_change=True)
                if len(ids) ==0:
                    killSwitch = True


            # In order to prevent exponental increase, we need to prune the tree after each generation
            self.prune(generation=generation)

            if generation % 10 == 0:
                print("Completed generation %s" % generation)

            generation = generation +1

        # Find the highest scoring family and write the results
        id,groups,scores = self.get_highest()

        # Get the group so we can update everything
        final_group = self.tree[id]
        self.update(peoplelist=final_group["total_people"])

        print("Best Group found in generation:%s" % final_group["generation"])
        final_groups,unmatched = self.output(groups,scores)
        if not web:
            self.write_results(final_groups,unmatched)

        return scores,final_groups,unmatched
    def print_group(self,group):
        keys = group.keys()
        badkeys = ["total_people","mentees","mentor"]
        for k in keys:
            if k not in badkeys:
                print(group[k])
    def get_highest(self):
        best_score = float('-inf')
        best_group_id = 0
        for key in self.tree.keys():
            if self.tree[key]["score"] > best_score:
                best_group_id = key
                best_score =self.tree[key]["score"]
        # Also since this is the end, lets update the graph
        groups,scores = self.get_group(best_group_id,printtree=True)
        return best_group_id,groups,scores


    def get_group(self,id,printtree=False):
        groups = []
        scores = []
        best_group = self.tree[id]
        while best_group["parent"] > -1:

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
                scores = [self.tree[e]["score"] for e in self.tree.keys() if self.tree[e]["generation"] == generation]
                if len(scores) > 0:
                    median_score = statistics.median(scores)

                    # Lets remove everything from this generation that falls below the median
                    ids = [e for e in self.tree.keys() if self.tree[e]["generation"] == generation and self.tree[e]["score"] < median_score]
                    for i in ids:
                        del self.tree[i]
            counter = counter -1



    def process_cluster(self,clusters,start_id,generation,parent=0,prevpeople=[]):
        groupnumber = start_id
        for cluster in clusters:

            score,group = self.make_group(cluster["str_time"],cluster["key"])
            self.tree[groupnumber] = {"parent":parent,"group": group,"score":score,"generation":generation,"total_people":group["mentees"] + group["mentor"] + prevpeople}
            groupnumber = groupnumber + 1

        return groupnumber


    def output(self,groups,scores):
        out_tupes = []
        for g in groups:
            mentee_list = " ".join([z.email for z in g["mentees"]])
            mentor_list = " ".join([z.email for z in g["mentor"]])
            # Add all of the additonal features
            keys = g.keys()
            badkeys = ["key","time","mentor","mentees"]
            features = ""
            for k in keys:
                if k not in badkeys:
                    if float(g[k]) > .85:
                        features = features +" "+ k
            out_tupes.append((g["key"],g["time"],mentor_list,mentee_list,features))
        unmatched = self.find_unmatched_mentees()
        return out_tupes,unmatched

    def write_results(self,final_groups,unmatched):
        f = open("groups.csv","w")
        f.write("Day,Time,Mentor,Mentees,AdditionalFeatures\n")
        for o in final_groups:
            f.write("%s,%s,%s,%s,%s\n" % o)
        f.close()
        f = open("unmatched.csv","w")
        f.write("Email\n")
        for u in unmatched:
            f.write(u + "\n")
        f.close()

    def find_unmatched_mentees(self):
        left_over_people = []
        for key in self.peopleHash.keys():
            isOpen = self.peopleHash[key].isOpen
            if isOpen == True:
                left_over_people.append(key)

        return list(set(left_over_people))


    def set_score_args(self,uw,gsw,ngw,fw):
        # CHeck to make sure that the total of the arguments equals 1
        if uw + gsw + ngw + fw != 1:
            print("WARNING: Score arguments do not equal 1. Using default arguments")
        else:
            self.uw = uw
            self.gsw = gsw
            self.ngw = ngw
            self.fw = fw



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

        # Calculate the score for the number of groups ( observed/expected)
        num_groups_score = (len(self.groups)/(self.num_mentors/self.mentors_per_group)) * 100
        if num_groups_score > 100:
         num_groups_score = 100 - (num_groups_score % 100)

        total_group_size_score = 0
        feature_score_total = 0

        # Get points based on the size of the groups
        for z in self.groups:
            group_size = len(z["mentees"])
            group_score_size = (group_size/self.group_size) * 100
            if group_score_size > 100:
                group_score_size = 100 - (group_score_size - 100)
            total_group_size_score = total_group_size_score + group_score_size




            # Lets check the additional features to see if we were able to account for those
            #  since they are additional, lets add points instead of substracting them
            if len(z["mentees"]) > 0:
                feature_keys = z["mentees"][0].feature_dict
                if len(feature_keys) > 0:
                    total_feature_score = 0
                    for key in feature_keys:

                        feature_score =  sum([m.feature_dict[key] for m in z["mentees"]])
                        # TODO: Fix this
                        #feature_score = feature_score + z["mentor"].feature_dict[key]
                        feature_score = feature_score/(len(z["mentees"]) )#+ 1)
                        total_feature_score = total_feature_score + feature_score
                    # Get the average score for all of the features
                    total_feature_score = feature_score/len(feature_keys)

                    # Here's where things get tricky. We want the feature score to be bimodal (scores closer to 0 and 1 should be
                    #  higher than scores closer to .5)



                    feature_score_total = feature_score_total + (abs(.5 - total_feature_score)  * 100)
                else:
                    feature_score_total =  feature_score_total + 100

        total_group_size_score = total_group_size_score/len(self.groups)
        feature_score_total = feature_score_total/len(self.groups)

        unmatched_score = (1 - len(self.find_unmatched_mentees())/len(self.peopleHash.keys())) * 100

        # Calculate the score based on the 4 categories we have
        #  - unmatched people
        #  - feature score
        #  - num groups
        #  - group size
        assert(self.uw + self.gsw + self.ngw +  self.fw == 1)
        # The most important thing is that as many of the people as possible get matched to a group
        #   Thus, the unmatched mentee score weight should be high
        assert(unmatched_score < 101)
        score = unmatched_score * self.uw

        # Second most important is group size. We want things to be as balanced as possible
        assert(total_group_size_score < 101)
        score = score + total_group_size_score * self.gsw

        # Third most important is the number of groups
        assert(num_groups_score < 101)
        score = score + num_groups_score * self.ngw


        # Finally, we the feature score needs to be added
        assert(feature_score_total < 101)
        score = score + feature_score_total * self.fw

        # The max score that a group can get is 100

        #print(unmatched_score,total_group_size_score,num_groups_score,feature_score_total)


        return score


def run_graph(contents, meeting_duration,sample_size,group_size, earliest_time,latest_time,unmatched,groupsize,num_group,features,web,mentors_per_group):
    g = Graph("placeholder.txt", contents=contents,meeting_duration=meeting_duration,sample_size=sample_size,group_size=group_size, earliest_time=earliest_time,latest_time=latest_time)
    g.set_score_args(unmatched,groupsize,num_group,features)
    return g.run(web=web,mentors_per_group=mentors_per_group)






