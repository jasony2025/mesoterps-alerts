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
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import Circle


img = mpimg.imread('cmcm.jpg')
imgplot = plt.imshow(img)


plt.gca().add_patch(plt.Circle((0, 0), 0, color='lightgreen'))
plt.gca().add_patch(plt.Circle((0, 0), 0, color='r'))
plt.gca().add_patch(plt.Circle((0, 0), 0, color='b'))
plt.gca().add_patch(plt.Circle((50, 630), 40, facecolor='b', edgecolor='black'))
t1 = plt.text(70, 590, "Golf Course", fontweight='extra bold', fontsize=10)
t1.set_bbox(dict(facecolor='lightblue', alpha=1, edgecolor='black'))
plt.gca().add_patch(plt.Circle((620, 1340), 40, facecolor='springgreen', edgecolor='black'))
t2 = plt.text(620, 1290, "Van Munching Hall", fontweight='extra bold', fontsize=10, ha='center')
t2.set_bbox(dict(facecolor='lightgreen', alpha=1, edgecolor='black'))
plt.gca().add_patch(plt.Circle((920, 590), 40, facecolor='springgreen', edgecolor='black'))
t3 = plt.text(920, 540, "Atlantic Building", fontweight='extra bold', fontsize=10, ha='center')
t3.set_bbox(dict(facecolor='lightgreen', alpha=1, edgecolor='black'))
plt.gca().add_patch(plt.Circle((1390, 610), 40, facecolor='r', edgecolor='black'))
t4 = plt.text(1390, 560, "AV Williams Building", fontweight='extra bold', fontsize=10, ha='center')
t4.set_bbox(dict(facecolor='lightcoral', alpha=1, edgecolor='black'))
plt.gca().add_patch(plt.Circle((1150, 730), 40, facecolor='r', edgecolor='black'))
t5 = plt.text(1150, 680, "Chemistry Building", fontweight='extra bold', fontsize=10, ha='center')
t5.set_bbox(dict(facecolor='lightcoral', alpha=1, edgecolor='black'))
plt.legend(["No recent alerts", "Recent rain alert", "Recent wind alert"], fontsize=10)

plt.savefig('test.png')


port = 465
password = "zgdf emij huka kkgf"
context = ssl.create_default_context()
sender_email = "allurations@gmail.com"
receiver_email = ["sirswagger21@gmail.com"]

subject = "Hi there"
body = "The UMD campus is experiencing heavy rain. This could lead to flash flooding. Please exercise caution if going outside."

message = MIMEMultipart()
message['Subject'] = subject
message['From'] = sender_email
message['To'] = ", ".join(receiver_email)
message.attach(MIMEText(body))

with open('test.png', 'rb') as f:
    image_part = MIMEImage(f.read())
message.attach(image_part)

with smtplib.SMTP_SSL('smtp.gmail.com', port, context=context) as server:
   server.login(sender_email, password)
   server.sendmail(sender_email, receiver_email, message.as_string())


