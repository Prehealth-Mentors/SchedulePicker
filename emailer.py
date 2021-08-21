# Author: Sam Shenoi
# Description: This file sends out an email to the matched mentors and mentees
#   notifying them about their group assignment. This feature isn't enabled by default
#   but can be turned on by specifying the correct flag.
# Based on: https://stackabuse.com/how-to-send-emails-with-gmail-using-python/

# Imports
import smtplib
from email.message import EmailMessage
import csv
import argparse


class Emailer:
    def __init__(self):

        # Open the config file and load the username and password
        try:
            f = open("config.txt","r")
        except:
            f = open("config.txt",'w')
            f.write("gmail_username= \ngmail_password= \n")
            f.close()
            print("We couldn't find a config file, so we created one for you. Please fill it out")
            exit()
        config_data = f.read()
        config_data = config_data.split("\n")
        assert(len(config_data) > 2)
        gmail_username = config_data[0].split("=")[1]
        gmail_password = config_data[1].split("=")[1]
        self.username = gmail_username


        try:
            self.server = smtplib.SMTP('smtp.gmail.com', 587)
            self.server.ehlo()
            self.server.starttls()
            self.server.login(gmail_username, gmail_password)

        except Exception as e:
            print(e)


    def template_string(self,to,mentor_name,mentee_names,day,time):
        msg = EmailMessage()

        content = """\
            Hi,

            This email has been sent to inform you that you have been matched to a
            PHP Peer Group for this semester.

            Mentor: %s
            Mentees: %s
            Day: %s
            Time: %s

            If you have any questions, please reach out to the PHP TAs. Please ignore this message if it is a duplicate.

            Thanks,

            The PreHealth Mentor Matching Team
        """ % (mentor_name,",".join(mentee_names),day,time)
        msg.set_content(content)
        msg["Subject"] = "Prehealth Peer Groups"
        msg["From"] = self.username
        msg["To"] = ",".join(to)
        return msg

    def close(self):
        self.server.quit()

    def read_file(self,filename):
        # This program defaults to reading the groups.csv file.
        with open(filename, newline='') as csvfile:
            firstRow = True
            data_dicts = []
            header = dict()
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in spamreader:
                if firstRow:
                    for i in range(0,len(row)):
                        header[i] = row[i].strip()
                    firstRow = False

                else:
                    group_dict = dict()
                    for i in range(0,len(row)):
                        if i in header.keys():
                            group_dict[header[i]] = row[i]
                    data_dicts.append(group_dict)
        return data_dicts





    def send_email(self,filename):
        data_dicts = self.read_file(filename)

        for d in data_dicts:
            to = d["Mentor"] + " " + d["Mentees"]
            to = to.split(" ")

            mentor_name = d["Mentor"].split(" ")
            mentor_name = ",".join([e.split("@")[0] for e in mentor_name])


            mentees = d["Mentees"].split(" ")
            mentees = [e.split("@")[0] for e in mentees]

            msg = self.template_string(to,mentor_name,mentees,d["Day"],d["Time"])

            self.server.send_message(msg)



if __name__ =="__main__":
    parser = argparse.ArgumentParser(description='Process command line options')
    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument('--input_file', required=True, metavar='-i', nargs='+', help='the path to the input file')

    args = parser.parse_args()



    e = Emailer()
    e.send_email(args.input_file[0])
    e.close()


