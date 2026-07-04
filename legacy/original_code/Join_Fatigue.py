# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 11:57:56 2023

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
from scipy import fftpack
from scipy.signal import find_peaks
from scipy.fft import rfft, rfftfreq,   fft, fftfreq
from scipy import signal
import statistics
from skimage.restoration import (denoise_wavelet, estimate_sigma)
import pywt
import re
from scipy.interpolate import make_interp_spline, BSpline
#%%
#Rear Main file
fname='Loadtide_Test_Log.xlsx'
#%%

DO_NF=0
DO_ST=1
DO_FA=0


if DO_FA==1:
    fatgigue_data={}

#%%
print('start')
##working Paths
Path_Code=os.path.abspath(os.getcwd())
os.chdir("..")
Main_Path=os.path.abspath(os.curdir)
Main_Input=os.path.join(Main_Path,'Join_Data')
Main_Output=os.path.join(Main_Path,'Process_Data')
# Main_Results=os.path.join(Main_Path,'Results')
# Main_NF=os.path.join(Main_Results,'Natural_Frequency')
# Main_ST=os.path.join(Main_Results,'Static')
# Main_FT=os.path.join(Main_Results,'Fatigue')
Main_Join_FT=os.path.join(Main_Output,'Fatigue')


#%%
#Check folders
# Dir_check=[Main_Output,Main_Results,Main_NF,Main_ST,Main_FT]
Dir_check=[Main_Output,Main_Join_FT]
# 
dist_act=np.array([2.2751, 3.56, 4.477])

for i in Dir_check:
    if not os.path.exists(i):
        os.makedirs(i)
#%%
#Rear Main file
Test_Log= pd.read_excel(os.path.join(Main_Path,fname),sheet_name='Test_Log')
Test_Log.dropna(subset = ["Date_start"], inplace=True)
strt='LTD_23A01_ZO_0029'

strt_ind=Test_Log.index[Test_Log.Test_Reference == strt]


Test_Log=Test_Log[strt_ind[0]:]

#%%
#Rear Main file
Test_Log= pd.read_excel(os.path.join(Main_Path,fname),sheet_name='Test_Log')
Test_Log.dropna(subset = ["Date_start"], inplace=True)
strt='LTD_23A01_ZO_0029'

strt_ind=Test_Log.index[Test_Log.Test_Reference == strt]


