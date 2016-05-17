# -*- coding: utf-8 -*-
"""
Created on Mon May  9 11:05:58 2016

@author: hxu
"""

import glob
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from func_aq import plot_aq
path='aqu_data/'
pic_path='aqu_pic'
files=sorted(glob.glob(path+'*.csv'))
gpath=[]
[gpath.append(i[24:26]) for i in files]

gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)



#file1 = drive.CreateFile({'title': fname, "parents":  [{"kind": "drive#fileLink","id": id}]})
for m in range(len(files)):
    pic_name=plot_aq(files[m],pic_path) # plot graph
    #print 'pic_name:====='+pic_name
    if pic_name=='':
        continue
    #for file_list in drive.ListFile({'q': 'trashed=true', 'maxResults': 10}):  
    #for file_list in drive.ListFile({'q': 'trashed=true', 'maxResults': 10}):
    file_list = drive.ListFile({'q': "trashed=false"}).GetList()
    for file1 in file_list:
      if file1['title'] == gpath[m]:
          id = file1['id']
    file1 = drive.CreateFile({'title': files[m], 
        "parents":  [{"id": id}], 
    })
    file1.SetContentFile(files[m])
    file1.Upload()
    if pic_name<>'few data':
        
        file2 = drive.CreateFile({'title': pic_name, 
            "parents":  [{"id": id}], 
        })
        file2.SetContentFile(pic_name)
        file2.Upload()    


import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

 
fromaddr = "huanxin.data@gmail.com"
toaddr = "xhx509@gmail.com"
 
msg = MIMEMultipart()
 
msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] ="Your aquetec csv data" #"SUBJECT OF THE EMAIL"
 
body = "Please Click this link to get your aquetec data\n https://drive.google.com/open?id=0BwmSjxiv9rYLUlhhWS1sN01LTUk"

msg.attach(MIMEText(body, 'plain'))
 
 
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(fromaddr, "likeicecream")  # your email address and password
text = msg.as_string()
server.sendmail(fromaddr, toaddr, text)
server.quit()    