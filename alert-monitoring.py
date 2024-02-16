

import mariadb
import math
from multiprocessing import Process
from multiprocessing import Manager
import time
import smtplib, ssl
from email.message import EmailMessage
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg



#Flags to check for common errors
SUCCESS = 0 #Data was queried from the MariaDB database as normal
NO_RECENT_DATA = 1 #Data was queried successfully, but isn't within 10 minutes from present
QUERY_FAILED = 2 #The code was unable to get data from the MariaDB for some reason (server down)

#Check whether rain rate is greater than 1.5 in/hr during the past 20 minutes
def checkRain(rain):
    if rain[-1] >= 1.5 and rain[-2] >= 1.5 or rain[-1] >= 3.0:
        return True
    return False

#Check whether moderate wind criteria have been reached
def checkWind(wind):
    if sum(wind)/len(wind) >= 26.0 or wind.sort()[math.floor(len(wind)/2)] >= 35.0:
        return True
    return False

    
#This function takes in the variable "station_name
#This is the name of the station database you want to check for an alert 
#(i.e. Mesoter7DB == Atlantic Station)
def monitor_station(station_name, return_dict):
    conn = mariadb.connect(
        user="jyoum",
        password="password",
        host="brewer.atmos.umd.edu",
        database=station_name)
    conn.autocommit = False   
    cur = conn.cursor()
    query = "SELECT dateTime, rainRate, windGust FROM {}.archive ORDER BY dateTime DESC LIMIT 30".format(station_name)
    cur.execute(query)
    alertFrequency = 60 #how frequent should the emails be sent? one per hour = 60, one per two hours = 120, etc.
    rainRate = [0 for i in range(0, int(alertFrequency/10))]
    windGust = [0 for i in range(0, int(alertFrequency/10))]
    dates = [0 for i in range(0, int(alertFrequency/10))]
    rainAlert = [False for i in range(0, int(alertFrequency/10))]
    windAlert = [False for i in range(0, int(alertFrequency/10))]
    #Store in easy python format
    for line in cur:
        dt = line[0]
        dates.pop(0)
        dates.append(dt)
        rainRate.pop(0)
        rainRate.append(line[1])
        windGust.pop(0)
        windGust.append(line[2])
        rainAlert.pop(0)
        rainAlert.append(False)
        windAlert.pop(0)
        windAlert.append(False)
    conn.close()

    if checkRain(rainRate) and True not in rainAlert and (datetime.now() - dt).total_seconds() < 600:
        port = 465
        password = "zgdf emij huka kkgf"

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login("allurations@gmail.com", password)

            sender_email = "allurations@gmail.com"
            receiver_email = "sirswagger21@gmail.com"
            message = """\
            Subject: Hi there

            The UMD campus is experiencing heavy rain. This could lead to flash flooding. Please exercise caution if going outside."""
            server.sendmail(sender_email, receiver_email, message)
        
        rainAlert[-1] = True


    if checkWind(windGust) and True not in rainAlert and (datetime.now() - dt).total_seconds() < 600:
        port = 465
        password = "Email password here"

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login("gmail name (e.g. hello@gmail.com)", password)

            sender_email = "my@gmail.com"
            receiver_email = "your@gmail.com"
            message = """\
            Subject: Hi there

            The UMD campus is experiencing strong winds. Please exercise caution if going outside."""
            server.sendmail(sender_email, receiver_email, message)
        
        windAlert[-1] = True



    print('{} Rain Rate Alert: {}'.format(station_name, checkRain(rainRate)))
    print('{} Wind Alert: {}'.format(station_name,checkWind(windGust)))
    return_dict[station_name] = [line[0], line[1], line[2], rainAlert[-1], windAlert[-1]]
    #return_dict will contain an array [datetime, rainRate at that dt, windGust at that dt, rainAlert at that dt, windAlert at that dt]

def main():
    #Spawn child processes to monitor each station over a set time interval
    #Wait for them to check if the alert should be triggered, reap the children, then sleep and repeat

    station_list = ['mesoterp7DB', 'mesoterp8DB', 'mesoterp9DB']
    while(True):
        manager = Manager()
        return_dict = manager.dict()
        jobs = []
        for i in range(len(station_list)):
            p = Process(target=monitor_station, args=(station_list[i], return_dict))
            jobs.append(p)
            p.start()
        
        for proc in jobs:
            proc.join()
        
        img = mpimg.imread('cmcm.jpg')
        imgplot = plt.imshow(img)
        plt.show()
        print(return_dict.values())
        print('Finished Monitoring')

        #send report
        time.sleep(600) #in seconds

    return 0

#Alrighty now I just need to set up the coding framework for monitoring
#Things I want ot monitor:
    #Rain rate
    #Wind speed (specifically 10-minute average gust?)

#What will the program do?
    #Initialize the mariadb connection
    #Every X interval in time, it will pull the latest data from a station,
    #then process the output into nice python objects (like an array or list)
        #It needs to be able to handle the data not being completely up to date
        #Meaning, don't do anything if the latest data is not within the last 10 minutes from current time
    #then it will run code to determine if an alert needs to be sent out
    
    #If true, send emails to everyone in email list (need to configure a subscribe AND unsibscribe button)
    #Add the alert to another MariaDB database we'll call alerts.
    #This will have a column for "station" and a column for alert type
    #Make sure it checks to see if an alert has already been sent out, you don't want to spam people's emails!
    #If false, do nothing!
    #Wait X time has past and repeat.

    #Additionally, it would be nice to include some error handling
    #But that's something extra we want to try to implement later.

if __name__== "__main__":
    main()

