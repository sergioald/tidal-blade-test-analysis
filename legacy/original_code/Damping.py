# -*- coding: utf-8 -*-
"""
Created on Mon Aug 29 14:46:59 2022

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
from scipy.signal import find_peaks
from skimage.restoration import (denoise_wavelet, estimate_sigma)



test2=['LTD_22A01_NF_0002','LTD_22A01_NF_0003','LTD_22A01_NF_0004']

# test2=['LTD_22A01_NF_0026','LTD_22A01_NF_0027','LTD_22A01_NF_0028']

for test in test2:
# test='LTD_22A01_NF_0028'
    zf='LTD_22A01_ZO_0001'
    
    path_nf="C:\path\to\test_data\Join_Data\\"+test+"\\"+test+".tdms"
    path_zf="C:\path\to\test_data\Join_Data\\"+zf+"\\"+zf+".tdms"
    
    
    
    tdms_file = TdmsFile(path_nf)
    zero_tdms_file = TdmsFile(path_zf)
    #Get Accelerometers
    all_acc_lst=[key for key in tdms_file['Log']._channels if key.__contains__("Acc_S") ]
    
    all_acc_lst_z=[key for key in all_acc_lst if key.__contains__("_Z") ]
    
    
    acc=all_acc_lst_z[0]
    
    Acc_NF=tdms_file['Log'][acc][:]-np.mean(zero_tdms_file['Log'][acc][:])
    time=tdms_file['Log'][acc].time_track(absolute_time=True)
    xo=np.max(Acc_NF)
    
    sigma_est = estimate_sigma(Acc_NF, average_sigmas=True)
    tot_load=denoise_wavelet(Acc_NF, method='VisuShrink', mode='soft',  
                           wavelet='sym9', 
                           sigma=sigma_est/4,
                           rescale_sigma='True')
    
    tot_load[tot_load<0]=0
    
    peaks, _ = find_peaks(tot_load,height=0.2,distance=5)
    
    
    
    
    peaks=peaks[peaks>np.argmax(tot_load)]
    
    plt.figure()
    # plt.plot(time,Acc_NF,'.')
    plt.plot(time,Acc_NF)
    # plt.plot(time,tot_load)
    plt.plot(time[peaks],Acc_NF[peaks],'x')
    
    cnt=1
    delta=[]
    sigma=[]
    for i in peaks:
        delt=(1/cnt)*(np.log(xo)/np.log(Acc_NF[i]))
        # delt=(1/cnt)*np.log(((xo)/(Acc_NF[i])))
        sigm=1/np.sqrt(1+(((2*np.pi)/delt)**2))
        cnt=cnt+1
        delta.append(delt)
        sigma.append(sigm)
    plt.figure()
    plt.plot(sigma)
    plt.ylabel('Damping Ratio')
    plt.xlabel("Oscillations")
    plt.title(test+'_'+acc)
    
    
    print(np.mean(sigma[120:]))