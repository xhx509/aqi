# -*- coding: utf-8 -*-
"""
Created on Mon Feb 29 13:16:01 2016

@author: hxu
"""

'''
This program include 4 basic applications
1, Download csv files which is oploaded by 'wifi.py' and stored in 'studentdrifters.org'
2, Plot a graph for each downloaded csv file
3, Organize and upload csv and graph files to google drive of 'huanxin.data@gmail.com'
4, Send email to notice the people who need these data files

###############################################
NOTICE: The PATHS YOU HAVE TO CHANGE TO MAKE THEM CORRECT
###############################################
'''
import ftplib
import os
import time
import glob
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from func_aq import plot_aq


ddir='/home/hxu/github/api/'
path='aqu_data/'
pic_path='aqu_pic/'
temporary_f_path='aqtemporary/'
os.chdir(ddir)
#ftp = FTP('/huanxin')

ftp=ftplib.FTP('216.9.9.126','huanxin','123321')
print 'Logging in.'
ftp.cwd('/huanxin')
print 'Accessing files'

filenames_new = ftp.nlst() # get filenames within the directory
#print filenames_new

filenames_history=sorted(glob.glob(path+'*.csv'))
filenames_history=[i[9:] for i in filenames_history]
files=list(set(filenames_new)-set(filenames_history))


for filename in files:
    local_filename = os.path.join(ddir+temporary_f_path, filename)
    file = open(local_filename, 'wb')
    ftp.retrbinary('RETR '+ filename, file.write)
    #ftp.delete(filename)
    file.close()

ftp.quit() # This is the “polite” way to close a connection
files=[(temporary_f_path+i) for i in files]
files=list(set(files))
#time.sleep(7200)
'''
filenames_history=sorted(glob.glob(path+'*.csv'))
filenames_history=[i[9:] for i in filenames_history]
files=list(set(filenames_new)-set(filenames_history))
files=[(temporary_f_path+i) for i in files]
files=list(set(files))
'''
#####################################################################
gpath=[]
[gpath.append(i.split('_')[2].split('-')[1]) for i in files]   # get the logger number here .."very important", you may need to change, or add logger number files in google drive
######################################################################
gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

#files.remove('aqtemporary/Logger_sn_1724-11_data_20160818_110124.csv')

#file1 = drive.CreateFile({'title': fname, "parents":  [{"kind": "drive#fileLink","id": id}]})
count=0
for m in range(len(files)):
    pic_name=plot_aq(files[m],pic_path,temporary_f_path) # plot graph
    #print 'pic_name:====='+pic_name
    if pic_name=='':
        continue
    #for file_list in drive.ListFile({'q': 'trashed=true', 'maxResults': 10}):  
    #for file_list in drive.ListFile({'q': 'trashed=true', 'maxResults': 10}):
    file_list = drive.ListFile({'q': "trashed=false"}).GetList()
    for file1 in file_list:
      if file1['title'] == gpath[m]:
          id = file1['id']
    file1 = drive.CreateFile({'title': files[m].split('/')[1],       # for get the original name, without prefix
        "parents":  [{"id": id}], 
    })
    print 'this is : '+files[m]
    file1.SetContentFile(files[m])
    file1.Upload()
    count=count+1
    
    os.rename(files[m],ddir+path+files[m][len(temporary_f_path):])
    if pic_name<>'few data':
        
        file2 = drive.CreateFile({'title': pic_name.split('/')[1], 
            "parents":  [{"id": id}], 
        })
        file2.SetContentFile(pic_name)
        file2.Upload()    
        os.rename(pic_name,ddir+path+files[m][len(temporary_f_path):-3]+'png')

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

 
fromaddr = "huanxin.data@gmail.com"
toaddr = "xhx509@gmail.com"
 
msg = MIMEMultipart()
 
msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] ="Your aquetec csv data" #"SUBJECT OF THE EMAIL"
 
body = str(count)+" raw data files were transmitted by WIFI, Please Click this link to get your aquetec data\n https://drive.google.com/open?id=0BwmSjxiv9rYLUlhhWS1sN01LTUk"

msg.attach(MIMEText(body, 'plain'))
 
 
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(fromaddr, "likeicecream")  # your email address and password
text = msg.as_string()
server.sendmail(fromaddr, toaddr, text)
server.quit() 
import pandas as pd   
codes_file='/home/hxu/github/api/codes_temp.dat'
df_codes=pd.read_csv(codes_file,delim_whitespace=True,index_col=0,names = ["ap3", "depth", "boat_name", "aqu_num"])
boat_name=[]
for i in range(len(files)):
    boat_name.append(df_codes[df_codes['aqu_num']==files[i].split('_')[2]]['boat_name'].tolist()[0])
from collections import Counter
boat_count=Counter(boat_name)











