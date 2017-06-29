# -*- coding: utf-8 -*-
"""
Routine to extract temperature data as telemetered by AP2s
originally coded by JiM in Feb 2015 similar to "getfix.py" for drifters
to add leaflets function  by Huanxin 
note: The input datafile, in fact, is the same for drifters,
!!! make sure file codes_temp.dat is uploaded
"""
import os
import sys
import random
import pytz
import ftplib
from func_aq import plot_aq
#hardcode path of modules
#inputfile="raw2013.dat"
#sys.path.append("/net/home3/ocn/jmanning/py/") 
path1="/net/data5/jmanning/drift/" # input data directory
inputfile="raw2013.dat"
pathout='/net/pubweb_html/epd/oceanography/'
codes_file='/home/hxu/github/api/codes_temp.dat'
import glob
from matplotlib.dates import date2num,num2date
import time
import pandas as pd
#from getap2s_functions import gettemps,read_codes,trans_latlon # this module is a modification of the getfix_functions
import datetime
import numpy as np 
import folium
from folium import features
def eastern_to_gmt(filename):
    eastern = pytz.timezone('US/Eastern')
    gmt = pytz.timezone('GMT')
    if len(filename.split('_'))<8:
        times=filename.split('_')[-2]+'_'+filename.split('_')[-1][:-4] #filename likes :  'aqu_data/Logger_sn_1724-7_data_20150528_100400.csv'
    else:
        times=filename.split('_')[-3]+'_'+filename.split('_')[-2] #filename likes : 'aqu_data/Logger_sn_1724-71_data_20151117_105550_2.csv'
    #date = datetime.datetime.strptime(filename, '%a, %d %b %Y %H:%M:%S GMT')
    date = datetime.datetime.strptime(times, '%Y%m%d_%H%M%S')
    date_eastern=eastern.localize(date)
    gmtdate=date_eastern.astimezone(gmt)
    #print date
    return gmtdate

#docks at woods hole, PJ, CapeMay... where data is test only still need to add Gloucester, Newburyport, Hampton. etc
dock_lats=[41.5701,41.3166,38.95694]
dock_lons=[-70.6200,-70.5,-74.87449]
starttime=date2num(datetime.datetime.now())-60  # 31 days
endtime=date2num(datetime.datetime.now())
pic_path='aqu_pic/'
temporary_f_path='aqtemporary/'
'''
# get "including" (list of ESNs), "startyd", and "endyd" for this case using getap2s_function 
print sys.argv[1] # where input argument is the name of the case like, for example, 'getemolt_2015'
#[including,caseid,startyd,endyd]=gettemps(sys.argv[1])
[including,caseid,startyd,endyd]=gettemps(sys.argv[1])
print 'ESNs = '+str(len(including))
print including
'''
emolt='http://www.nefsc.noaa.gov/drifter/emolt.dat'
df=pd.read_csv(emolt,delim_whitespace=True,index_col=0)
including=list(set(df.index))

df_codes=pd.read_csv(codes_file,delim_whitespace=True,index_col=0,names = ["ap3", "depth", "boat_name", "aqu_num"])
#example: 
#including=[320241, 322134, 328420, 368537, 327192, 368742] is the list of ESNs
#caseid=[1, 1, 1, 1, 1, 1] # consecutive use of these transmitter
# get "ide" and "depth" for specific ESNs from /data5/jmanning/drift/codes_temp.dat
#where "ide" is the eMOLT site
#[esn,ide,depth]=read_codes('codes.dat')

map_1 = folium.Map(location=[41.572, -68.9072],width='88%', height='80%',left="3%", top="2%",
                   control_scale=True,
                   detect_retina=True,
                   zoom_start=8      
	)

map_1.add_tile_layer(tiles='Oceanbasemap',name='Oceanbasemap',
                          attr= 'Tiles &copy; Esri &mdash; National Geographic, Esri, DeLorme, NAVTEQ, UNEP-WCMC, USGS, NASA, ESA, METI, NRCAN, GEBCO, NOAA, iPC',
                          tile_url='http://server.arcgisonline.com/ArcGIS/rest/services/Ocean_Basemap/MapServer/tile/{z}/{y}/{x}',
                          )
