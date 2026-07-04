# -*- coding: utf-8 -*-
"""
Created on Tue Feb 14 11:28:15 2023

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
import decimal
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

# check=1
# if check==1:
    
#     for indx, row in Test_Log.iterrows():
#         print(indx,row['Type_Test'],row['Test_Reference'])
        
#         # Main_Iutput_file=os.path.join(Main_Output,fname)
        
#         fname=row['Test_Reference']
        
#         ft_path=os.path.join(Main_Output,fname)
        
ft_path='C:\path\to\test_data\Second_Campaign_3_Actuator\\Test Data\\LTD_23A01_ST_0037'
# print(os.listdir(ft_path))

#def Join_tdms(ft_path):
ft_files = [s for s in os.listdir(ft_path) if s.__contains__(".tdms") and not s.__contains__("_index")]

ft_files.sort()

#%%

# if len(ft_files)==2:

# cnt=0

# for j in range(len(ft_files)):
    
#     k0=ft_files[j]
#     k1=ft_files[j+1]
    
    # print(k0,k1)
    
k0='C:\path\to\test_data\Second_Campaign_3_Actuator\\Join_Data\\LTD_23A01_FA_0033\\LTD_23A01_FA_0033.tdms'
k1='C:\path\to\test_data\Second_Campaign_3_Actuator\\Join_Data\\LTD_23A01_FA_0035\\LTD_23A01_FA_0035.tdms'


# for k in ft_files:
    
    # print(k,cnt_3)
    # cnt_3+=1



    
cnt=+1
# original_file = TdmsFile(os.path.join(ft_path,k0))


with TdmsFile.open(k0) as original_file:

    # original_file = TdmsFile(k0)
    
    
    # original_groups = original_file.groups()
    # root_object = RootObject(original_file.properties)
    
    
    # tdms_writer.write_segment([root_object] + original_groups)
    
    all_chn_lst=[key for key in original_file['Log']._channels]

    strt_times=[]
    end_times=[]
    tf_original=[]
    log_freq=[]
    
    for ch in all_chn_lst:
        # strt_times.append(original_file['Log'][ch].properties['wf_start_time'])
        if original_file['Log'][ch].properties['wf_increment']>0.004:
            end_times.append(original_file['Log'][ch].time_track(absolute_time=True)[-31])
#         log_freq.append(original_file['Log'][ch].properties['wf_increment'])
#         # d_point1 = decimal.Decimal(original_file['Log'][ch].properties['wf_increment'])
#         # d_round1=-1*d_point1.as_tuple().exponent
#         # print(d_round1)
        
#     # strt_t=max(strt_times)
#     # end_t=min(end_times)

#     # print(max(end_times),min(end_times))
#     # print('first file')
    
#     # with TdmsFile.open(os.path.join(ft_path,ft_files[1])) as second_file:
    
    
    
    
    min_first_f=min(end_times)
    
    # endd=np.argmin(abs(original_file['Log']['Load_A02_PVE'].time_track(absolute_time=True)-min_first_f))
    # plt.plot(original_file['Log']['Load_A02_PVE'].time_track(absolute_time=True)[:endd],original_file['Log']['Load_A02_PVE'][:endd])
    # plt.plot(original_file['Log']['Temp_S_B_01'].time_track(absolute_time=True)[:],original_file['Log']['Temp_S_B_01'][:],'x')
   
    # asd
    
    # cn=all_chn_lst[np.argmin(end_times)]
    # min_first_f=original_file['Log'][ch].time_track(absolute_time=True)[-2]
#     end_times_first=[]
#     for ld_ch in all_chn_lst:
#         stc_start=original_file['Log'][ld_ch].time_track(absolute_time=True)[np.argmin(abs(original_file['Log'][ld_ch].time_track(absolute_time=True)-min_first_f))]
#         end_times_first.append(stc_start)


#     print('second')
# second_file=TdmsFile.read_metadata(k1)
# 
# # second_file = TdmsFile(k1)

# # all_chn_lst2=[key for key in original_file['Log']._channels]


with TdmsFile.open(k1) as second_file:
    # second_file = TdmsFile(k1)
    strt_times2=[]
#     end_times2=[]
#     tf_original2=[]
#     log_freq2=[]
    
    for ch in all_chn_lst:
        if second_file['Log'][ch].properties['wf_increment']>0.004:
            
            strt_times2.append(second_file['Log'][ch].time_track(absolute_time=True)[10])
#         # end_times2.append(second_file['Log'][ch].time_track(absolute_time=True)[-1])
#         log_freq2.append(second_file['Log'][ch].properties['wf_increment'])
    
    
    max_secnd_f=max(strt_times2)
#     frst_times_scndf=[]
#     for ld_ch in all_chn_lst:
#         stc_start=second_file['Log'][ld_ch].time_track(absolute_time=True)[np.argmin(abs(second_file['Log'][ld_ch].time_track(absolute_time=True)-max_secnd_f))]
#         frst_times_scndf.append(stc_start)



#     num_samp_j=[]

#     for i in range(len(strt_times2)):
#        num_samp_j.append( ((frst_times_scndf[i]-end_times_first[i])/ np.timedelta64(1, 's'))/log_freq[i])
    


k2='C:\path\to\test_data\Second_Campaign_3_Actuator\\Process_Data\\Fatigue\\LTD_23A01_FA.tdms'

z0='C:\path\to\test_data\Second_Campaign_3_Actuator\\Join_Data\\LTD_23A01_ZO_0031\\LTD_23A01_ZO_0031.tdms'
z1='C:\path\to\test_data\Second_Campaign_3_Actuator\\Join_Data\\LTD_23A01_ZO_0034\\LTD_23A01_ZO_0034.tdms'

zero_tdms_file0 = TdmsFile(z0)
zero_tdms_file1 = TdmsFile(z1)


with TdmsWriter(k2) as tdms_writer: 
    
    with TdmsFile.open(k0) as original_file:
    
    
        original_groups = original_file.groups()
        root_object = RootObject(original_file.properties)
        tdms_writer.write_segment([root_object] + original_groups)
        
        
        for chn_c in all_chn_lst:                    

                
            # print('problem in ',cnt,chn_c,dtt, dt0,t0,t1,prop['wf_samples'])

            # strt=np.argmin(abs(original_file['Log'][chn_c].time_track(absolute_time=True)-strt_t))
            # endd=np.argmin(np.abs(original_file['Log'][chn_c].time_track(absolute_time=True)-end_t))
            
            
            
            
            endd=np.argmin(abs(original_file['Log'][chn_c].time_track(absolute_time=True)-min_first_f))
            
            if 'Temp'in chn_c:
                data=original_file['Log'][chn_c][:endd]
            else:
                data=original_file['Log'][chn_c][:endd]-np.mean(zero_tdms_file0['Log'][chn_c][:])
            prop=original_file['Log'][chn_c].properties
            prop['wf_samples']=data.shape[0]
            prop['wf_start_time']=original_file['Log'][chn_c].time_track(absolute_time=True)[0]
            
            channel_object = ChannelObject("Log", original_file['Log'][chn_c].name, \
                                        data,\
                                        properties=prop)
            tdms_writer.write_segment([channel_object]) 
            print(chn_c)
            # tf_original.append(original_file['Log'][chn_c].time_track(absolute_time=True)[-1])

        original_file.close()
        
    
    
    with TdmsFile.open(k2) as original_file:
    
    
        with TdmsWriter(k2, mode='a') as tdms_writer: 
            
            with TdmsFile.open(k1) as second_file:
    

                for chn_c in all_chn_lst:

                    
                    strtt=np.argmin(abs(second_file['Log'][chn_c].time_track(absolute_time=True)-max_secnd_f))
                    
                    
                    
                    data= np.append(original_file['Log'][chn_c][:],second_file['Log'][chn_c][strtt:])
                    prop=original_file['Log'][chn_c].properties
                    prop['wf_samples']=data.shape[0]
                    
                    if 'Temp'in chn_c:
                        data=second_file['Log'][chn_c][strtt:]
                    else:
                        data=second_file['Log'][chn_c][strtt:]-np.mean(zero_tdms_file1['Log'][chn_c][:])
                    
                    
                    channel_object = ChannelObject("Log", second_file['Log'][chn_c].name, \
                                                data,\
                                                properties=prop)
                    tdms_writer.write_segment([channel_object])
                    print(chn_c)
            
            original_file.close()
        original_file.close()



asfsf
#     diff=[]

#     for i in range(len(strt_times2)):
#         diff.append((strt_times2[i]-end_times[i])/ np.timedelta64(1, 's'))

#     num_samp=[]
#     for i in range(len(strt_times2)):
#         num_samp.append(diff[i]/log_freq[i])
    
#     for i in num_samp:
#         if i != 1:
#             print('error')
#             adsadsa
    



# # 
#     sdasd