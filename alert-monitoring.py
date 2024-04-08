import mariadb
import math
from multiprocessing import Process
from multiprocessing import Manager
import time
import smtplib, ssl
import io
from email.encoders import encode_base64
from email.message import EmailMessage
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.utils import make_msgid
import mimetypes
from datetime import datetime
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import Circle



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

    print('{} Rain Rate Alert: {}'.format(station_name, checkRain(rainRate)))
    print('{} Wind Alert: {}'.format(station_name,checkWind(windGust)))
    return_dict[station_name] = [line[0], line[1], line[2], rainAlert, windAlert]
    #return_dict will contain an array [datetime, rainRate at that dt, windGust at that dt, rainAlert at that dt, windAlert at that dt]

def createGraphic(rain, wind):
    img = mpimg.imread('cmcm.jpg')
    imgplot = plt.imshow(img)
    

    plt.gca().add_patch(plt.Circle((0, 0), 0, color='lightgreen'))
    plt.gca().add_patch(plt.Circle((0, 0), 0, color='r'))
    plt.gca().add_patch(plt.Circle((0, 0), 0, color='b'))

    colors = []
    for i in range(0, len(rain)):
        if rain[i] == False and wind[i] == False:
            colors.append('springgreen')
        elif rain[i] == True and wind[i] == False:
            colors.append('lightblue')
        elif rain[i] == False and wind[i] == True:
            colors.append('lightcoral')
        #TBD: when both rain AND wind are triggered


    #atlantic
    j = 0
    plt.gca().add_patch(plt.Circle((920, 590), 40, facecolor=colors[j], edgecolor='black'))
    t1 = plt.text(920, 540, "Atlantic Building", fontweight='extra bold', fontsize=10, ha='center')
    t1.set_bbox(dict(facecolor=colors[j], alpha=1, edgecolor='black'))

    #williams
    j = 1
    plt.gca().add_patch(plt.Circle((1390, 610), 40, facecolor=colors[j], edgecolor='black'))
    t2 = plt.text(1390, 560, "AV Williams Building", fontweight='extra bold', fontsize=10, ha='center')
    t2.set_bbox(dict(facecolor=colors[j], alpha=1, edgecolor='black'))

    #golf
    j = 2
    plt.gca().add_patch(plt.Circle((50, 630), 40, facecolor=colors[j], edgecolor='black'))
    t3 = plt.text(70, 590, "Golf Course", fontweight='extra bold', fontsize=10)
    t3.set_bbox(dict(facecolor=colors[j], alpha=1, edgecolor='black'))

    #vmh
    j = 3
    plt.gca().add_patch(plt.Circle((620, 1340), 40, facecolor=colors[j], edgecolor='black'))
    t4 = plt.text(620, 1290, "Van Munching Hall", fontweight='extra bold', fontsize=10, ha='center')
    t4.set_bbox(dict(facecolor=colors[j], alpha=1, edgecolor='black'))

    #chem
    j = 4
    plt.gca().add_patch(plt.Circle((1150, 730), 40, facecolor=colors[j], edgecolor='black'))
    t5 = plt.text(1150, 680, "Chemistry Building", fontweight='extra bold', fontsize=10, ha='center')
    t5.set_bbox(dict(facecolor=colors[j], alpha=1, edgecolor='black'))
    
    plt.legend(["No recent alerts", "Recent rain alert", "Recent wind alert"], fontsize=10)

    fig = plt.gcf()
    fig.set_size_inches(8, 8)
    plt.savefig('test.png', bbox_inches='tight')
    return 0

def generateEmail(rain, wind):
    k = 0
    if True in rain and True not in wind:
        k = 0
    elif True in wind and True not in rain:
        k = 1
    elif True in rain and True in wind:
        k = 2
    else:
        return 0
    
    port = 465
    password = "zgdf emij huka kkgf"
    context = ssl.create_default_context()
    sender_email = "allurations@gmail.com"
    receiver_email = ["sirswagger21@gmail.com", "Jasony2025@gmail.com"]

    subjectMessages = ["Rain Alert: Exercise Caution", "Wind Alert: Exercise Caution", "Rain and Wind Alert: Exercise Caution"]
    subject = subjectMessages[k]

    message = EmailMessage()
    message['Subject'] = subject
    message['From'] = sender_email
    message['To'] = ", ".join(receiver_email)
    message.set_content("")

    bodyMessages = [
        """\
        <html>
            <body>
                <p style="font-size:18px;">
                Hello, <br> <br>
                The UMD campus is currently experiencing heavy rain. This could lead to flash flooding. Please exercise caution if going outside. <br> <br>
                Sincerely, <br>
                Mesoterps
                </p>
                <p style="font-size:9px;">
                DISCLAIMER: This is an UNOFFICIAL alert from students at the Department of Atmospheric and Oceanic Science. For official guidance, please consult the National Weather Service.
                </p>
                <img src="cid:{image_cid}">
            </body>
        </html>
        """,
        """\
        <html>
            <body>
                <p style="font-size:18px;">
                Hello, <br> <br>
                The UMD campus is currently experiencing strong winds. This could lead to downed trees and wind damages. Please exercise caution if going outside. <br> <br>
                Sincerely, <br>
                Mesoterps
                </p>
                <p style="font-size:9px;">
                DISCLAIMER: This is an UNOFFICIAL alert from students at the Department of Atmospheric and Oceanic Science. For official guidance, please consult the National Weather Service.
                </p>
                <img src="cid:{image_cid}">
            </body>
        </html>
        """,
        """\
        <html>
            <body>
                <p style="font-size:18px;">
                Hello, <br> <br>
                The UMD campus is currently experiencing heavy rain and strong winds. This could lead to flash flooding, wind damages, and very low visibility. Please exercise caution if going outside. <br> <br>
                Sincerely, <br>
                Mesoterps
                </p>
                <p style="font-size:9px;">
                DISCLAIMER: This is an UNOFFICIAL alert from students at the Department of Atmospheric and Oceanic Science. For official guidance, please consult the National Weather Service.
                </p>
                <img src="cid:{image_cid}">
            </body>
        </html>
        """
    ]
    image_cid = make_msgid(domain='weather.umd.edu')
    message.add_alternative(
    bodyMessages[k].format(image_cid=image_cid[1:-1]), subtype='html')
    with open('test.png', 'rb') as img:
        maintype, subtype = mimetypes.guess_type(img.name)[0].split('/')
        message.get_payload()[1].add_related(img.read(), maintype=maintype, subtype=subtype, cid=image_cid)

    with smtplib.SMTP_SSL('smtp.gmail.com', port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())

def main():
    #Spawn child processes to monitor each station over a set time interval
    #Wait for them to check if the alert should be triggered, reap the children, then sleep and repeat

    station_list = ['mesoterp7DB', 'mesoterp8DB', 'mesoterp9DB', 'mesoterp1DB', 'mesoterp3DB']
    #atlantic, williams, golf, vmh, chemistry
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
        
        r = return_dict.values()
        rainArray = []
        windArray = []
        for i in range(0, len(r)):
            rain = False
            wind = False
            if True in r[i][3]:
                rain = True
            if True in r[i][4]:
                wind = True
            rainArray.append(rain)
            windArray.append(wind)

        createGraphic(rain, wind)
        generateEmail(rain, wind)

            

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

