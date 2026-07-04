# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 09:23:41 2022

@author: slopezd
"""

print('Run Test Process')

from nptdms import TdmsFile
import pandas as pd
import os
import numpy as np
import sys
from nptdms import TdmsFile, TdmsWriter, RootObject, ChannelObject, GroupObject
import shutil
#%%

# import time
# print("Pause")
# time.sleep(60*60*4)    # Pause 5.5 seconds
# print("Finish Pause")
#%%
print('start')
##working Paths
Path_Code=os.path.abspath(os.getcwd())
os.chdir("..")
Main_Path=os.path.abspath(os.curdir)
Main_Input=os.path.join(Main_Path,'Join_Data')
Main_Output=os.path.join(Main_Path,'Re_Sample_Data')

#%%
### JOIN FILES

# cnt=0
# #Verify against first file
# # if len(list(set(all_chn_lst_1).intersection(all_chn_lst))) != len(all_chn_lst):
# #     print('Not same Channels, write code to solve')
# #     sys.exit()

time_increment='0.5S'
absolut_time=0


def join_tdms(fname):
    
#%%
    print(fname)
    Main_Output_file=os.path.join(Main_Output,fname)

    if not os.path.exists(Main_Output_file):
        os.makedirs(Main_Output_file)
    
    
    if os.path.exists(os.path.join(Main_Output_file,fname+'.xlsx')):
        print('File exist', fname)
        # return
    

    ft_path=os.path.join(Main_Input,fname)
    # print(os.listdir(ft_path))

    #def Join_tdms(ft_path):
    ft_files = [s for s in os.listdir(ft_path) if s.__contains__(".tdms") and not s.__contains__("_index")]
    print('Total Files ',len(ft_files))
    ft_files.sort()
    
    cnt=0
    for k in ft_files:
        if cnt<1:
            file_name=os.path.join(Main_Output_file,fname+'.xlsx')
            with TdmsFile.open(os.path.join(ft_path,k)) as ft_tdms_file:
                if absolut_time==1:
                    df=ft_tdms_file.as_dataframe(time_index=True, absolute_time=True).resample(time_increment).mean().to_excel(file_name)
                else:
                    df=ft_tdms_file.as_dataframe(time_index=True, absolute_time=False)
                    df.index = pd.TimedeltaIndex(df.index, unit='s')
                    df=df.resample(time_increment).mean()
                    df.index=df.index/ np.timedelta64(1, 's')
                    df.to_excel(file_name)
            cnt=cnt+1
        else:
            file_name=os.path.join(Main_Output_file,fname+'_'+str(cnt)+'.xlsx')
            with TdmsFile.open(os.path.join(ft_path,k)) as ft_tdms_file:
                if absolut_time==1:
                    df=ft_tdms_file.as_dataframe(time_index=True, absolute_time=True).resample(time_increment).mean().to_excel(file_name)
                else:
                    df=ft_tdms_file.as_dataframe(time_index=True, absolute_time=False)
                    df.index = pd.TimedeltaIndex(df.index, unit='s')
                    df=df.resample(time_increment).mean()
                    df.index=df.index/ np.timedelta64(1, 's')
                    df.to_excel(file_name)
   

             
#%%           
    return
#%%



# for indx, row in Test_Log.iterrows():
#     print(indx,row['Type_Test'],row['Test_Reference'])
#     join_tdms(row['Test_Reference'])
a=[x[0].split('\\')[-1] for x in os.walk(Main_Input) if 'LTD' in x[0].split('\\')[-1]]
for i in a:
    join_tdms(i)