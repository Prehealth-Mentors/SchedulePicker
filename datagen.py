# Name: datagen.py
# Author: Sam Shenoi
# Description: This file generates some random test data in order to test the effectiveness of
#  the SchedulePicker system. Data is written out to "in.txt" in the sample data folder.
#  This behavior can be changed provided that the proper arguments are passed in.
import random
import string

class DataGen:
    def __init__(self):
        self.letters = string.ascii_lowercase

    def create_data(self,num_mentees=50,num_mentors=10):
        f = open("sampledata/in.txt","w")
        for i in range(0,num_mentees):
            email = ''.join(random.choice(self.letters) for i in range(5)) + "@baylor.edu"
            isMentor = 0
            







