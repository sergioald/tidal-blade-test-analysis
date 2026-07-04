# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 18:18:34 2023

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
Main_Input=os.path.join(Main_Path,'Process_Data')
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


        
# ft_path='C:\path\to\test_data\Second_Campaign_3_Actuator\\Test Data\\LTD_23A01_ST_0030'
# print(os.listdir(ft_path))
ft_path='C:\path\to\test_data\Second_Campaign_3_Actuator\\Process_Data\\Fatigue'


# ft_path='C:\path\to\test_data\Second_Campaign_3_Actuator\\Join_Data\\LTD_23A01_ST_0030'



#def Join_tdms(ft_path):
ft_files = [s for s in os.listdir(ft_path) if s.__contains__(".tdms") and not s.__contains__("_index")]

ft_files.sort()

#%%

# if len(ft_files)==2:

cnt=0

dif1=0
dif2=0
dift=0
for j in range(len(ft_files)):
    
    k0=ft_files[j]
    # k1=ft_files[j+1]
    
    k0=os.path.join(ft_path,k0)
    
    chn=['Load_A_01','Load_A_01_PVE','Load_A_01_PVE_Filter']
    
    chn=['Load_A_01','Pos_S_Cent','Pos_S_Tip']
    
    # chn=['Load_A_01_PVE','Pos_S_Cent','Pos_S_Tip']
    
    
    with TdmsFile.open(k0) as original_file:
        
        l0=len(original_file['Log'][chn[0]][:])
        l1=len(original_file['Log'][chn[1]][:])
        l2=len(original_file['Log'][chn[2]][:])
        
        dift=dift+original_file['Log'][chn[0]].properties['wf_start_time']-original_file['Log'][chn[1]].properties['wf_start_time']
        
        dif1=dif1+l0-l1
        dif2=dif2+l0-l2
        
        print(l0,l0-l1,l0-l2,j)
        
        
    
        
print(dif1,dif2,dift/ np.timedelta64(1, 's'))
            
                