map_1.add_tile_layer(                   name='NatGeo_World_Map',
                   #tiles='https://server.arcgisonline.com/ArcGIS/rest/services/Ocean_Basemap/MapServer/tile/{z}/{y}/{x}/',
                   #tiles='http://services.arcgisonline.com/ArcGIS/rest/services/Specialty/World_Navigation_Charts/MapServer/tile/{z}/{y}/{x}',
                   tile_url='http://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}',
                   attr= 'Tiles &copy; Esri &mdash; National Geographic, Esri, DeLorme, NAVTEQ, UNEP-WCMC, USGS, NASA, ESA, METI, NRCAN, GEBCO, NOAA, iPC',)

colors=['red', 'darkred', 'orange', 'green', 'green', 'blue', 'purple', 'darkpuple', 'cadetblue','red', 'darkred', 'orange', 'green', 'orange', 'blue', 'purple', 'darkpuple', 'cadetblue']
#dictionary = zip(esn, colors)
lat_box=[];lon_box=[]
route=0;lat=0;lon=0;popup=0;idn1=0;html='';lastfix=1;randomlat=1;randomlon=0;png_files=[]
mc = features.MarkerCluster()  
for i in range(0,len(including)): # note: I am skipping vessel_1 since that was just at the dock test
  print i,route,popup,lastfix,
  if i<>route and popup<>0 and lastfix==0 and html<>'':
                         
                                             #print 1111111111111111111111111111111111111111111111111111111
                                             iframe = folium.element.IFrame(html=html, width=300, height=250)
                                             popup = folium.Popup(iframe, max_width=900)
                                             folium.Marker([lat+randomlat,lon+randomlon], popup=popup,icon=folium.Icon(color=colors[route],icon='info-sign')).add_to(map_1)  
  
  
  #print startyd[i],endyd[i]
  #open the raw input datafile 

  lastfix=1
  
  
  for line in range(len(df)):
      if df.iloc[line].name==including[i]:
          id_idn1=including[i]
          yr1=int(df.iloc[line][15])
          mth1=int(df.iloc[line][1])
          day1=int(df.iloc[line][2])
          hr1=int(df.iloc[line][3])
          mn1=int(df.iloc[line][4])
          yd1=float(df.iloc[line][5])
          datet=datetime.datetime(yr1,mth1,day1,hr1,mn1,tzinfo=None)
          
          #atet=str(int())
          if starttime<=date2num(datet)<=endtime:
              html=''
              meandepth=str(df.iloc[line][10])
              rangedepth=str(df.iloc[line][11])
              len_day=df.iloc[line][12]
              mean_temp=str(df.iloc[line][13])
              sdevia_temp=str(df.iloc[line][14])
              lat=df.iloc[line][7]
              lon=df.iloc[line][6]
              for aqu_file in glob.glob('aqu_data/*'):
                  gmttime=eastern_to_gmt(aqu_file)
                  if date2num(datet)-(1/24./1.5)<date2num(gmttime)<date2num(datet)+(1/24./1.5): #20 minutes period
                      if df_codes[df_codes['aqu_num']==aqu_file.split('_')[3]].index.tolist()[0]==including[i]:
                          print aqu_file,line,including[i]
                          png_files.append(aqu_file[9:-4]+'.png')
                                      
                          html='''
                                <h1>  '''+id_idn1+'''</h1><br>
                                  
                                <p>
                                <body>
                                <code>
                                '''+datet.strftime('%d-%b-%Y  %H:%M')+ '<br>meandepth(m): '+str(meandepth).rjust(10)+'<br>rangedepth(m): '+str(rangedepth).rjust(10)+'<br>time_period(minutes): '+str(len_day*60*24).rjust(10) +'<br>meantemp(C): ' +str(mean_temp).rjust(4)+'<br>sdevia_temp(C): '+str(sdevia_temp)+'<br>Click <a href="http://studentdrifters.org/huanxin/'+aqu_file[9:-4]+'.png">here</a> to view the detailed graph.<br>Click <a href="http://nefsc.noaa.gov/drifter/'+including[i]+'.png">here</a> to view the long time series graph.''''
                                </code>
                                <img src="http://studentdrifters.org/huanxin/'''+aqu_file[9:-4]+'''.png" alt="pics" style="width:300px;height:260px;"></body>
                                </p>
                                '''
                          
              if html=='':
                   html='''
                        <h1>  '''+id_idn1+'''</h1><br>
                          
                        <p>
                        <body>
                        <code>
                        '''+datet.strftime('%d-%b-%Y  %H:%M')+ '<br>meandepth(m): '+str(meandepth).rjust(10)+'<br>rangedepth(m): '+str(rangedepth).rjust(10)+'<br>time_period(minutes): '+str(len_day*60*24).rjust(10) +'<br>meantemp(C): ' +str(mean_temp).rjust(4)+'<br>sdevia_temp(C): '+str(sdevia_temp)+'<br>Click <a href="http://nefsc.noaa.gov/drifter/'+including[i]+'.png">here</a> to view the long time series graph.''''
                        </code>
                        </body>
                        </p>
                        '''
              lon_box.append(lon)
              lat_box.append(lat)
              iframe = folium.element.IFrame(html=html, width=520, height=280)
              popup = folium.Popup(iframe, max_width=1500)
              randomlat=random.randint(-3000, 3000)/100000.
              randomlon=random.randint(-2500, 2000)/100000.
              #folium.Marker([lat+randomlat,lon+randomlon], popup=popup,icon=folium.Icon(icon='star',color=colors[i])).add_to(map_1)
              mk=folium.Marker([lat+randomlat,lon+randomlon], popup=popup,icon=folium.Icon(icon='star',color=colors[i]))
              mc.add_children(mk)
              map_1.add_children(mc)
              lastfix=0
  route=i