Test_Log=Test_Log[strt_ind[0]:]
#%%
#Start process
cnt=0
DO_FA=1
for indx, row in Test_Log.iterrows():
    print(indx,row['Type_Test'],row['Test_Reference'])
    f_fname=row['Test_Reference']
    f_path=os.path.join(Main_Input,f_fname)
    if row['Type_Test']=='ZO':
        print('Reading Zero File')
        zero_tdms_file = TdmsFile(os.path.join(f_path,f_fname+'.tdms'))
        continue
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
    if row['Type_Test']=='FA':
        if DO_FA==1:
            
            f_name_s=f_fname.split("_")[0]+"_"+f_fname.split("_")[1]+"_FA"
            f_name_s_f=os.path.join(Main_Join_FT,f_name_s+".pickle")
            
            if os.path.exists(f_name_s_f):
                continue
            
            print('Reading Fatigue File')
            ft_files = [s for s in os.listdir(f_path) if s.__contains__(".tdms") and not s.__contains__("_index")]
            cnt2=0
            print(ft_files)
            for ffiles in ft_files:
                
                if cnt2==0:
                    
                    ffiles=f_fname+'.tdms'
                    cnt2=cnt2+1
                else:
                    ffiles=f_fname+'_'+str(cnt2)+'.tdms'
                    cnt2=cnt2+1
                    
                print(ffiles)
                with TdmsFile.open(os.path.join(f_path,ffiles)) as tdms_file:
                #tdms_file = TdmsFile(os.path.join(f_path,f_fname+'.tdms'))
                    
                    all_lds_lst=[key for key in tdms_file['Log']._channels if key.__contains__("Load_A") and not key.__contains__("_PVE")]
                    
                    print(all_lds_lst)
                    
                    ld_ch=all_lds_lst[0]
                    
                    tot_load=(tdms_file['Log'][ld_ch][:]-np.mean(zero_tdms_file['Log'][ld_ch][:]))
                    
                    if np.mean(tot_load)<0:
                        tot_load=tot_load*-1
                    
                    
                    plt.figure()
                    plt.plot(tot_load)
                    
                    sigma_est = estimate_sigma(tot_load, average_sigmas=True)
                    tot_load=denoise_wavelet(tot_load, method='VisuShrink', mode='soft',  
                                           wavelet='sym9', 
                                           sigma=sigma_est*5,
                                           rescale_sigma='True')
                    
                    peaks_up, _ = find_peaks(tot_load, prominence=(35))
                    peaks_dwn, _ = find_peaks(tot_load*-1, prominence=(35))
                    
                    


                    # plt.figure()
                    # contour_heights = tot_load[peaks_up] - properties['prominences']
                    plt.plot(tot_load)
                    plt.plot(peaks_up, tot_load[peaks_up], "x")
                    plt.plot(peaks_dwn, tot_load[peaks_dwn], "o")
                    # plt.vlines(x=peaks_up, ymin=contour_heights, ymax=tot_load[peaks_up])
                    plt.show()

                    
                    continue
                    
                    if len(all_lds_lst)==0:
                        print('No Load: ',f_fname)
                        continue
                    
                    ld_ch='Load_A_01_PVE'
                    tot_load=tdms_file['Log'][ld_ch][:]-np.mean(zero_tdms_file['Log'][ld_ch][:])*0.994
                    

                    
                    sigma_est = estimate_sigma(tot_load, average_sigmas=True)
                    tot_load=denoise_wavelet(tot_load, method='VisuShrink', mode='soft',  
                                           wavelet='sym9', 
                                           sigma=sigma_est/0.5,
                                           rescale_sigma='True')
                    
                    peaks_up, _ = find_peaks(tot_load, prominence=(70))
                    peaks_dwn, _ = find_peaks(tot_load*-1, prominence=(70))
                    
                    

                    # fatgigue_data[ld_ch].extend(tot_load)
                    
                     
                    # plt.figure()
                    # contour_heights = tot_load[peaks_up] - properties['prominences']
                    # plt.plot(tot_load,c='k')
                    # plt.plot(peaks, tot_load[peaks], "x")
                    # plt.vlines(x=peaks_up, ymin=contour_heights, ymax=tot_load[peaks_up])
                    # plt.show()
                    
                    if int(len(peaks_up)-len(peaks_dwn))==1:
                        if peaks_up[0]<peaks_dwn[0]:
                            print('ENTER')
                            peaks_all=np.sort(np.concatenate((peaks_up,peaks_dwn)))
                            time_all=tdms_file['Log'][ld_ch].time_track(absolute_time=True,accuracy='ms')[peaks_all]
                            dif1=tot_load[peaks_up[:-1]]-tot_load[peaks_dwn]
                            dif2=tot_load[peaks_up[1:]]-tot_load[peaks_dwn]
                            Load_Diff=0.5*(dif1+dif2)
                            tot_load_max=tot_load[peaks_up]
                            tot_load_mmin=tot_load[peaks_dwn]
                            tot_load_pks=tot_load[peaks_all]
                        else:
                            print('FAIL')
                            plt.figure()
                            plt.plot(tot_load)
                            plt.plot(peaks_up, tot_load[peaks_up], "x")
                            plt.plot(peaks_dwn, tot_load[peaks_dwn], "o")
                            figManager = plt.get_current_fig_manager()
                            figManager.window.showMaximized()
                            plt.show()
                            asadsad
                            
                    elif int(len(peaks_up)-len(peaks_dwn))==0:
                        if peaks_up[0]<peaks_dwn[0]:
                            peaks_dwn=peaks_dwn[:-1]
                            print('ENTER')
                            peaks_all=np.sort(np.concatenate((peaks_up,peaks_dwn)))
                            time_all=tdms_file['Log'][ld_ch].time_track(absolute_time=True,accuracy='ms')[peaks_all]
                            dif1=tot_load[peaks_up[:-1]]-tot_load[peaks_dwn]
                            dif2=tot_load[peaks_up[1:]]-tot_load[peaks_dwn]
                            Load_Diff=0.5*(dif1+dif2)
                            tot_load_max=tot_load[peaks_up]
                            tot_load_mmin=tot_load[peaks_dwn]
                            tot_load_pks=tot_load[peaks_all]
                            
                    else:
                        print('FAIL_2')
                        plt.figure()
                        plt.plot(tot_load)
                        plt.plot(peaks_up, tot_load[peaks_up], "x")
                        plt.plot(peaks_dwn, tot_load[peaks_dwn], "o")
                        figManager = plt.get_current_fig_manager()
                        figManager.window.showMaximized()
                        plt.show()
                        asadsad
                    
                    times_up=tdms_file['Log'][ld_ch].time_track(absolute_time=True,accuracy='ms')[peaks_up]
                    times_dnw=tdms_file['Log'][ld_ch].time_track(absolute_time=True,accuracy='ms')[peaks_dwn]
                   
                    # if cnt==0:
                    #     fatgigue_data['peaks_all']=[]
                    #     fatgigue_data['peaks_up']=[]
                    #     fatgigue_data['peaks_dwn']=[]
                    #     fatgigue_data['Load_Diff']=[]
                    # fatgigue_data['peaks_all'].extend(peaks_all+len(fatgigue_data[ld_ch]))
                    # fatgigue_data['peaks_up'].extend(peaks_up+len(fatgigue_data[ld_ch])) 
                    # fatgigue_data['peaks_dwn'].extend(peaks_dwn+len(fatgigue_data[ld_ch])) 
                    # fatgigue_data['Load_Diff'].extend(Load_Diff)
                    
                    if cnt==0:
                        fatgigue_data[ld_ch]=tot_load
                        fatgigue_data['peaks_all']=peaks_all
                        fatgigue_data['time_loads_p']=time_all
                        fatgigue_data['time_up']=tdms_file['Log'][ld_ch].time_track(absolute_time=True,accuracy='ms')[peaks_up]
                        fatgigue_data['time_dwn']=tdms_file['Log'][ld_ch].time_track(absolute_time=True,accuracy='ms')[peaks_dwn]
                        fatgigue_data['peaks_up']=peaks_up
                        fatgigue_data['peaks_dwn']=peaks_dwn
                        fatgigue_data['Load_Diff']=Load_Diff
                        fatgigue_data['Temp_S_T_10_Time']=tdms_file['Log']['Temp_S_T_10'].time_track(absolute_time=True,accuracy='ms')
                        fatgigue_data['Temp_S_T_10']=tdms_file['Log']['Temp_S_T_10'][:]
                        fatgigue_data['Temp_S_T_10_0']=tdms_file['Log']['Temp_S_T_10'][:]-np.mean(zero_tdms_file['Log']['Temp_S_T_10'][:])
                    else:
                        npoin=len(fatgigue_data[ld_ch])
                        fatgigue_data['peaks_all']=np.concatenate((fatgigue_data['peaks_all'],(peaks_all+npoin)))
                        fatgigue_data['peaks_up']=np.concatenate((fatgigue_data['peaks_up'],(peaks_up+npoin)))
                        fatgigue_data['peaks_dwn']=np.concatenate((fatgigue_data['peaks_dwn'],(peaks_dwn+npoin)))
                        fatgigue_data['Load_Diff']=np.concatenate((fatgigue_data['Load_Diff'],Load_Diff))
                        fatgigue_data['time_loads_p']=np.concatenate((fatgigue_data['time_loads_p'],time_all))
                        fatgigue_data['time_up']=np.concatenate((fatgigue_data['time_up'],tdms_file['Log'][ld_ch].time_track(absolute_time=True,accuracy='ms')[peaks_up]))
                        fatgigue_data['time_dwn']=np.concatenate((fatgigue_data['time_dwn'],tdms_file['Log'][ld_ch].time_track(absolute_time=True,accuracy='ms')[peaks_dwn]))
                        fatgigue_data[ld_ch]=np.concatenate((fatgigue_data[ld_ch],tot_load))
                        fatgigue_data['Temp_S_T_10']=np.concatenate((fatgigue_data['Temp_S_T_10'],tdms_file['Log']['Temp_S_T_10'][:]))
                        fatgigue_data['Temp_S_T_10_0']=np.concatenate((fatgigue_data['Temp_S_T_10_0'],tdms_file['Log']['Temp_S_T_10'][:]-np.mean(zero_tdms_file['Log']['Temp_S_T_10'][:])))
                        fatgigue_data['Temp_S_T_10_Time']=np.concatenate((fatgigue_data['Temp_S_T_10_Time'],tdms_file['Log']['Temp_S_T_10'].time_track(absolute_time=True,accuracy='ms')))
                        
                    
                    
                    
                    all_pos_lst=[key for key in tdms_file['Log']._channels if key.__contains__("Pos_S") ]
                    all_pos_lst=[key for key in all_pos_lst if not  key.__contains__("Filter") ]
                    
                    ###Ross 
                    
                    all_ros_lst_all=[key for key in tdms_file['Log']._channels if key.__contains__("Ros") ]
                    all_ros_lst_all=[key for key in all_ros_lst_all if not  key.__contains__("Filter") ]
                    all_ros_lst_120=[key for key in all_ros_lst_all if  key.__contains__("120") ]
                    all_ros_lst_350=[key for key in all_ros_lst_all if  key.__contains__("350") ]
                    
                    ### Broken sensr
                    all_ros_lst_120=[key for key in all_ros_lst_120 if not  key.__contains__("Str_Ros_120_4_4") ]
                    
                    unique_ros_120=sorted(list(set([key[12:15] for key in all_ros_lst_120])))
                    
                    all_ros_lst_120_0=[key for key in all_ros_lst_120 if  key.__contains__("_0") ]
                    
                    
                    all_sen_lst=all_pos_lst+all_ros_lst_120_0
                    
                    
                    for dis in all_sen_lst:
                        print(dis)
                        time_indx=[]
                        time_indx_max=[]
                        time_indx_min=[]
                        
                        disp=tdms_file['Log'][dis][:]-np.mean(zero_tdms_file['Log'][dis][:])
                        
                        
                        sigma_est = estimate_sigma(disp, average_sigmas=True)
                        disp=denoise_wavelet(disp, method='VisuShrink', mode='soft',  
                                                wavelet='sym9', 
                                                sigma=sigma_est/0.5,
                                                rescale_sigma='True')
                        
                        
                        cnt_test=-1
                        up=0
                        time_dis=tdms_file['Log'][dis].time_track(absolute_time=True)
                        for k in time_all:
                            
                            dtime=-1
                            while dtime<0:
                                cnt_test+=1
                                dtime=time_dis[cnt_test]-k
                            
                            if up==0:
                                
                                if dtime<abs(time_dis[cnt_test-1]-k):
                                
                                    time_indx_max.append(cnt_test)
                                else:
                                    time_indx_max.append(cnt_test-1)
                                up=1
                            elif up==1:
                                if dtime<abs(time_dis[cnt_test-1]-k):
                                
                                    time_indx_min.append(cnt_test)
                                else:
                                    time_indx_min.append(cnt_test-1)
                                up=0
                        
                        # time_indx_max2=[]
                        # time_indx_min2=[]
                        
                        # for k in times_up:
                        
                        #     time_indx_max2.append(np.argmin(abs(tdms_file['Log'][dis].time_track(absolute_time=True)-k)))
                        
                        # for k in times_dnw:
                        
                        #     time_indx_min2.append(np.argmin(abs(tdms_file['Log'][dis].time_track(absolute_time=True)-k)))
                        
                            
                        
                        disp_max=disp[time_indx_max]
                        disp_min=disp[time_indx_min]
                        dif1=disp[peaks_up[:-1]]-disp[peaks_dwn]
                        dif2=disp[peaks_up[1:]]-disp[peaks_dwn]
                        disp_dif=0.5*(dif1+dif2)
                        # disp=disp[time_indx]
                        
                        if cnt==0:
                            fatgigue_data[dis]=disp
                            fatgigue_data[dis+'_max']=disp_max
                            fatgigue_data[dis+'_min']=disp_min
                            fatgigue_data[dis+'_dif']=disp_dif
                        
                        else:
                            fatgigue_data[dis]=np.concatenate((fatgigue_data[dis],disp))
                            fatgigue_data[dis+'_max']=np.concatenate((fatgigue_data[dis+'_max'],disp_max))
                            fatgigue_data[dis+'_min']=np.concatenate((fatgigue_data[dis+'_min'],disp_min))
                            fatgigue_data[dis+'_dif']=np.concatenate((fatgigue_data[dis+'_dif'],disp_dif))
                            
                            

                    
                    # ###Ross 
                    
                    # all_ros_lst_all=[key for key in tdms_file['Log']._channels if key.__contains__("Ros") ]
                    # all_ros_lst_all=[key for key in all_ros_lst_all if not  key.__contains__("Filter") ]
                    # all_ros_lst_120=[key for key in all_ros_lst_all if  key.__contains__("120") ]
                    # all_ros_lst_350=[key for key in all_ros_lst_all if  key.__contains__("350") ]
                    
                    # ### Broken sensr
                    # all_ros_lst_120=[key for key in all_ros_lst_120 if not  key.__contains__("Str_Ros_120_4_4") ]
                    
                    # unique_ros_120=sorted(list(set([key[12:15] for key in all_ros_lst_120])))
                    
                    # all_ros_lst_120_0=[key for key in all_ros_lst_120 if  key.__contains__("_0") ]
                    
                    
                    # for strl in all_ros_lst_120_0:
                        
                    #     print(strl)
                    #     #Substrac Zero Data

                    #     time_indx=[]
                    #     time_indx_max=[]
                    #     time_indx_min=[]
                        
                    #     disp=tdms_file['Log'][strl][:]-np.mean(zero_tdms_file['Log'][strl][:])
                        
                        
                    #     sigma_est = estimate_sigma(disp, average_sigmas=True)
                    #     disp=denoise_wavelet(disp, method='VisuShrink', mode='soft',  
                    #                         wavelet='sym9', 
                    #                         sigma=sigma_est/0.5,
                    #                         rescale_sigma='True')
                        
                        
                    #     # for k in time_all:
                        
                    #     #     time_indx.append(np.argmin(abs(tdms_file['Log'][dis].time_track(absolute_time=True)-k)))
                        
                    #     for k in times_up:
                        
                    #         time_indx_max.append(np.argmin(abs(tdms_file['Log'][strl].time_track(absolute_time=True)-k)))
                        
                    #     for k in times_dnw:
                        
                    #         time_indx_min.append(np.argmin(abs(tdms_file['Log'][strl].time_track(absolute_time=True)-k)))
                                         
                    #     disp_max=disp[time_indx_max]
                    #     disp_min=disp[time_indx_min]
                    #     # disp=disp[time_indx]
                        
                    #     if cnt==0:
                    #         fatgigue_data[strl+'_max']=disp_max
                    #         fatgigue_data[strl+'_min']=disp_min
                        
                    #     else:
                        
                    #         fatgigue_data[strl+'_max']=np.concatenate((fatgigue_data[strl+'_max'],disp_max))
                    #         fatgigue_data[strl+'_min']=np.concatenate((fatgigue_data[strl+'_min'],disp_min))


                    cnt=1
                    

                
