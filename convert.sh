#/bin/bash

# Author: Sam Shenoi
# Description: This script is a quick fix script for converting files into the proper format for the program
#  To run this file, use the following commands on the command line
# ##############
#
#  chmod u+x convert.sh
#  ./convert.sh <your filename here>
#############################



sed 's/:\([0-9]\):/:0\1:/g' $1 > temp.csv
sed 's/-\([0-9]\):/-0\1:/g' temp.csv > temp2.csv
# Remove the pesky \r bc microsoft sucks
sed 's/\r$//' temp2.csv > temp.csv
sed 's/Times.*/Times/' temp.csv > finalform.csv
