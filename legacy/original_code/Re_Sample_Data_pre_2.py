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

time_increment_seconds=0.5
absolut_time=0
time_increment=str(time_increment_seconds)+'S'

def join_tdms(fname):
    
#%%
    print(fname)
    Main_Output_file=os.path.join(Main_Output,fname)

    if not os.path.exists(Main_Output_file):
        os.makedirs(Main_Output_file)
    
    
    if os.path.exists(os.path.join(Main_Output_file,fname+'.xlsx')):
        print('File exist', fname)
        return
    

    ft_path=os.path.join(Main_Input,fname)
    # print(os.listdir(ft_path))

    #def Join_tdms(ft_path):
    ft_files = [s for s in os.listdir(ft_path) if s.__contains__(".tdms") and not s.__contains__("_index")]
    print('Total Files ',len(ft_files))
    ft_files.sort()
    
    cnt=0
    for k in ft_files:
        if cnt<1:
            file_name=os.path.join(Main_Output_file,fname+'_'+time_increment.replace('.','_'))
            file_name=file_name+ '.csv'
            with TdmsFile.open(os.path.join(ft_path,k)) as ft_tdms_file:
                all_chn_lst_or=[key for key in ft_tdms_file['Log']._channels]
                df = pd.DataFrame()
                cn_cnt=1
                for ch in all_chn_lst_or:
                    print(fname,ch,cn_cnt)
                    if absolut_time==1:
                        
                        df=pd.concat([df,ft_tdms_file['Log'][ch].as_dataframe(time_index=True, absolute_time=True).resample(time_increment).mean()])
                        cn_cnt=cn_cnt+1
                    else:
                        df2=ft_tdms_file['Log'][ch].as_dataframe(time_index=True, absolute_time=False)
                        # df2.index=[np.round(x,5) for x in df2.index]
                        df2.index = pd.TimedeltaIndex(df2.index, unit='s')
                        df2=df2.resample(time_increment).mean()
                        df=pd.concat([df, df2])
                        cn_cnt=cn_cnt+1
                        
            df.index=np.arange(0,df.shape[0]*time_increment_seconds,time_increment_seconds)
            print('Saving ',fname)
            df.to_csv(file_name) 
            cnt=cnt+1
        else:
            file_name=os.path.join(Main_Output_file,fname+'_'+time_increment.replace('.','_')+'_'+str(cnt))
            file_name=file_name+ '.csv'
            with TdmsFile.open(os.path.join(ft_path,k)) as ft_tdms_file:
                all_chn_lst_or=[key for key in ft_tdms_file['Log']._channels]
                df = pd.DataFrame()
                for ch in all_chn_lst_or:
                    print(fname,ch,cn_cnt)
                    if absolut_time==1:
                        
                        df=pd.concat([df,ft_tdms_file['Log'][ch].as_dataframe(time_index=True, absolute_time=True).resample(time_increment).mean()])
                        cn_cnt=cn_cnt+1
                    else:
                        df2=ft_tdms_file['Log'][ch].as_dataframe(time_index=True, absolute_time=False)
                        # df2.index=[np.round(x,5) for x in df2.index]
                        df2.index = pd.TimedeltaIndex(df2.index, unit='s')
                        df2=df2.resample(time_increment).mean()
                        df=pd.concat([df, df2])
                        cn_cnt=cn_cnt+1
                       
            df.index=np.arange(0,df.shape[0]*time_increment_seconds,time_increment_seconds)
            print('Saving ',fname)
            df.to_csv(file_name) 
            cnt=cnt+1
                    
   

             
#%%           
    return
#%%



# for indx, row in Test_Log.iterrows():
#     print(indx,row['Type_Test'],row['Test_Reference'])
#     join_tdms(row['Test_Reference'])
a=[x[0].split('\\')[-1] for x in os.walk(Main_Input) if 'LTD' in x[0].split('\\')[-1]]
for i in a:
    join_tdms(i)