"""

for i in range(1,len(including)): # note: I am skipping vessel_1 since that was just at the dock test
  if i<>route and popup<>0 and lastfix==0:
                                             #print 1111111111111111111111111111111111111111111111111111111
                                             iframe = folium.element.IFrame(html=html, width=300, height=250)
                                             popup = folium.Popup(iframe, max_width=900)
                                             folium.Marker([lat+randomlat,lon+randomlon], popup=popup,icon=folium.Icon(color=colors[route],icon='info-sign')).add_to(map_1)  
                                             
  #open the raw input datafile 
  lastfix=1
  f = open(inputfile,'r')
  #f = open(path1+inputfile,'r') 
  #     f_output.write("ID        ESN   MTH DAY HR_GMT MIN  YEARDAY    LON           LAT     DEPTH TEMP\n")
  #start parsing the variables needed from the raw datafile
  for line in f:
      if line[1:4]=='esn' and line[11]=='<': #AP2s!!:
          idn1=int(line[7:11]) # picks up ESN
          #print idn1
          xxx=[]
          if idn1==including[i]:
                index_idn1=np.where(str(idn1)==np.array(esn))[0] # Is this ESN in the codes_temp?
                # some idn1 can not fine in ESN (codes_temps.dat), so I can not find it's id and depth
                if index_idn1.shape[0]<>0: # if this unit is included in the codes_temp.dat file
                    id_idn1=ide[index_idn1[caseid[i]-1]] # where "caseid" is the consecutive time this unit was used
                    depth_idn1=-1.0*float(depth[index_idn1[caseid[i]-1]]) # make depth negative
                    skip1=next(f) #skip one line
                    if skip1[1:9]=="unixTime":
                        unixtime=int(skip1[10:20]) #get unix time
                        #convert unixtime to datetime
                        time_tuple=time.gmtime(unixtime)
                        yr1=time_tuple.tm_year
                        mth1=time_tuple.tm_mon
                        day1=time_tuple.tm_mday
                        hr1=time_tuple.tm_hour
                        mn1=time_tuple.tm_min
                        yd1=date2num(datetime.datetime(yr1,mth1,day1,hr1,mn1))-date2num(datetime.datetime(yr1,1,1,0,0))
                        datet=datetime.datetime(yr1,mth1,day1,hr1,mn1,tzinfo=None)                               
                        skip2=next(f) # skip one line
                        #skip3=next(f)
                        skip4=next(f)                        
                        if datet>startyd[i] and datet<endyd[i] and skip4[17]<>9 and skip4[17:19]<>27:
                          data_raw=skip4[48:]

                          try:
                            if (int(data_raw[27:31])<900) or (int(data_raw[27:31])>1100):
                              #print data_raw
                              lat,lon=trans_latlon(data_raw)    # transfer lat,lon from Hex to Decimal
                                #check to see if this is a dock side test
                              dist_bear=[]
                              for kk in range(len(dock_lats)):
                                 if (lat<89.) and (data_raw[21]!='B') and (data_raw[27]!='D') and (data_raw[31]!='D') and (data_raw[21]!='D') and (data_raw[32]!='D') and (datetime.datetime.now()-datet<datetime.timedelta(45)) and (data_raw[20]!='B') and (lat not in lat_box) and (lon not in lon_box): # otherwise no good GPS
                                    #print    float(data_raw[21:26])        
                                    meandepth=float(data_raw[21:24])              
                                    rangedepth=float(data_raw[24:27])              
                                    len_day=float(data_raw[27:30])/1000.            
                                    mean_temp=float(data_raw[30:34])/100
                                    try:
                                      float(data_raw[34:38]) # this problem arose in March 2016
                                      sdevia_temp=float(data_raw[34:38])/100           #standard deviation temperature
                                    except ValueError:
                                      sdevia_temp=0.0  
                                    if mean_temp<30.0: #eliminates obviously bad data
                                      lastime= str(mth1).rjust(2)+ " " + str(day1).rjust(2)+" " +str(hr1).rjust(3)+ " " +str(mn1).rjust(3)
                                      html=      '''<h1>'''+id_idn1+'''</h1><br> 
                                            <p>                                                                                   
                                            <code>
                                            '''+datet.strftime('%d-%b-%Y  %H:%M')+ '<br>meandepth(m): '+str(meandepth).rjust(10)+'<br>rangedepth(m): '+str(rangedepth).rjust(10)+'<br>time_period(minutes): '+str(len_day*6*24).rjust(10) +'<br>meantemp(C): ' +str(mean_temp).rjust(4)+'<br>sdevia_temp(C): '+str(sdevia_temp)+'''
                                            </code>
                                            </p>
                                            '''
                                      lon_box.append(lon)
                                      lat_box.append(lat)
                                      iframe = folium.element.IFrame(html=html, width=300, height=250)
                                      popup = folium.Popup(iframe, max_width=900)
                                      randomlat=random.randint(-14000, 14000)/100000.
                                      randomlon=random.randint(-14000, 14000)/100000.
                                      #folium.Marker([lat+randomlat,lon+randomlon], popup=popup,icon=folium.Icon(icon='star',color=colors[i])).add_to(map_1)
                                      mk=folium.Marker([lat+randomlat,lon+randomlon], popup=popup,icon=folium.Icon(icon='star',color=colors[i]))
                                      mc.add_children(mk)
                                      map_1.add_children(mc)
                                      lastfix=0 # for last fix       
                          except:
                             print ''         
  f.close()
  route=i
"""  
#f_output.close()
#map_1.save(pathout+'fishtemp_lf.html')  
folium.LayerControl().add_to(map_1)
map_1.save('telemetry.html')
with open('telemetry.html', 'a') as file:
    file.write('''        <body>
            <div id="header"><br>
                <h1>&nbsp;&nbsp;&nbsp;&nbsp&nbsp;Realtime Bottom Temperatures from Fishing Vessels</h1>                
                <h2>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Icons posted within 10 miles of actual position</h2> 
            </div>   
        
        
        
        </body>''')
