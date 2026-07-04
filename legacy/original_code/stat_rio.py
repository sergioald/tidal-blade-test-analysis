# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 10:56:47 2022

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
import statistics
test='LTD_22A01_ST_0020'

path_rio="C:\path\to\test_data\Test Data\\"+test+"\\RIO Data\\"+test+".tdms"
path_stc="C:\path\to\test_data\Join_Data\\"+test+"\\"+test+".tdms"

stc_tdms_file = TdmsFile(path_stc)
print('STC')
rio_tdms_file = TdmsFile(path_rio)

all_lds_lst=[key for key in stc_tdms_file['Log']._channels if key.__contains__("Load_A") ]
var=all_lds_lst[1]

#%%
st=85000
dt=13.9
plt.figure()
plt.plot(stc_tdms_file['Log'][var].time_track(accuracy='s')[:],stc_tdms_file['Log'][var][:])
plt.plot(rio_tdms_file['General Logging']['Time elapsed since test start (seconds)'][st:]+dt,rio_tdms_file['General Logging']['Load Cell 1 (kN)'][st:],'k')


#%%   
plt.figure()  
plt.plot(stc_tdms_file['Log'][var][:])
plt.plot(rio_tdms_file['General Logging']['Load Cell 1 (kN)'][st:],'k')

#%% 
plt.figure()
plt.plot(rio_tdms_file['General Logging']['Time elapsed since test start (seconds)'][st:]+0,rio_tdms_file['General Logging']['Load Cell 1 (kN)'][st:],'k')
plt.plot(rio_tdms_file['General Logging']['Time elapsed since test start (seconds)'][st:]+0,rio_tdms_file['General Logging']['Desired Y Value'][st:])


#%%

load_rio=rio_tdms_file['General Logging']['Load Cell 1 (kN)'][st:]
tm_rio=rio_tdms_file['General Logging']['Time elapsed since test start (seconds)'][st:]+dt
targ_load=statistics.mode(load_rio.astype(int))
wh=np.where(load_rio.astype(int)==targ_load)

print('rio mean: ',np.mean(load_rio[wh[0][0]:wh[0][-1]]))

stc_start=np.argmin(np.abs(stc_tdms_file['Log'][var].time_track()-tm_rio[wh[0][0]]))
stc_end=np.argmin(np.abs(stc_tdms_file['Log'][var].time_track()-tm_rio[wh[0][-1]]))

print('other mean: ',np.mean(stc_tdms_file['Log'][var][stc_start:stc_end]))

cf=np.mean(load_rio[wh[0][0]:wh[0][-1]])/np.mean(stc_tdms_file['Log'][var][stc_start:stc_end])
print('Correction Factor = ',cf)

plt.figure()

plt.plot(stc_tdms_file['Log'][var][stc_start:stc_end])
plt.plot(load_rio[wh[0][0]:wh[0][-1]])

plt.figure()

plt.plot(stc_tdms_file['Log'][var][stc_start:stc_end])
plt.plot(stc_tdms_file['Log'][var][stc_start:stc_end]*cf)
plt.plot(load_rio[wh[0][0]:wh[0][-1]],'k')