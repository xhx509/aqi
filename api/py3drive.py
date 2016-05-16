# -*- coding: utf-8 -*-
"""
Created on Tue Apr 26 15:50:38 2016

@author: hxu
"""


'''
gauth = GoogleAuth()
drive = GoogleDrive(gauth)
parent_id='43'
#f = drive.CreateFile()
#f = drive.CreateFile({'parent': parent_id})
f = drive.CreateFile({'title':'dummy.csv', 'mimeType':'text/csv',
        "parents": [{"kind": "drive#fileLink","id": '43'}]})
f.SetContentFile('asdf.dat') # Read local file
f.Upload() # Upload it

'''




import sys
sys.path.extend('/home/hxu/Public/anaconda/lib/python2.7/site-packages')
sys.path.append('/home/hxu/Public/anaconda/lib/python2.7/site-packages/')
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

gpath = '43'
fname = 'asdf.dat'

gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
for file1 in file_list:
    if file1['title'] == gpath:
        id = file1['id']

#file1 = drive.CreateFile({'title': fname, "parents":  [{"kind": "drive#fileLink","id": id}]})
file1 = drive.CreateFile({'title': fname, 
    "parents":  [{"id": id}], 
})
file1.SetContentFile(fname)
file1.Upload()
'''
import sys
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
def createRemoteFolder(self, folderName, parentID = None):
        # Create a folder on Drive, returns the newely created folders ID
        body = {
          'title': folderName,
          'mimeType': "application/vnd.google-apps.folder"
        }
        if parentID:
            body['parents'] = [{'id': parentID}]
        root_folder = drive_service.files().insert(body = body).execute()
        return root_folder['id']
folderName='1234'

'''       