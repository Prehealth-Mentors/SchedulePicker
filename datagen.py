# Name: datagen.py
# Author: Sam Shenoi
# Description: This file generates some random test data in order to test the effectiveness of
#  the SchedulePicker system. Data is written out to "in.txt" in the sample data folder.
#  This behavior can be changed provided that the proper arguments are passed in.
import random
import string
from datetime import datetime, date,timedelta

class DataGen:
    def __init__(self):
        self.letters = string.ascii_lowercase
        self.time_format = "%H:%M"

    def switcher(self,i):
        days = {
            1:"M",
            2:"T",
            3:"W",
            4:"R",
            5:"F",
            6:"S",
            7:"N"
        }
        return days[i]

    def format_real_data(self):
        # Use this function to take data from the google form and format it into something we can use
        print("HI")

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
            email = ''.join(random.choice(self.letters) for i in range(5)) + "@baylor.edu"
            isMentor = 0
            if i > num_mentees - 1:
                isMentor = 1

            num_days = random.randint(1,7)
            times = self.create_times(num_days)

            f.write("%s,%s," % (email,isMentor))

            for a in times:
                f.write("%s:%s-%s," % (a["day"],datetime.strftime(a["start"],"%I:%M%p"),datetime.strftime(a["end"],"%I:%M%p")))
            f.write("\n")

        f.close()

if __name__== "__main__":

    dg = DataGen()
    dg.create_fake_data(num_mentees=5,num_mentors=1)

























