import mariadb
import math
import sys
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



fig, ax = plt.subplots()
ax.patch.set_alpha(0)

rain = [True, True, False, True, False]
wind = [False, False, False, True, True]
img = mpimg.imread('Meteorology\Micronet\cmcm.jpg')
imgplot = ax.imshow(img)
rainPicture = mpimg.imread('Meteorology\\Micronet\\rainNew3.png')
windPicture = mpimg.imread('Meteorology\\Micronet\\windNew.png')
neutralPicture = mpimg.imread('Meteorology\\Micronet\\neutralNew6.png')
bothPicture = mpimg.imread('Meteorology\\Micronet\\bothNew.png')


# ax.add_patch(plt.Circle((0, 0), 0, color='springgreen'))
# ax.add_patch(plt.Circle((0, 0), 0, color='lightcoral'))
# ax.add_patch(plt.Circle((0, 0), 0, color='lightblue'))

colors = []
pictures = []
for i in range(0, len(rain)):
    if rain[i] == False and wind[i] == False:
        colors.append('springgreen')
        pictures.append(neutralPicture)
    elif rain[i] == True and wind[i] == False:
        colors.append('lightblue')
        pictures.append(rainPicture)
    elif rain[i] == False and wind[i] == True:
        colors.append('lightcoral')
        pictures.append(windPicture)
    else:
        colors.append('lavender')
        pictures.append(bothPicture)



#atlantic
j = 0
fig.figimage(pictures[j], 413, 369) #atlantic
t1 = ax.text(920, 540, "Atlantic Building", fontweight='extra bold', fontsize=10, ha='center')
t1.set_bbox(dict(facecolor=colors[j], alpha=1, edgecolor='black'))

#williams
j = 1
fig.figimage(pictures[j], 605, 425) #av williams
t2 = ax.text(1360, 395, "AV Williams Building", fontweight='extra bold', fontsize=10, ha='center')
t2.set_bbox(dict(facecolor=colors[j], alpha=1, edgecolor='black'))

#golf
j = 2
fig.figimage(pictures[j], 100, 410) #golf
t3 = ax.text(70, 602, "Golf Course", fontweight='extra bold', fontsize=10)
t3.set_bbox(dict(facecolor=colors[j], alpha=1, edgecolor='black'))

#vmh
j = 3
fig.figimage(pictures[j], 308, 140) #vmh
t4 = ax.text(620, 1286, "Van Munching Hall", fontweight='extra bold', fontsize=10, ha='center')
t4.set_bbox(dict(facecolor=colors[j], alpha=1, edgecolor='black'))

#chem
j = 4
fig.figimage(pictures[j], 510, 375) #chem
t5 = ax.text(1340, 669, "Chemistry Building", fontweight='extra bold', fontsize=10, ha='center')
t5.set_bbox(dict(facecolor=colors[j], alpha=1, edgecolor='black'))


ax.legend(["No recent alerts", "Recent rain alert", "Recent wind alert"], fontsize=10)
ax.set_title('Hazardous Weather Conditions Map')
fig.set_size_inches(8, 8)

plt.savefig('test.png', bbox_inches='tight')




k = 0
if True in rain and True not in wind:
    k = 0
elif True in wind and True not in rain:
    k = 1
elif True in rain and True in wind:
    k = 2


port = 465
password = "khtb zmtx npmm zqkq"
context = ssl.create_default_context()
sender_email = "umdmicronetalerts@gmail.com"
receiver_email = ["sirswagger21@gmail.com", "Jasony2025@gmail.com"]

subjectMessages = ["Rain Alert: Exercise Caution", "Wind Alert: Exercise Caution", "Rain and Wind Alert: Exercise Caution"]
subject = subjectMessages[k]

message = EmailMessage()
message['Subject'] = subject
message['From'] = "UMD Micronet Alerts umdmicronetalerts@gmail.com"
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