file.close()



if __name__=="__main__":

    if not os.path.exists('../uploaded_files'):
        os.makedirs('../uploaded_files')
  
    open('../uploaded_files/myfile.dat','w+').close()
    files=png_files

    with open('../uploaded_files/myfile.dat') as f:
        content = f.readlines()        
    upfiles = [line.rstrip('\n') for line in open('../uploaded_files/myfile.dat')]
    

    #f=open('../uploaded_files/myfile.dat', 'rw')
    dif_data=list(set(files)-set(upfiles))
    if dif_data==[]:
        print 'no new file was found'
        time.sleep(15)
        pass
 
    for u in dif_data:
        #print u
        pic_name=plot_aq('aqu_data/'+u.replace('png','csv'),pic_path,temporary_f_path)
        session = ftplib.FTP('216.9.9.126','huanxin','123321')
        try:
            #file = open("aqu_data/"+u,"rb") 
            session.cwd("/aqu_pic")  
            #session.retrlines('LIST')               # file to send
            #session.storbinary('STOR ' +u, file) 
            session.storbinary("STOR " +u, open(pic_name, 'rb'))   # send the file
            #session.close()
            #file.close()
            session.quit()# close file and FTP
            #file.close()
            #file.close() 
            print u
            #os.rename('C:/Program Files (x86)/Aquatec/AQUAtalk for AQUAlogger/DATA/'+u[:7]+'/'+u[8:], 'C:/Program Files (x86)/Aquatec/AQUAtalk for AQUAlogger/uploaded_files/'+u[8:])
            print u+' uploaded'
            #os.rename(u[:7]+'/'+u[8:], "uploaded_files/"+u[8:]) 
            time.sleep(2)                     # close file and FTP
        except:
            print u+' did not upload'
    upfiles.extend(dif_data)
    f=open('../uploaded_files/myfile.dat','w')
    [f.writelines(i+'\n') for i in upfiles]
    f.close()
    print 'you can leave or close your wifi if you want'
    #time.sleep(180)        
