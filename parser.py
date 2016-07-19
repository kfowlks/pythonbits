#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""SAP Trace log Coalesce Tool

Author: Kevin Fowlks
Date:   07/15/2016

This program takes a single argument (directory path) and combines the data from multiple servers into a single stream. The
program also outputs a limited set of data columns that can be captured from stdio and piped into standard unix tools for futher processing. 

Sample Output line

"2016 07 15 09:06:41:754"~"Error"~"exception for queue RTMF_POST_QUEUE[EXCEPTION]javax.jms.JMSSecurityException: User: russkyle has not permission: vpName: default, type: administration, action: create_queue, destination: ALLat com.sap.jms.server.sc.UMESecurityProvider.checkPermission(UMESecurityProvider.java:223)"~"ebsprd210a1"~"russkyle"

Output Column(s)

"Timestamp", "Log Level", "Error Message String", "server name", [Username if found in error message string]

Directory Structure:

/logs/<server name with trace files> e.g. C:\prod-logs\ebsprd210a1

Note: Files from /usr/sap/PP1/J51/j2ee/cluster/server0/log and /usr/sap/PP1/J51/j2ee/cluster/server1/log 
       should be combined into the same directory e.g. C:\prod-logs\ebsprd210a1

Usage:
    The program can be run as shown below:
        $ python parser.py <path to logs>

    Or

    $ python parser.py /cygdrive/c/prod-logs/ | sort -t~ -k1M -k1.3 -k1.4 -k4
"""

import sys
import os
import io 
import csv
import codecs

UTF8Writer = codecs.getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)

def prepareFileCollection(inpath):
    logdict = {}
    
    for root, dirs, files in os.walk(inpath):
        path = root.split('/')
        #print((len(path) - 1) * '---', os.path . basename(root))
        #print((len(path) - 1) * '---', os.path . basename(root))
        filelist = []
        
        for file in files:
            servername = path[3]
            if os.path.splitext(file)[1] == ".trc":
                #print(os.path.join(root,file))
                #print(path[2] + " --> " +  file)
                #print(len(path) * '---',  name(file))
                
                filelist.append(os.path.join(root,file))

            logdict[servername] = filelist
            #filelist = []
                
    return logdict      

# Gather our code in a main() function
def main():

    inputLogPath = sys.argv[1]
    logFilesDict = prepareFileCollection(inputLogPath)

    for servername, filelist in logFilesDict.items():
        for filename in filelist:
            #print "I got %r" % filename
            f = io.open(filename, "r", encoding="utf-8")

            try:
                eventfound = False
                event_cnt = 0
                event_line_cnt = 0
                event_msg = ""
                event_line_cnt = 0

                for line in f.readlines():

                    if not line.startswith("#"):
                        
                        if eventfound is True and event_line_cnt > 0:
                            event_msg = event_msg + " " + line.strip()
                            #print line
                            event_cnt = event_cnt + 1
                            
                            if(event_cnt > 3 ):
                                
                                loc = event_msg.find("User:")

                                if loc > 0:
                                    event_opt_user = event_msg[loc:].split(' ')[1].strip()
                                else:
                                    event_opt_user = 'N/A'

                                #print "USER -> {0}".format(event_opt_user)

                                #print event_line_cnt
                                try:
                                    print '"{0}"~"{1}"~"{2}"~"{3}"~"{4}"'.format(event_ts,event_level,event_msg,servername,event_opt_user)
                                except UnicodeEncodeError, e:
                                    print ""

                                #print event_level
                                #print event_msg
                                event_cnt      = 0
                                event_line_cnt = 0
                                event_msg      = ""
                                eventfound     = False
                                event_line_cnt = 0
                                event_ts    = ""
                                event_level = ""
                                event_cat   = ""
                                #break

                        continue
                    
                    #print len(line)
                    if line.startswith("#") and  len(line) < 3:
                       continue

                    eventfound = True
                    event_line_cnt = event_line_cnt + 1
       
                    #print line
                    if event_line_cnt == 1:
                        event_ts = line.split("#")[2].strip()
                        event_level = line.split("#")[4].strip()
                    else:
                        event_cat = line.split("#")[1].strip()

            finally:
                f.close()

if __name__ == '__main__':
    main()
