# -*- coding: utf-8 -*-
"""
Created on Mon Jun 27 10:41:35 2022

@author: slopezd
"""

print('Run Test Process')


from nptdms import TdmsFile
import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks
from scipy.fft import rfft, rfftfreq,   fft, fftfreq
import statistics
from skimage.restoration import denoise_wavelet, estimate_sigma, cycle_spin
import pywt
import re
import pickle
#%%
#Rear Main file
fname='Loadtide_Test_Log.xlsx'
#%%

DO_NF=0
DO_ST=0
DO_FA=1


#%%
print('start')
##working Paths
Path_Code=os.path.abspath(os.getcwd())
os.chdir("..")
Main_Path=os.path.abspath(os.curdir)
Main_Input=os.path.join(Main_Path,'Join_Data')
Main_Output=os.path.join(Main_Path,'Process_Data')
Main_Results=os.path.join(Main_Path,'Results')
Main_NF=os.path.join(Main_Results,'Natural_Frequency')
Main_ST=os.path.join(Main_Results,'Static')
Main_FT=os.path.join(Main_Results,'Fatigue')


#%%
#Check folders
Dir_check=[Main_Output,Main_Results,Main_NF,Main_ST,Main_FT]
# 
dist_act=np.array([2.2751, 3.56, 4.477])

for i in Dir_check:
    if not os.path.exists(i):
        os.makedirs(i)

#%%
#Rear Main file
# Test_Log= pd.read_excel(os.path.join(Main_Path,fname),sheet_name='Test_Log')
# Test_Log.dropna(subset = ["Date_start"], inplace=True)


# strt='LTD_23A01_ZO_0040'
# strt_ind=Test_Log.index[Test_Log.Test_Reference == strt]
# Test_Log=Test_Log[strt_ind[0]:]


tests_dir=[x[0].split('\\')[-1] for x in os.walk(Main_Input)][1:]
tests_n=[int(x.split('_')[-1]) for x in tests_dir]

tests_dir = [x for _,x in sorted(zip(tests_n,tests_dir))]

###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################FATIGUE ########################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
f_fname='LTD_23A01_FA_0049'
f_path=os.path.join(Main_Input,f_fname)
ft_files = [s for s in os.listdir(f_path) if s.__contains__(".tdms") and not s.__contains__("_index")]
cnt2=0

for ffiles in ft_files:
    cnt=0
    fatgigue_data={}
    
    filt_lev=6
    
    with TdmsFile.open(os.path.join(f_path,ffiles)) as tdms_file:
    #tdms_file = TdmsFile(os.path.join(f_path,f_fname+'.tdms'))
        all_lds_lst=[key for key in tdms_file['Log']._channels]
        ld=tdms_file['Log']['Load_A02_PVE_Filter'][:]
        tm_ld=tdms_file['Log']['Load_A02_PVE_Filter'].time_track(absolute_time=True)
        pos=tdms_file['Log']['Pos_S_Cent_Filter'][:]
        tm_pos=tdms_file['Log']['Pos_S_Cent_Filter'].time_track(absolute_time=True)
        
        
        peaks_up, _ = find_peaks(ld,prominence=30)
        peaks_up_2, _ = find_peaks(pos,prominence=10)
        print(len(peaks_up),len(peaks_up_2))
        
        
        plt.figure()
        plt.plot(tm_ld,ld)
        plt.plot(tm_ld[peaks_up],ld[peaks_up],'x')
        plt.plot(tm_pos,pos*3.3)
        plt.plot(tm_pos[peaks_up_2],pos[peaks_up_2]*3.3)
        
        plt.figure()
        plt.plot(ld[peaks_up],pos[peaks_up_2],'.')
        
        
        
        