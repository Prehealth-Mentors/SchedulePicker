# Author: Sam Shenoi
# Description: This file sends out an email to the matched mentors and mentees
#   notifying them about their group assignment. This feature isn't enabled by default
#   but can be turned on by specifying the correct flag.
# Based on: https://stackabuse.com/how-to-send-emails-with-gmail-using-python/

# Imports
import smtplib

class Emailer:
    def __init__(self):
        # Open the config file and load the username and password
        try:
            f = open("config2.txt","r")
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

        try:
            self.server = smtplib.SMTP('smtp.gmail.com', 587)
            self.server.ehlo()
            self.server.starttls()
            self.server.login(gmail_user, gmail_password)
        except:
            print('Something went wrong...')

    def template_string(self,fro,to,mentor_name,mentee_names,day,time):
        email_text = """\
            From: %s
            To: %s
            Subject: PHP Peer Group Assignments

            Hi,

            This email has been sent to inform you that you have been matched to a
            PHP Peer Group for this semester.

            Mentor: %s
            Mentees: %s
            Day: %s
            Time: %s

            If you have any questions, please reach out to the PHP TAs.

            Thanks,

            The PreHealth Mentor Matching Team


        """ % (fro,",".join(to),mentor_name,",".join(mentee_names),day,time)
        return email_text

    def send_email(self,sent_from,to):
        self.server.sendmail(sent_from, to, "")






if __name__ == "__main___":
    e = Emailer()
    print("Still in development. Please check back later!")
