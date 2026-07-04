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

strt='LTD_23A01_ZO_0029'

strt_ind=Test_Log.index[Test_Log.Test_Reference == strt]


Test_Log=Test_Log[strt_ind[0]:]

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
    # print(os.listdir(ft_path))

    #def Join_tdms(ft_path):
    ft_files = [s for s in os.listdir(ft_path) if s.__contains__(".tdms") and not s.__contains__("_index")]
    
    ft_files.sort()


    
    
    # print(ft_files)

    # df_ch=pd.DataFrame(data=None,columns=ft_files )
    all_chn_lst=[]

    #Get all the chnls
    cnt=0
    
    if len(ft_files)==0:
        
        print('No Files for fname')
        
        return

#%%   
    if len(ft_files)==1:
        
        shutil.copyfile(os.path.join(ft_path,ft_files[0]), os.path.join(Main_Output_file,fname+'.tdms'))
        
        return
    
    chan_control=1
    
    if chan_control==1:
    
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
            
        # else:
        #     with TdmsFile.open(os.path.join(ft_path,k)) as ft_tdms_file:
        #         ft_tdms_file = TdmsFile(os.path.join(ft_path,k))
        #         ft_log= ft_tdms_file['Log']
                # all_chn_lst.extend([key for key in ft_log._channels])
            
        all_chn_lst.sort()
        
        del ft_tdms_file, ft_log
    


#%%      
    cnt=0
    cnt_2=0
    fname_or=fname
    cnt_3=0
    
    with TdmsWriter(os.path.join(Main_Output_file,fname+'.tdms')) as tdms_writer: 
    
        for k in ft_files:
            
            print(k,cnt_3,cnt_2,cnt)
            cnt_3+=1
            
            
            
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
                # end_t=min(end_times)

                # print(max(end_times),min(end_times))
                # print('first file')
                for chn_c in all_chn_lst:                    

                        
                    # print('problem in ',cnt,chn_c,dtt, dt0,t0,t1,prop['wf_samples'])

                    # strt=np.argmin(abs(original_file['Log'][chn_c].time_track(absolute_time=True)-strt_t))
                    # endd=np.argmin(np.abs(original_file['Log'][chn_c].time_track(absolute_time=True)-end_t))
                    
                    
                    data=original_file['Log'][chn_c].data#[strt:endd]
                    prop=original_file['Log'][chn_c].properties
                    prop['wf_samples']=data.shape[0]
                    prop['wf_start_time']=original_file['Log'][chn_c].time_track(absolute_time=True)[0]
                    
                    channel_object = ChannelObject("Log", original_file['Log'][chn_c].name, \
                                                data,\
                                                properties=prop)
                    tdms_writer.write_segment([channel_object]) 
                    
                    # tf_original.append(original_file['Log'][chn_c].time_track(absolute_time=True)[-1])

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
                    # strt_t=max(strt_times)
                    # end_t=min(end_times)
                    
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
                            print('files non consecutive')
                            pause_file=1
                    
                    # print(strt_t,end_t,pd.to_timedelta(strt_t-end_t).total_seconds())
                    # print(max(tf_original),min(tf_original),pd.to_timedelta(max(tf_original)-min(tf_original)).total_seconds())
                    
                    if pause_file==1:
                        
                        print('Pause file',k)
                        cnt_2=cnt_2+1
                        fname=fname_or+'_'+str(cnt_2)
                    else:
                        print('No Pause File')
                        
                        
                    if pause_file==0:
                        
                        with TdmsWriter(os.path.join(Main_Output_file,fname+'.tdms'), mode='a') as tdms_writer: 
                    

                            for chn_c in all_chn_lst_cmn:
                                
                                dt0=original_file['Log'][chn_c].properties['wf_increment']
                                dt1=next_file['Log'][chn_c].properties['wf_increment']
                                
                                
                                t0=original_file['Log'][chn_c].time_track(absolute_time=True)[-1]
                                t1=next_file['Log'][chn_c].properties['wf_start_time']
                                dtt=pd.to_timedelta(t1-t0).total_seconds()
                                
                                
                                
                                if dt0==dt1 and dtt==dt0:
                                
                                    data= np.append(original_file['Log'][chn_c][:],next_file['Log'][chn_c][:])
                                    prop=original_file['Log'][chn_c].properties
                                    prop['wf_samples']=data.shape[0]
                                    data=next_file['Log'][chn_c][:]
                                    
                                    
                                    channel_object = ChannelObject("Log", next_file['Log'][chn_c].name, \
                                                                data,\
                                                                properties=prop)
                                    tdms_writer.write_segment([channel_object])
    
    
                                    
                            for chn_c in all_chn_lst_new_chn:
                                
                                
                                strt=np.argmin(abs(next_file['Log'][chn_c].time_track(absolute_time=True)-strt_t))
                                # endd=np.argmin(abs(next_file['Log'][chn_c].time_track(absolute_time=True)-end_t))
                                prop=next_file['Log'][chn_c].properties
                                data=next_file['Log'][chn_c][strt:]
                                prop['wf_samples']=data.shape[0]
                                prop['wf_start_time']=max(tf_original)+prop['wf_increment']
                                
                                
                                channel_object = ChannelObject("Log", next_file['Log'][chn_c].name, \
                                                            data,\
                                                            properties=prop)
                                tdms_writer.write_segment([channel_object]) 
                                
                                    
                            original_file.close()
                    
                    else:
                        
                        # tdms_writer.close()
                        with TdmsWriter(os.path.join(Main_Output_file,fname+'.tdms')) as tdms_writer:
                            

                                
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
                                    # end_times.append(original_file['Log'][ch].time_track(absolute_time=True)[-1])
                                strt_t=max(strt_times)
                                # end_t=min(end_times)

                                # print(max(end_times),min(end_times))
                                print('first file',cnt_2)
                                for chn_c in all_chn_lst:                    

                                        
                                    # print('problem in ',cnt,chn_c,dtt, dt0,t0,t1,prop['wf_samples'])

                                    strt=np.argmin(abs(original_file['Log'][chn_c].time_track(absolute_time=True)-strt_t))
                                    # endd=np.argmin(np.abs(original_file['Log'][chn_c].time_track(absolute_time=True)-end_t))
                                    
                                    
                                    data=original_file['Log'][chn_c][strt:]
                                    prop=original_file['Log'][chn_c].properties
                                    prop['wf_samples']=data.shape[0]
                                    prop['wf_start_time']=original_file['Log'][chn_c].time_track(absolute_time=True)[strt]
                                    
                                    channel_object = ChannelObject("Log", original_file['Log'][chn_c].name, \
                                                                data,\
                                                                properties=prop)
                                    tdms_writer.write_segment([channel_object]) 
                                    
                                    # tf_original.append(original_file['Log'][chn_c].time_track(absolute_time=True)[endd])
             
                        
                            
    # tdms_writer.close()


             
#%%           
    return
#%%
      
for indx, row in Test_Log.iterrows():
    print(indx,row['Type_Test'],row['Test_Reference'])
    join_tdms(row['Test_Reference'])

