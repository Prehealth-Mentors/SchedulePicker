# Name: datagen.py
# Author: Sam Shenoi
# Description: This file generates some random test data in order to test the effectiveness of
#  the SchedulePicker system. Data is written out to "in.txt" in the sample data folder.
#  This behavior can be changed provided that the proper arguments are passed in.
import random
import string
from datetime import datetime, date,timedelta
import csv

class DataGen:
    def __init__(self):
        self.letters = string.ascii_lowercase
        self.time_format = "%H:%M"

    def switcher(self,i):
        days = {
            1:"Monday",
            2:"T",
            3:"W",
            4:"R",
            5:"Friday",
            6:"Saturday",
            7:"N"
        }
        return days[i]

    def format_real_data(self,mentor_file,mentee_file):
        # Use this function to take data from the google form and format it into something we can use
        first_row = True
        csv_dict = dict()
        people = []
        with open(mentor_file, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in spamreader:
                if first_row:
                    counter = 0
                    for r in row:
                        csv_dict[r] = counter
                        counter = counter + 1
                    first_row = False
                else:
                    email = row[csv_dict['Email']]
                    if email != " " and email != "":
                        r = row[csv_dict["Please indicate whether you are a transfer student or not"] + 2:]
                        time_str = ",".join(r)
                        time_str = time_str.replace(" ", "")
                        people.append({"email":email,"time_str":time_str,"isMentor":1})
        first_row = True
        csv_dict = dict()
        with open(mentee_file, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in spamreader:
                if first_row:
                    counter = 0
                    for r in row:
                        csv_dict[r] = counter
                        counter = counter + 1
                    first_row = False

                else:
                    if len(row) > 0:
                        name = row[csv_dict['name']]
                        try:
                            email = row[csv_dict['Email']]
                        except:
                            email = name

                        try:
                            r = row[16:len(row) -4]

                        except:
                            r = ""
                        if r != "":

                            time_str = ",".join(r)
                            time_str = time_str.replace(" ", "")
                            people.append({"email":email,"time_str":time_str,"isMentor":0})

        f = open("realdata/in.txt","w")
        f.write("Name, isMentor, Times\n")
        for p in people:
            f.write("%s,%s,%s\n" % (p["email"],p["isMentor"],p["time_str"]))
        f.close()






    def create_times(self,num_days):
        added = []
        for n in range(0,num_days):
            day = self.switcher(random.randint(1,7))

            start_hour = random.randint(0,23)
            start_minute = random.randint(0,58)

            end_hour = random.randint(start_hour,23)
            end_minute = random.randint(start_minute + 1,59)


            # Check to make sure that we aren't interfering with another range
            new_obj = {"start":datetime.strptime("%s:%s" % (start_hour,start_minute),self.time_format ),
                        "end":datetime.strptime("%s:%s" % (end_hour,end_minute), self.time_format),
                        "day":day
                        }
            no_conflict = True
            for obj in added:
                if obj["day"] == new_obj["day"]:
                    if obj["start"] <= new_obj["end"] or new_obj["start"] <= obj["end"]:
                        no_conflict = False


            if no_conflict:
                added.append(new_obj)
        return added




    def create_fake_data(self,num_mentees=50,num_mentors=10):

        f = open("sampledata/in.txt","w")
        f.write("Name, isMentor, Times\n")

        for i in range(0,num_mentees + num_mentors):

            isMentor = 0
            email = ""

            if i > num_mentees - 1:
                isMentor = 1
                mentor_number = i % num_mentees
                email = "mentor%d@baylor.edu" % mentor_number
            else:
                email = "mentee%d@baylor.edu" % i


            num_days = random.randint(1,7)
            times = self.create_times(num_days)

            f.write("%s,%s," % (email,isMentor))

            for a in times:
                f.write("%s:%s-%s," % (a["day"],datetime.strftime(a["start"],"%I:%M%p"),datetime.strftime(a["end"],"%I:%M%p")))
            f.write("\n")

        f.close()

if __name__== "__main__":

    dg = DataGen()
    #dg.format_real_data("realdata/mentors.csv","realdata/mentees.csv")
    dg.create_fake_data()

























