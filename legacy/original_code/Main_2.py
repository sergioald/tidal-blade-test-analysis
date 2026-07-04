# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 09:23:41 2022

@author: slopezd
"""

print('Run Test Process')

from nptdms import TdmsFile
import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
import sys
from nptdms import TdmsFile, TdmsWriter, RootObject, ChannelObject, GroupObject
import shutil
#%%
print('start')
##working Paths
Path_Code=os.path.abspath(os.getcwd())
os.chdir("..")
Main_Path=os.path.abspath(os.curdir)
Main_Input=os.path.join(Main_Path,'Test Data')
Main_Output=os.path.join(Main_Path,'Join_Data')



# files = os.listdir(Main_Input)
# files = [s for s in files if s.__contains__(".tdms")]

#%%
#Rear Main file
fname='Loadtide_Test_Log.xlsx'
Test_Log= pd.read_excel(os.path.join(Main_Path,fname),sheet_name='Test_Log')
Test_Log.dropna(subset = ["Date_start"], inplace=True)
#Get Zero
zeros_test=Test_Log.index[Test_Log['Type_Test'] == 'ZO'].tolist()
nf_test=Test_Log.index[Test_Log['Type_Test'] == 'NF'].tolist()
st_test=Test_Log.index[Test_Log['Type_Test'] == 'ST'].tolist()
fa_test=Test_Log.index[Test_Log['Type_Test'] == 'FA'].tolist()


#%%
#Check all files open

check=0
if check==1:
    cnt=0
    for indx, row in Test_Log.iterrows():
        print(indx,row['Type_Test'],row['Test_Reference'])
        zero_fname=row['Test_Reference']
        zero_path=os.path.join(Main_Input,zero_fname)
        zero_files = [s for s in os.listdir(zero_path) if s.__contains__(".tdms") and not s.__contains__("_index")]
        
        Main_Output_file=os.path.join(Main_Output,zero_fname)
        if os.path.exists(os.path.join(Main_Output_file,zero_fname+'.tdms')):
            print('File exist', zero_fname)
            continue
        
        for fl in zero_files:
            try:
                zero_tdms_file = TdmsFile(os.path.join(zero_path,fl))
            except:
                print ('Error opeing: ', indx,row['Type_Test'],row['Test_Reference'], fl)
                cnt=+1
    if cnt>0:
        sys.exit()
    else:
        print('All fiiles can be open')

#%%
### JOIN FILES

# cnt=0
# #Verify against first file
# # if len(list(set(all_chn_lst_1).intersection(all_chn_lst))) != len(all_chn_lst):
# #     print('Not same Channels, write code to solve')
# #     sys.exit()



def join_tdms(fname):
    
#%%    
    Main_Output_file=os.path.join(Main_Output,fname)

    if not os.path.exists(Main_Output_file):
        os.makedirs(Main_Output_file)
        
    if os.path.exists(os.path.join(Main_Output_file,fname+'.tdms')):
        print('File exist', fname)
        return
    

    ft_path=os.path.join(Main_Input,fname)

    #def Join_tdms(ft_path):
    ft_files = [s for s in os.listdir(ft_path) if s.__contains__(".tdms") and not s.__contains__("_index")]

    ft_files.sort()

    # df_ch=pd.DataFrame(data=None,columns=ft_files )
    all_chn_lst=[]

    #Get all the chnls
    cnt=0
    if len(ft_files)>1:
        for k in ft_files:
            with TdmsFile.open(os.path.join(ft_path,k)) as ft_tdms_file:
                # ft_tdms_file = TdmsFile(os.path.join(ft_path,k))
                ft_log= ft_tdms_file['Log']
                if cnt==0:
                    # all_chn_lst_1=[key for key in ft_log._channels]
                    all_chn_lst_2=[key for key in ft_log._channels]
                    intial_num_ch=len(all_chn_lst_2)
                    cnt=+1
                else:
                    all_chn_lst_3=[key for key in ft_log._channels]
                    all_chn_lst.extend(all_chn_lst_3)
                    new_num_ch=len(all_chn_lst_3)
                    if not intial_num_ch==new_num_ch:
                        print(k, 'has pluss numnber of channels: ',new_num_ch-intial_num_ch)
                        diff_ch_1=list(set(all_chn_lst_3).difference(all_chn_lst_2))
                        diff_ch_2=list(set(all_chn_lst_2).difference(all_chn_lst_3))
                        if len(diff_ch_1)>0:
                            print('New channels are: ',diff_ch_1)
                        if len(diff_ch_2)>0:
                            print('Missing Channels are:',diff_ch_2)
                    all_chn_lst_2=all_chn_lst_3
                    intial_num_ch=new_num_ch
                        
            all_chn_lst = (list(set(all_chn_lst)))
            
            
            # if not len(all_chn_lst) == len(all_chn_lst_1):
            #     print('problem number of channels change')
        
    else:
        with TdmsFile.open(os.path.join(ft_path,k)) as ft_tdms_file:
            ft_tdms_file = TdmsFile(os.path.join(ft_path,k))
            ft_log= ft_tdms_file['Log']
            all_chn_lst.extend([key for key in ft_log._channels])
        
    all_chn_lst.sort()
    
    del ft_tdms_file, ft_log
    
#%%   
    if len(ft_files)==1:
        
        shutil.copyfile(os.path.join(ft_path,ft_files[0]), os.path.join(Main_Output_file,fname+'.tdms'))
        
        return
#%%      
    cnt=0

        
    with TdmsWriter(os.path.join(Main_Output_file,fname+'.tdms')) as tdms_writer: 
    
        for k in ft_files:
            
            print(k)
            
            
            
            if cnt==0:
                
                cnt=+1
                original_file = TdmsFile(os.path.join(ft_path,k))
                original_groups = original_file.groups()
                root_object = RootObject(original_file.properties)
                
                
                tdms_writer.write_segment([root_object] + original_groups)
                
                all_chn_lst=[key for key in original_file['Log']._channels]

                strt_times=[]
                end_times=[]
                tf_original=[]
                
                
                for ch in all_chn_lst:
                    strt_times.append(original_file['Log'][ch].properties['wf_start_time'])
                    end_times.append(original_file['Log'][ch].time_track(absolute_time=True)[-1])
                strt_t=max(strt_times)
                end_t=min(end_times)

                print(max(end_times),min(end_times))
                print('first file')
                for chn_c in all_chn_lst:                    

                        
                    # print('problem in ',cnt,chn_c,dtt, dt0,t0,t1,prop['wf_samples'])

                    strt=np.argmin(abs(original_file['Log'][chn_c].time_track(absolute_time=True)-strt_t))
                    endd=np.argmin(np.abs(original_file['Log'][chn_c].time_track(absolute_time=True)-end_t))
                    
                    
                    data=original_file['Log'][chn_c][strt:endd]
                    prop=original_file['Log'][chn_c].properties
                    prop['wf_samples']=data.shape[0]
                    prop['wf_start_time']=original_file['Log'][chn_c].time_track(absolute_time=True)[strt]
                    
                    channel_object = ChannelObject("Log", original_file['Log'][chn_c].name, \
                                                data,\
                                                properties=prop)
                    tdms_writer.write_segment([channel_object]) 
                    
                    tf_original.append(original_file['Log'][chn_c].time_track(absolute_time=True)[endd])

                original_file.close()                
                
            else:
                
                cnt+=1
                original_file=[]
                original_groups=[]
                root_object=[]
                
                tf_original=[]
                
                with TdmsFile.open(os.path.join(Main_Output_file,fname+'.tdms')) as original_file:
                    
                    
                    next_file = TdmsFile(os.path.join(ft_path,k))
                    all_chn_lst=[key for key in next_file['Log']._channels]
                    # all_chn_lst.sort()
                    all_chn_lst_or=[key for key in original_file['Log']._channels]
                    
                    all_chn_lst_new_chn=list(set(all_chn_lst).difference(all_chn_lst_or))
                    
                    all_chn_lst_cmn=list(set(all_chn_lst_or).intersection(all_chn_lst))
                    
                    strt_times=[]
                    end_times=[]
                    for ch in all_chn_lst_cmn:
                        strt_times.append(next_file['Log'][ch].properties['wf_start_time'])
                        end_times.append(next_file['Log'][ch].time_track(absolute_time=True)[-1])
                    strt_t=max(strt_times)
                    end_t=min(end_times)
                    
                    pause_file=0
                    
                    for chn_c in all_chn_lst_cmn:
                        
                        dt0=original_file['Log'][chn_c].properties['wf_increment']
                        dt1=next_file['Log'][chn_c].properties['wf_increment']
                        
                        
                        # ta=original_file['Log'][chn_c].properties['wf_start_time']
                        t0=original_file['Log'][chn_c].time_track(absolute_time=True)[-1]
                        t1=next_file['Log'][chn_c].properties['wf_start_time']
                        dtt=pd.to_timedelta(t1-t0).total_seconds()
                        
                        tfo=original_file['Log'][chn_c].time_track(absolute_time=True)[-1]
                        
                        tf_original.append(tfo)
                        
                        if not (dt0==dt1 and dtt==dt0):
                            pause_file=1
                    
                    # print(strt_t,end_t,pd.to_timedelta(strt_t-end_t).total_seconds())
                    print(max(tf_original),min(tf_original),pd.to_timedelta(max(tf_original)-min(tf_original)).total_seconds())
                    
                    if pause_file==1:
                        print('Pause file')
                    else:
                        print('No Pause File')
                    
                    for chn_c in all_chn_lst_cmn:                    
                        if pause_file==0:
                    
                            endd=np.argmin(abs(next_file['Log'][chn_c].time_track(absolute_time=True)-end_t))
                            
                            data= np.append(original_file['Log'][chn_c][:],next_file['Log'][chn_c][:endd])
                            prop=original_file['Log'][chn_c].properties
                            prop['wf_samples']=data.shape[0]
                            data=next_file['Log'][chn_c][:endd]
                            
                            channel_object = ChannelObject("Log", next_file['Log'][chn_c].name, \
                                                        data,\
                                                        properties=prop)
                            tdms_writer.write_segment([channel_object])
                        else:
                            
                            # print('problem in ',cnt,chn_c,dtt, dt0,t0,t1,prop['wf_samples'])

                            strt=np.argmin(abs(next_file['Log'][chn_c].time_track(absolute_time=True)-strt_t))
                            endd=np.argmin(abs(next_file['Log'][chn_c].time_track(absolute_time=True)-end_t))
                            
                            data= np.append(original_file['Log'][chn_c][:],next_file['Log'][chn_c][strt:endd])
                            prop=original_file['Log'][chn_c].properties
                            prop['wf_samples']=data.shape[0]
                            data=next_file['Log'][chn_c][strt:endd]
                            
                            channel_object = ChannelObject("Log", next_file['Log'][chn_c].name, \
                                                        data,\
                                                        properties=prop)
                            tdms_writer.write_segment([channel_object])    
                            
                    for chn_c in all_chn_lst_new_chn:
                        
                        
                        strt=np.argmin(abs(next_file['Log'][chn_c].time_track(absolute_time=True)-strt_t))
                        endd=np.argmin(abs(next_file['Log'][chn_c].time_track(absolute_time=True)-end_t))
                        prop=next_file['Log'][chn_c].properties
                        data=next_file['Log'][chn_c][strt:endd]
                        prop['wf_samples']=data.shape[0]
                        prop['wf_start_time']=max(tf_original)+prop['wf_increment']
                        
                        
                        channel_object = ChannelObject("Log", next_file['Log'][chn_c].name, \
                                                    data,\
                                                    properties=prop)
                        tdms_writer.write_segment([channel_object]) 
                        
                            
                original_file.close()
                            
    # tdms_writer.close()
                
#%%           
    return
#%%
      
for indx, row in Test_Log.iterrows():
    print(indx,row['Type_Test'],row['Test_Reference'])
    join_tdms(row['Test_Reference'])


#%%
sdsadss


for ch in all_chn_lst:
    for k in ft_files:
        ft_tdms_file = TdmsFile(os.path.join(ft_path,k))
        ft_log= ft_tdms_file['Log']

cnt_f=0
colmns=[]
colmns.append('channel')
st_t=[]
ft_t=[]
old_k=''
for k in ft_files:
    st=[]
    ft=[]
    try:
        ft_tdms_file = TdmsFile(os.path.join(ft_path,k))
        ft_log= ft_tdms_file['Log']
    except:
        print('error')
    colmns.append('st '+k)
    colmns.append('ft '+k)
    if cnt_f==0:
        
        ch_lst=[]
        ch_inc=[]
        for j in ft_log.channels():
            ch_lst.append(j.name)
            ch_inc.append(j.properties['wf_increment'])  
        df=pd.DataFrame(list(zip(ch_lst, ch_inc)),columns=['channel','wf_increment'])
    df['st '+k]=np.nan
    if cnt_f==1:
        df['delta_t '+k]=np.nan
    df['ft '+k]=np.nan
    for m in ch_lst:
        
        j=ft_log[m]
        df.loc[df['channel'] == m, ['st '+k]]=j.properties['wf_start_time']
        df.loc[df['channel'] == m, ['ft '+k]]=j.time_track(absolute_time=True)[-1]
    df['st '+k]=pd.to_datetime(df['st '+k])
    df['ft '+k]=pd.to_datetime(df['ft '+k])
    
    if cnt_f==1:
        print(k,old_k)
        df['delta_t '+k]=df['st '+k]-df['ft '+old_k]
        df['dif_inc '+k]=pd.to_timedelta(df['delta_t '+k]).dt.total_seconds()==df['wf_increment']
        print(df['dif_inc '+k].unique())    
    cnt_f=1
    old_k=k
        
    
#%%
cnt=0
for indx, row in Test_Log.iterrows():
    #Zero File
    if cnt==0 and row['Type_Test']== 'ZO':
        print(indx,row['Type_Test'],row['Test_Reference'])
        zero_fname=row['Test_Reference']
        zero_path=os.path.join(Main_Input,zero_fname)
        zero_files = [s for s in os.listdir(zero_path) if s.__contains__(".tdms") and not s.__contains__("_index")]
        zero_tdms_file = TdmsFile(os.path.join(zero_path,zero_files[0]))
        zero_log= zero_tdms_file['Log']
        cnt=+1
        continue
    elif cnt==0:
        print('Error start with ZERO FILE')
    else:
        print('Zero file is: ',zero_fname)
    
    if cnt>0:
        if row['Type_Test']== 'ZO':
            print(indx,row['Type_Test'],row['Test_Reference'])
            zero_fname=row['Test_Reference']
            zero_path=os.path.join(Main_Input,zero_fname)
            zero_files = [s for s in os.listdir(zero_path) if s.__contains__(".tdms") and not s.__contains__("_index")]
            zero_tdms_file = TdmsFile(os.path.join(zero_path,zero_files[0]))
            zero_log= zero_tdms_file['Log']
            cnt=+1
            print('Zero file is: ',zero_fname)
        elif row['Type_Test']== 'NF':
            nf_fname=row['Test_Reference']
            nf_path=os.path.join(Main_Input,nf_fname)
            nf_files = [s for s in os.listdir(nf_path) if s.__contains__(".tdms") and not s.__contains__("_index")]
            if len(nf_files)>1:
                print('Join Files')
            
sdsa
#%%

for i in zeros_test:
    zero_fname=Test_Log.at[i,'Test_Reference']
    zero_path=os.path.join(Main_Input,zero_fname)
    zero_files = [s for s in os.listdir(zero_path) if s.__contains__(".tdms") and not s.__contains__("_index")]
    zero_tdms_file = TdmsFile(os.path.join(zero_path,zero_files[0]))
    zero_log= zero_tdms_file['Log']
    
    # wi=[]
    # wf=[]
    
    # plt.figure()
    # for i in zero_log.channels():
    #     # print(i.name,i.properties['wf_start_time'])
    #     wi.append(i.properties['wf_start_time'])
    #     wf.append(i.time_track(absolute_time=True)[-1])
        
    #     plt.plot(i.time_track(absolute_time=True),i[:])
    # print((max(wi)-min(wi))/np.timedelta64(1, 's'))

#%%

for i in nf_test:
    try:
        nf_fname=Test_Log.at[i,'Test_Reference']
        nf_path=os.path.join(Main_Input,nf_fname)
        nf_files = [s for s in os.listdir(nf_path) if s.__contains__(".tdms") and not s.__contains__("_index")]
        nf_tdms_file = TdmsFile(os.path.join(nf_path,nf_files[0]))
        nf_log= nf_tdms_file['Log']
        print('work',i,nf_fname)
    except:
        nf_fname=Test_Log.at[i,'Test_Reference']
        print('error',i,nf_fname)

#%%  


for i in st_test:
    ft_fname=Test_Log.at[i,'Test_Reference']
    ft_path=os.path.join(Main_Input,ft_fname)
    ft_files = [s for s in os.listdir(ft_path) if s.__contains__(".tdms") and not s.__contains__("_index")]
    cnt_f=0
    colmns=[]
    colmns.append('channel')
    st_t=[]
    ft_t=[]
    old_k=''
    for k in ft_files:
        st=[]
        ft=[]
        try:
            ft_tdms_file = TdmsFile(os.path.join(ft_path,k))
            ft_log= ft_tdms_file['Log']
        except:
            print('error')
        colmns.append('st '+k)
        colmns.append('ft '+k)
        if cnt_f==0:
            
            ch_lst=[]
            ch_inc=[]
            for j in ft_log.channels():
                ch_lst.append(j.name)
                ch_inc.append(j.properties['wf_increment'])  
            df=pd.DataFrame(list(zip(ch_lst, ch_inc)),columns=['channel','wf_increment'])
        df['st '+k]=np.nan
        if cnt_f==1:
            df['delta_t '+k]=np.nan
        df['ft '+k]=np.nan
        for m in ch_lst:
            
            j=ft_log[m]
            df.loc[df['channel'] == m, ['st '+k]]=j.properties['wf_start_time']
            df.loc[df['channel'] == m, ['ft '+k]]=j.time_track(absolute_time=True)[-1]
        df['st '+k]=pd.to_datetime(df['st '+k])
        df['ft '+k]=pd.to_datetime(df['ft '+k])
        
        if cnt_f==1:
            print(k,old_k)
            df['delta_t '+k]=df['st '+k]-df['ft '+old_k]
            df['dif_inc '+k]=pd.to_timedelta(df['delta_t '+k]).dt.total_seconds()==df['wf_increment']
            print(df['dif_inc '+k].unique())    
        cnt_f=1
        old_k=k
                
df.to_excel('delta_static.xlsx')
            
            
        
asads
      
for i in st_test:
    ft_fname=Test_Log.at[i,'Test_Reference']
    ft_path=os.path.join(Main_Input,ft_fname)
    ft_files = [s for s in os.listdir(ft_path) if s.__contains__(".tdms") and not s.__contains__("_index")]
    for k in ft_files:
        wi=[]
        wf=[]
        wn=[]
        collect_meta=[]
        try:
            ft_tdms_file = TdmsFile(os.path.join(ft_path,k))
            ft_log= ft_tdms_file['Log']
            

            # print(ft_fname,k)
            # plt.figure()
            count=0
            for j in ft_log.channels():
                wn.append(j.name+k)
                # print(i.name,i.properties['wf_start_time'])
                try:
                    wi.append(j.properties['wf_start_time'])
                    wf.append(j.time_track(absolute_time=True)[-1])
                except:
                    print('No st_time ',ft_fname,k,j.name)
                    # wi.append(0)
                    # wf.append(0)
                    count+=1
                
            #     plt.plot(j.time_track(absolute_time=True),j[:])
            print(ft_fname,k,(max(wi)-min(wi))/np.timedelta64(1, 's'), 'No wf_t ',count) 

        except:
            print(ft_fname,k,' Error reading ')
        collect_meta.append(wn)
        collect_meta.append(wi)
        collect_meta.append(wf)