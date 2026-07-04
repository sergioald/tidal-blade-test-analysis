# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 14:42:59 2023

@author: slopezd
"""

print('Run Test Process')

from nptdms import TdmsFile
import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
# import sys
# from nptdms import TdmsFile, TdmsWriter, RootObject, ChannelObject, GroupObject
# import shutil
# from scipy import fftpack
from scipy.signal import find_peaks
# from scipy.fft import rfft, rfftfreq,   fft, fftfreq
# from scipy import signal
# import statistics
from skimage.restoration import (denoise_wavelet, estimate_sigma)
# import pywt
# import re
# from scipy.interpolate import make_interp_spline, BSpline
import pickle
from sklearn import linear_model
from sklearn.metrics import mean_squared_error, r2_score

#%%
print('start')
##working Paths
Path_Code=os.path.abspath(os.getcwd())
os.chdir("..")
Main_Path=os.path.abspath(os.curdir)
Main_Input=os.path.join(Main_Path,'Process_Data\\Fatigue')
Main_Output=os.path.join(Main_Path,'Results\\Fatigue_Pros_Data')

Main_FT=Main_Output

# files = os.listdir(Main_Input)
# files = [s for s in files if s.__contains__(".tdms")]
#%%


# file='C:\path\to\test_data\Second_Campaign_3_Actuator\\Process_Data\\Fatigue\\LTD_23A01_FA.tdms'

# file='C:\path\to\test_data\Second_Campaign_3_Actuator\\Join_Data\LTD_23A01_FA_0033\\LTD_23A01_FA_0033.tdms'

# file='C:\path\to\test_data\Second_Campaign_3_Actuator\\Join_Data\LTD_23A01_FA_0035\\LTD_23A01_FA_0035.tdms'

files= [s for s in os.listdir(Main_Input) if s.__contains__(".tdms") and not s.__contains__("_index")]

file=os.path.join(Main_Input,files[0])

filt_lev=1
dist_act=np.array([2.2751, 3.56, 4.477])


fatgigue_data={}

with TdmsFile.open(file) as tdms_file:
#tdms_file = TdmsFile(os.path.join(f_path,f_fname+'.tdms'))

    p_len=0
    if p_len==1:
    
        all_chn_lst=[key for key in tdms_file['Log']._channels]
        
        for ch in all_chn_lst:
            
            print(tdms_file['Log'][ch].properties['wf_increment'],len(tdms_file['Log'][ch][:]),ch)
        
    
    
    all_lds_lst=[key for key in tdms_file['Log']._channels if key.__contains__("Load_A") and not key.__contains__("_PVE")]
    
    # all_lds_lst=[key for key in tdms_file['Log']._channels if key.__contains__("Pump") and not key.__contains__("_Filter")]
    
    
    # all_lds_lst=[key for key in all_lds_lst if key.__contains__("HP")]
    
    all_loads_filt={}
    
    
    plt.figure()
    
    for ld_ch in all_lds_lst:
    
        # ld_ch='Load_A_01_PVE'
        
        tot_load=tdms_file['Log'][ld_ch][:]
        
        if np.mean(tot_load)<0:
            tot_load=tot_load*-1
        
        # plt.figure()
        # plt.plot(tot_load)
        
        
        sigma_est = estimate_sigma(tot_load, average_sigmas=True)
        
        # VisuShrink
        # BayesShrink
        
        tot_load=denoise_wavelet(tot_load, method='BayesShrink', mode='soft',  
                               wavelet='sym20', 
                               sigma=sigma_est*filt_lev,
                               rescale_sigma='True')
        
        
        plt.plot(tot_load, label=ld_ch)
        plt.legend()
        # plt.title(ld_ch)
        # plt.ylim(92, 102)
        
        # tot_load=denoise_wavelet(tot_load, method='BayesShrink', mode='soft',  
        #                        wavelet='db38', 
        #                        sigma=sigma_est*filt_lev,
        #                        rescale_sigma='True')
        
        
        # plt.plot(tot_load, label=ld_ch,c='k')
        
        # plt.xlim(2600000,2601000)
        
        
        # print(len(tot_load))
        
        all_loads_filt[ld_ch]=tot_load
        
    len_d=all_loads_filt[ld_ch].shape[0]
    all_loads_filt_m=np.empty((len_d, len(all_lds_lst)))
    
    cnt_l=0
    for ld_ch in all_lds_lst:
        if all_loads_filt[ld_ch].shape[0]!=len_d:
            exit()
        else:
            all_loads_filt_m[:,cnt_l]=all_loads_filt[ld_ch]
        cnt_l+=1
        
    
        # plt.plot(tot_load) 
    
    rbm_all=all_loads_filt_m*dist_act
    rbm = np.sum(rbm_all, axis=1)
    tot_load= np.sum(all_loads_filt_m, axis=1)
    
    peaks_up, _ = find_peaks(rbm, prominence=(250))
    peaks_dwn, _ = find_peaks(rbm*-1, prominence=(250))
    
    print('peaks_up',len(peaks_up))
    print('peaks_dwn',len(peaks_dwn))
    
    asdasd

    plt.figure()
    # contour_heights = tot_load[peaks_up] - properties['prominences']
    plt.plot(rbm)
    plt.plot(peaks_up, rbm[peaks_up], "x")
    plt.plot(peaks_dwn, rbm[peaks_dwn], "o")
    # plt.vlines(x=peaks_up, ymin=contour_heights, ymax=tot_load[peaks_up])
    plt.show()
    
    
    
    if int(len(peaks_up)-len(peaks_dwn))==1:
        if peaks_up[0]<peaks_dwn[0]:
            print('ENTER 0')
            peaks_all=np.sort(np.concatenate((peaks_up,peaks_dwn)))
            time_all=tdms_file['Log'][ld_ch].time_track(absolute_time=True,accuracy='ms')[peaks_all]
            
            
            ###############################################################
            ################Load###########################################
            ###############################################################
            
            dif1=abs(tot_load[peaks_up[:-1]]-tot_load[peaks_dwn])
            dif2=abs(tot_load[peaks_up[1:]]-tot_load[peaks_dwn])
            Load_Diff=0.5*(dif1+dif2)
            tot_load_max=tot_load[peaks_up]
            tot_load_mmin=tot_load[peaks_dwn]
            tot_load_pks=tot_load[peaks_all]
            
            ###############################################################
            ##############Moment###########################################
            ###############################################################
            
            dif1_m=abs(rbm[peaks_up[:-1]]-rbm[peaks_dwn])
            dif2_m=abs(rbm[peaks_up[1:]]-rbm[peaks_dwn])
            Moment_Diff=0.5*(dif1_m+dif2_m)
            tot_rbm_max=rbm[peaks_up]
            tot_rbm_mmin=rbm[peaks_dwn]
            tot_rbm_pks=rbm[peaks_all]
            
            
            
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
            print('ENTER 1')
            peaks_all=np.sort(np.concatenate((peaks_up,peaks_dwn)))
            time_all=tdms_file['Log'][ld_ch].time_track(absolute_time=True,accuracy='ms')[peaks_all]
            ###############################################################
            ################Load###########################################
            ###############################################################
            
            dif1=abs(tot_load[peaks_up[:-1]]-tot_load[peaks_dwn])
            dif2=abs(tot_load[peaks_up[1:]]-tot_load[peaks_dwn])
            Load_Diff=0.5*(dif1+dif2)
            tot_load_max=tot_load[peaks_up]
            tot_load_mmin=tot_load[peaks_dwn]
            tot_load_pks=tot_load[peaks_all]
            
            ###############################################################
            ##############Moment###########################################
            ###############################################################
            
            dif1_m=abs(rbm[peaks_up[:-1]]-rbm[peaks_dwn])
            dif2_m=abs(rbm[peaks_up[1:]]-rbm[peaks_dwn])
            Moment_Diff=0.5*(dif1_m+dif2_m)
            tot_rbm_max=rbm[peaks_up]
            tot_rbm_mmin=rbm[peaks_dwn]
            tot_rbm_pks=[peaks_all]
            
            
        elif peaks_up[0]>peaks_dwn[0]:
            peaks_dwn=peaks_dwn[:-1]
            print('ENTER 1')
            peaks_all=np.sort(np.concatenate((peaks_up,peaks_dwn)))
            time_all=tdms_file['Log'][ld_ch].time_track(absolute_time=True,accuracy='ms')[peaks_all]
            ###############################################################
            ################Load###########################################
            ###############################################################
            
            dif1=abs(tot_load[peaks_up[:-1]]-tot_load[peaks_dwn])
            dif2=abs(tot_load[peaks_up[1:]]-tot_load[peaks_dwn])
            Load_Diff=0.5*(dif1+dif2)
            tot_load_max=tot_load[peaks_up]
            tot_load_mmin=tot_load[peaks_dwn]
            tot_load_pks=tot_load[peaks_all]
            
            ###############################################################
            ##############Moment###########################################
            ###############################################################
            
            dif1_m=abs(rbm[peaks_up[:-1]]-rbm[peaks_dwn])
            dif2_m=abs(rbm[peaks_up[1:]]-rbm[peaks_dwn])
            Moment_Diff=0.5*(dif1_m+dif2_m)
            tot_rbm_max=rbm[peaks_up]
            tot_rbm_mmin=rbm[peaks_dwn]
            tot_rbm_pks=[peaks_all]
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
            
            
    else:
        print('FAIL_3')
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
    cnt=0
    
    fatgigue_data['Load_Tot']=tot_load
    fatgigue_data['Moment_Tot']=rbm
    fatgigue_data['peaks_all']=peaks_all
    fatgigue_data['time_loads_p']=time_all
    fatgigue_data['time_up']=tdms_file['Log'][ld_ch].time_track(absolute_time=True,accuracy='ms')[peaks_up]
    fatgigue_data['time_dwn']=tdms_file['Log'][ld_ch].time_track(absolute_time=True,accuracy='ms')[peaks_dwn]
    fatgigue_data['peaks_up']=peaks_up
    fatgigue_data['peaks_dwn']=peaks_dwn
    fatgigue_data['Load_Diff']=Load_Diff
    fatgigue_data['Moment_Diff']=Moment_Diff
    fatgigue_data['Temp_S_T_10_Time']=tdms_file['Log']['Temp_S_T_10'].time_track(absolute_time=True,accuracy='ms')
    fatgigue_data['Temp_S_T_10']=tdms_file['Log']['Temp_S_T_10'][:]
    fatgigue_data['Temp_S_T_10_0']=tdms_file['Log']['Temp_S_T_10'][:]
    
    
    
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
    
    
    print(all_ros_lst_120_0)
    
    all_sen_lst=all_pos_lst+all_ros_lst_120_0
    
    
    for dis in all_sen_lst:
        print(dis)
        time_indx=[]
        time_indx_max=[]
        time_indx_min=[]
        
        disp=tdms_file['Log'][dis][:]
        
        
        sigma_est = estimate_sigma(disp, average_sigmas=True)
        disp=denoise_wavelet(disp, method='VisuShrink', mode='soft',  
                                wavelet='sym20', 
                                sigma=sigma_est*filt_lev,
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
        dif1=abs(disp[peaks_up[:-1]]-disp[peaks_dwn])
        dif2=abs(disp[peaks_up[1:]]-disp[peaks_dwn])
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



    
f_name_s=files[0].split(".tdms")[0]
f_name_s_f=os.path.join(Main_Output,f_name_s+".pickle")


# if os.path.exists(f_name_s_f):
#     fatgigue_data=open(f_name_s_f, 'rb')
#     # with open(f_name_s_f, 'rb') as fatgigue_data:
#     fatgigue_data=pickle.load(fatgigue_data)
    
# else:
    
    
    
with open(f_name_s_f, 'wb') as handle:
    pickle.dump(fatgigue_data, handle, protocol=pickle.HIGHEST_PROTOCOL)

c_num=np.arange(1,len(fatgigue_data['Load_Diff'])+1)
fatgigue_data['Cycle_Number']=c_num


###################################################################
####################Load###########################################
###################################################################


fatgigue_data['Load_Up_Peack']=fatgigue_data['Load_Tot'][fatgigue_data['peaks_up']]
fatgigue_data['Load_Low_Peack']=fatgigue_data['Load_Tot'][fatgigue_data['peaks_dwn']]
fatgigue_data['R_value']=fatgigue_data['Load_Low_Peack']/(fatgigue_data['Load_Low_Peack']+fatgigue_data['Load_Diff'])


###################################################################
##################Moment###########################################
###################################################################

fatgigue_data['Moment_Up_Peack']=fatgigue_data['Moment_Tot'][fatgigue_data['peaks_up']]
fatgigue_data['Moment_Low_Peack']=fatgigue_data['Moment_Tot'][fatgigue_data['peaks_dwn']]
fatgigue_data['MR_value']=fatgigue_data['Moment_Low_Peack']/(fatgigue_data['Moment_Low_Peack']+fatgigue_data['Moment_Diff'])




fatigue_keys=[key for key in fatgigue_data ]

df_f_stat=pd.DataFrame()
for j in fatigue_keys:
    df_f_stat[j]=pd.Series(fatgigue_data[j]).describe()
df_f_stat.to_excel(os.path.join(Main_FT,f_name_s+"_statistics.xlsx"))




#%%
#####PLOTS

###################################################################
###################################################################
###################################################################
####################PLOTS##########################################
###################################################################
###################################################################
###################################################################


###################################################################
####################Load###########################################
###################################################################



x=c_num.reshape(-1, 1)
y=fatgigue_data['Load_Diff'].reshape(-1, 1)
# Create linear regression object
regr = linear_model.LinearRegression()

# Train the model using the training sets
regr.fit(x,y)
# The coefficients
print("Coefficients: \n", regr.coef_)
# The mean squared error
# print("Mean squared error: %.2f" % mean_squared_error(x,y))
# The ${r^2}$: 1 is perfect prediction
# print("${r^2}$: %.2f" % r2_score(x,y))

plt.figure()
plt.plot(x,y,'.')
plt.plot(x,regr.predict(x))
plt.title("Fatigue Test Delta Load")
plt.xlabel("Number of Cycle")
plt.ylabel("Delta Force kN")
txt="${r^2}$: %.2f" % r2_score(regr.predict(x),y)
plt.annotate(txt, xy=(min(x), 100))
figManager = plt.get_current_fig_manager()
figManager.window.showMaximized()
plt.show()
plt.savefig(os.path.join(Main_FT,f_name_s+'_Load_Delta.png'),bbox_inches='tight',dpi=500)
plt.close()


x=c_num.reshape(-1, 1)
y=fatgigue_data['Load_Tot'][fatgigue_data['peaks_dwn']].reshape(-1, 1)


# Create linear regression object
regr = linear_model.LinearRegression()

# Train the model using the training sets
regr.fit(x,y)
# The coefficients
print("Coefficients: \n", regr.coef_)
# The mean squared error
print("Mean squared error: %.2f" % mean_squared_error(x,y))
# The ${r^2}$: 1 is perfect prediction
print("${r^2}$: %.2f" % r2_score(regr.predict(x),y))

plt.figure()
plt.plot(x,y,'.')
plt.plot(x,regr.predict(x))
plt.title("Fatigue Test Lower Peak Loads")
plt.xlabel("Number of Cycle")
plt.ylabel("Force kN")
txt="${r^2}$: %.2f" % r2_score(regr.predict(x),y)
plt.annotate(txt, xy=(min(x), 55))
figManager = plt.get_current_fig_manager()
figManager.window.showMaximized()
plt.show()
plt.savefig(os.path.join(Main_FT,f_name_s+'_Load_LP.png'),bbox_inches='tight',dpi=500)
plt.close()



x=np.arange(1,len(fatgigue_data['peaks_up'])+1).reshape(-1, 1)
y=fatgigue_data['Load_Tot'][fatgigue_data['peaks_up']].reshape(-1, 1)


# Create linear regression object
regr = linear_model.LinearRegression()

# Train the model using the training sets
regr.fit(x,y)
# The coefficients
# print("Coefficients: \n", regr.coef_)
# # The mean squared error
# print("Mean squared error: %.2f" % mean_squared_error(x,y))
# # The ${r^2}$: 1 is perfect prediction
# print("${r^2}$: %.2f" % r2_score(regr.predict(x),y))

plt.figure()
plt.plot(x,y,'.')
plt.plot(x,regr.predict(x))
plt.title("Fatigue Test Upper Peak Loads")
plt.xlabel("Number of Cycle")
plt.ylabel("Force kN")
txt="${r^2}$: %.2f" % r2_score(regr.predict(x),y)
plt.annotate(txt, xy=(min(x), 155))
figManager = plt.get_current_fig_manager()
figManager.window.showMaximized()
plt.show()
plt.savefig(os.path.join(Main_FT,f_name_s+'_Load_UP.png'),bbox_inches='tight',dpi=500)
plt.close()



x=c_num.reshape(-1, 1)
y=fatgigue_data['R_value'].reshape(-1, 1)


# Create linear regression object
regr = linear_model.LinearRegression()

# Train the model using the training sets
regr.fit(x,y)


plt.figure()
plt.plot(x,y,'.')
plt.plot(x,regr.predict(x))
plt.title("Fatigue stress ratio R")
plt.xlabel("Number of Cycle")
plt.ylabel("Fatigue stress ratio R")
txt="${r^2}$: %.2f" % r2_score(regr.predict(x),y)
plt.annotate(txt, xy=(min(x), 155))
figManager = plt.get_current_fig_manager()
figManager.window.showMaximized()
plt.show()
plt.savefig(os.path.join(Main_FT,f_name_s+'_R_Ratio.png'),bbox_inches='tight',dpi=500)
plt.close()  



###################################################################
##################Moment###########################################
###################################################################



x=c_num.reshape(-1, 1)
y=fatgigue_data['Moment_Diff'].reshape(-1, 1)
# Create linear regression object
regr = linear_model.LinearRegression()

# Train the model using the training sets
regr.fit(x,y)
# The coefficients
print("Coefficients: \n", regr.coef_)
# The mean squared error
# print("Mean squared error: %.2f" % mean_squared_error(x,y))
# The ${r^2}$: 1 is perfect prediction
# print("${r^2}$: %.2f" % r2_score(x,y))

plt.figure()
plt.plot(x,y,'.')
plt.plot(x,regr.predict(x))
plt.title("Fatigue Test Delta Moment")
plt.xlabel("Number of Cycle")
plt.ylabel("Delta Moment kN-m")
txt="${r^2}$: %.2f" % r2_score(regr.predict(x),y)
plt.annotate(txt, xy=(min(x), 100))
figManager = plt.get_current_fig_manager()
figManager.window.showMaximized()
plt.show()
plt.savefig(os.path.join(Main_FT,f_name_s+'_Moment_Delta.png'),bbox_inches='tight',dpi=500)
plt.close()


x=c_num.reshape(-1, 1)
y=fatgigue_data['Moment_Tot'][fatgigue_data['peaks_dwn']].reshape(-1, 1)


# Create linear regression object
regr = linear_model.LinearRegression()

# Train the model using the training sets
regr.fit(x,y)
# The coefficients
print("Coefficients: \n", regr.coef_)
# The mean squared error
print("Mean squared error: %.2f" % mean_squared_error(x,y))
# The ${r^2}$: 1 is perfect prediction
print("${r^2}$: %.2f" % r2_score(regr.predict(x),y))

plt.figure()
plt.plot(x,y,'.')
plt.plot(x,regr.predict(x))
plt.title("Fatigue Test Lower Peak Moments")
plt.xlabel("Number of Cycle")
plt.ylabel("Moment kN-m")
txt="${r^2}$: %.2f" % r2_score(regr.predict(x),y)
plt.annotate(txt, xy=(min(x), 55))
figManager = plt.get_current_fig_manager()
figManager.window.showMaximized()
plt.show()
plt.savefig(os.path.join(Main_FT,f_name_s+'_Moment_LP.png'),bbox_inches='tight',dpi=500)
plt.close()



x=np.arange(1,len(fatgigue_data['peaks_up'])+1).reshape(-1, 1)
y=fatgigue_data['Moment_Tot'][fatgigue_data['peaks_up']].reshape(-1, 1)


# Create linear regression object
regr = linear_model.LinearRegression()

# Train the model using the training sets
regr.fit(x,y)
# The coefficients
# print("Coefficients: \n", regr.coef_)
# # The mean squared error
# print("Mean squared error: %.2f" % mean_squared_error(x,y))
# # The ${r^2}$: 1 is perfect prediction
# print("${r^2}$: %.2f" % r2_score(regr.predict(x),y))

plt.figure()
plt.plot(x,y,'.')
plt.plot(x,regr.predict(x))
plt.title("Fatigue Test Upper Peak Moments")
plt.xlabel("Number of Cycle")
plt.ylabel("Moment kN-m")
txt="${r^2}$: %.2f" % r2_score(regr.predict(x),y)
plt.annotate(txt, xy=(min(x), 155))
figManager = plt.get_current_fig_manager()
figManager.window.showMaximized()
plt.show()
plt.savefig(os.path.join(Main_FT,f_name_s+'_Moment_UP.png'),bbox_inches='tight',dpi=500)
plt.close()



x=c_num.reshape(-1, 1)
y=fatgigue_data['MR_value'].reshape(-1, 1)


# Create linear regression object
regr = linear_model.LinearRegression()

# Train the model using the training sets
regr.fit(x,y)


plt.figure()
plt.plot(x,y,'.')
plt.plot(x,regr.predict(x))
plt.title("Fatigue Moment ratio MR")
plt.xlabel("Number of Cycle")
plt.ylabel("Fatigue Moment ratio MR")
txt="${r^2}$: %.2f" % r2_score(regr.predict(x),y)
plt.annotate(txt, xy=(min(x), 155))
figManager = plt.get_current_fig_manager()
figManager.window.showMaximized()
plt.show()
plt.savefig(os.path.join(Main_FT,f_name_s+'_MR_Ratio.png'),bbox_inches='tight',dpi=500)
plt.close()  


all_top=[key for key in fatigue_keys if  key.__contains__("max") ]

for k in all_top:
    
    x=np.arange(1,len(fatgigue_data[k])+1).reshape(-1, 1)
    y=fatgigue_data[k].reshape(-1, 1)
    # Create linear regression object
    regr = linear_model.LinearRegression()
    
    # Train the model using the training sets
    regr.fit(x,y)
    
    plt.figure()
    plt.plot(x,y,'.')
    plt.plot(x,regr.predict(x))
    plt.title("Fatigue Test "+k)
    plt.xlabel("Number of Cycle")
    if 'Pos_S' in k:
        plt.ylabel("Displacement [mm]")
    else:
        plt.ylabel("Strain [$\epsilon$]")
    txt="${r^2}$: %.2f" % r2_score(regr.predict(x),y)
    plt.annotate(txt, xy=(min(x), max(y)))
    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
    plt.show()
    plt.savefig(os.path.join(Main_FT,f_name_s+'_'+k+'.png'),bbox_inches='tight',dpi=500)
    plt.close()
    
all_dwn=[key for key in fatigue_keys if  key.__contains__("min") ]

for k in all_dwn:
    
    x=np.arange(1,len(fatgigue_data[k])+1).reshape(-1, 1)
    y=fatgigue_data[k].reshape(-1, 1)
    # Create linear regression object
    regr = linear_model.LinearRegression()
    
    # Train the model using the training sets
    regr.fit(x,y)
    
    plt.figure()
    plt.plot(x,y,'.')
    plt.plot(x,regr.predict(x))
    plt.title("Fatigue Test "+k)
    plt.xlabel("Number of Cycle")
    if 'Pos_S' in k:
        plt.ylabel("Displacement [mm]")
    else:
        plt.ylabel("Strain [$\epsilon$]")
    txt="${r^2}$: %.2f" % r2_score(regr.predict(x),y)
    plt.annotate(txt, xy=(min(x), max(y)))
    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
    plt.show()
    plt.savefig(os.path.join(Main_FT,f_name_s+'_'+k+'.png'),bbox_inches='tight',dpi=500)
    plt.close()

all_dif=[key for key in fatigue_keys if  key.__contains__("dif") ]

for k in all_dif:
    
    x=np.arange(1,len(fatgigue_data[k])+1).reshape(-1, 1)
    y=fatgigue_data[k].reshape(-1, 1)
    # Create linear regression object
    regr = linear_model.LinearRegression()
    
    # Train the model using the training sets
    regr.fit(x,y)
    
    plt.figure()
    plt.plot(x,y,'.')
    plt.plot(x,regr.predict(x))
    plt.title("Fatigue Test "+k)
    plt.xlabel("Number of Cycle")
    if 'Pos_S' in k:
        plt.ylabel("Delta Displacement [mm]")
    else:
        plt.ylabel("Delta Strain [$\epsilon$]")
    txt="${r^2}$: %.2f" % r2_score(regr.predict(x),y)
    plt.annotate(txt, xy=(min(x), max(y)))
    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
    plt.show()
    plt.savefig(os.path.join(Main_FT,f_name_s+'_'+k+'.png'),bbox_inches='tight',dpi=500)
    plt.close()



###################################################################
####################Load###########################################
###################################################################


for k in all_dif:
    
    x=np.arange(1,len(fatgigue_data[k])+1).reshape(-1, 1)
    y=np.divide(fatgigue_data[k],fatgigue_data['Load_Diff']).reshape(-1, 1)
    
    # Create linear regression object
    regr = linear_model.LinearRegression()
    
    # Train the model using the training sets
    regr.fit(x,y)
    
    plt.figure()
    plt.plot(x,y,'.')
    plt.plot(x,regr.predict(x))
    plt.title("Fatigue Test Delta Load "+k)
    plt.xlabel("Number of Cycle")
    if 'Pos_S' in k:
        plt.ylabel("Delta Displacement / Delta Force [mm/kN]")
    else:
        plt.ylabel("Delta Strain / Delta Force [$\epsilon$/kN]")
    txt="${r^2}$: %.2f" % r2_score(regr.predict(x),y)
    plt.annotate(txt, xy=(min(x), max(y)))
    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
    plt.show()
    plt.savefig(os.path.join(Main_FT,f_name_s+'_'+k+'_DL.png'),bbox_inches='tight',dpi=500)
    plt.close()
    
    
###################################################################
##################Moment###########################################
###################################################################

for k in all_dif:
    
    x=np.arange(1,len(fatgigue_data[k])+1).reshape(-1, 1)
    y=np.divide(fatgigue_data[k],fatgigue_data['Moment_Diff']).reshape(-1, 1)
    
    # Create linear regression object
    regr = linear_model.LinearRegression()
    
    # Train the model using the training sets
    regr.fit(x,y)
    
    plt.figure()
    plt.plot(x,y,'.')
    plt.plot(x,regr.predict(x))
    plt.title("Fatigue Test Delta Moment "+k)
    plt.xlabel("Number of Cycle")
    if 'Pos_S' in k:
        plt.ylabel("Delta Displacement / Delta Moment [mm/kN-m]")
    else:
        plt.ylabel("Delta Strain / Delta Moment [$\epsilon$/kN-m]")
    txt="${r^2}$: %.2f" % r2_score(regr.predict(x),y)
    plt.annotate(txt, xy=(min(x), max(y)))
    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
    plt.show()
    plt.savefig(os.path.join(Main_FT,f_name_s+'_'+k+'_DM.png'),bbox_inches='tight',dpi=500)
    plt.close()
    
    
###################################################################
####################Load###########################################
###################################################################


for k in all_dwn:
    
    x=np.arange(1,len(fatgigue_data[k])+1).reshape(-1, 1)
    y=np.divide(fatgigue_data[k],fatgigue_data['Load_Tot'][fatgigue_data['peaks_dwn']]).reshape(-1, 1)
    # Create linear regression object
    regr = linear_model.LinearRegression()
    
    # Train the model using the training sets
    regr.fit(x,y)
    
    plt.figure()
    plt.plot(x,y,'.')
    plt.plot(x,regr.predict(x))
    plt.title("Fatigue Test Lower Load "+k)
    plt.xlabel("Number of Cycle")
    if 'Pos_S' in k:
        plt.ylabel("Displacement / Force [mm/kN]")
    else:
        plt.ylabel("Strain / Force [$\epsilon$/kN]")
    txt="${r^2}$: %.2f" % r2_score(regr.predict(x),y)
    plt.annotate(txt, xy=(min(x), max(y)))
    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
    plt.show()
    plt.savefig(os.path.join(Main_FT,f_name_s+'_'+k+'_PD.png'),bbox_inches='tight',dpi=500)
    plt.close()
    
###################################################################
##################Moment###########################################
###################################################################

for k in all_dwn:
    
    x=np.arange(1,len(fatgigue_data[k])+1).reshape(-1, 1)
    y=np.divide(fatgigue_data[k],fatgigue_data['Moment_Tot'][fatgigue_data['peaks_dwn']]).reshape(-1, 1)
    # Create linear regression object
    regr = linear_model.LinearRegression()
    
    # Train the model using the training sets
    regr.fit(x,y)
    
    plt.figure()
    plt.plot(x,y,'.')
    plt.plot(x,regr.predict(x))
    plt.title("Fatigue Test Lower Moment "+k)
    plt.xlabel("Number of Cycle")
    if 'Pos_S' in k:
        plt.ylabel("Displacement / Moment [mm/kN-m]")
    else:
        plt.ylabel("Strain / Moment [$\epsilon$/kN-m]")
    txt="${r^2}$: %.2f" % r2_score(regr.predict(x),y)
    plt.annotate(txt, xy=(min(x), max(y)))
    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
    plt.show()
    plt.savefig(os.path.join(Main_FT,f_name_s+'_'+k+'_MPD.png'),bbox_inches='tight',dpi=500)
    plt.close()
    
    
###################################################################
####################Load###########################################
###################################################################   


for k in all_top:
    
    x=np.arange(1,len(fatgigue_data[k])+1).reshape(-1, 1)
    y=np.divide(fatgigue_data[k],fatgigue_data['Load_Tot'][fatgigue_data['peaks_up']]).reshape(-1, 1)
    # Create linear regression object
    regr = linear_model.LinearRegression()
    
    # Train the model using the training sets
    regr.fit(x,y)
    
    plt.figure()
    plt.plot(x,y,'.')
    plt.plot(x,regr.predict(x))
    plt.title("Fatigue Test Upper Load "+k)
    plt.xlabel("Number of Cycle")
    if 'Pos_S' in k:
        plt.ylabel("Displacement / Force [mm/kN]")
    else:
        plt.ylabel("Strain / Force [$\epsilon$/kN]")
    txt="${r^2}$: %.2f" % r2_score(regr.predict(x),y)
    plt.annotate(txt, xy=(min(x), max(y)))
    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
    plt.show()
    plt.savefig(os.path.join(Main_FT,f_name_s+'_'+k+'_PU.png'),bbox_inches='tight',dpi=500)
    plt.close()
    
    
###################################################################
##################Moment###########################################
###################################################################


for k in all_top:
    
    x=np.arange(1,len(fatgigue_data[k])+1).reshape(-1, 1)
    y=np.divide(fatgigue_data[k],fatgigue_data['Moment_Tot'][fatgigue_data['peaks_up']]).reshape(-1, 1)
    # Create linear regression object
    regr = linear_model.LinearRegression()
    
    # Train the model using the training sets
    regr.fit(x,y)
    
    plt.figure()
    plt.plot(x,y,'.')
    plt.plot(x,regr.predict(x))
    plt.title("Fatigue Test Upper Moment "+k)
    plt.xlabel("Number of Cycle")
    if 'Pos_S' in k:
        plt.ylabel("Displacement / Moment [mm/kN-m]")
    else:
        plt.ylabel("Strain / Moment [$\epsilon$/kN-m]")
    txt="${r^2}$: %.2f" % r2_score(regr.predict(x),y)
    plt.annotate(txt, xy=(min(x), max(y)))
    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
    plt.show()
    plt.savefig(os.path.join(Main_FT,f_name_s+'_'+k+'_MPU.png'),bbox_inches='tight',dpi=500)
    plt.close()
    
###################################################################
####################Load###########################################
################################################################### 


for k in all_top:
    
    
    tt=np.arange(1,len(fatgigue_data[k])+1).reshape(-1, 1)
    x=fatgigue_data['Load_Tot'][fatgigue_data['peaks_up']].reshape(-1, 1)
    y=fatgigue_data[k].reshape(-1, 1)
    # Create linear regression object
    regr = linear_model.LinearRegression()
    
    # Train the model using the training sets
    regr.fit(x,y)

    
    plt.figure()        
    plt.scatter(x,y,s=5,c=tt)
    cbar=plt.colorbar()
    cbar.ax.set_ylabel('Cycle', rotation=90)
    plt.title("Fatigue Test Upper Load "+k)
    plt.xlabel("Force kN")
    if 'Pos_S' in k:
        plt.ylabel("Displacement [mm]")
    else:
        plt.ylabel("Strain [$\epsilon$]")
    plt.plot(x,regr.predict(x))
    txt="${r^2}$: %.2f" % r2_score(regr.predict(x),y)
    plt.annotate(txt, xy=(min(x), max(y)))
    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
    plt.show()
    plt.savefig(os.path.join(Main_FT,f_name_s+'_'+k+'_LOADvsDISP_2D_UP.png'),bbox_inches='tight',dpi=500)
    plt.close()
    
    plt.figure()
    ax = plt.axes(projection='3d')
    ax.scatter3D(x,y, tt, c=tt)
    plt.title("Fatigue Test Upper Load "+k)
    ax.set_xlabel(str('Force [kN]'))
    ax.set_ylabel(str('Displacement [mm]'))
    ax.set_zlabel('Cycle')
    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
    plt.show()
    plt.savefig(os.path.join(Main_FT,f_name_s+'_'+k+'_LOADvsDISP_3D_UP.png'),bbox_inches='tight',dpi=500)
    plt.close()
    
###################################################################
##################Moment###########################################
###################################################################

for k in all_top:
    
    
    tt=np.arange(1,len(fatgigue_data[k])+1).reshape(-1, 1)
    x=fatgigue_data['Moment_Tot'][fatgigue_data['peaks_up']].reshape(-1, 1)
    y=fatgigue_data[k].reshape(-1, 1)
    # Create linear regression object
    regr = linear_model.LinearRegression()
    
    # Train the model using the training sets
    regr.fit(x,y)

    
    plt.figure()        
    plt.scatter(x,y,s=5,c=tt)
    cbar=plt.colorbar()
    cbar.ax.set_ylabel('Cycle', rotation=90)
    plt.title("Fatigue Test Upper Moment "+k)
    plt.xlabel("Moment kN-m")
    if 'Pos_S' in k:
        plt.ylabel("Displacement [mm]")
    else:
        plt.ylabel("Strain [$\epsilon$]")
    plt.plot(x,regr.predict(x))
    txt="${r^2}$: %.2f" % r2_score(regr.predict(x),y)
    plt.annotate(txt, xy=(min(x), max(y)))
    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
    plt.show()
    plt.savefig(os.path.join(Main_FT,f_name_s+'_'+k+'_LOADvsDISP_2D_MUP.png'),bbox_inches='tight',dpi=500)
    plt.close()
    
    plt.figure()
    ax = plt.axes(projection='3d')
    ax.scatter3D(x,y, tt, c=tt)
    plt.title("Fatigue Test Upper Moment "+k)
    ax.set_xlabel(str('Moment [kN-m]'))
    ax.set_ylabel(str('Displacement [mm]'))
    ax.set_zlabel('Cycle')
    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
    plt.show()
    plt.savefig(os.path.join(Main_FT,f_name_s+'_'+k+'_LOADvsDISP_3D_MUP.png'),bbox_inches='tight',dpi=500)
    plt.close()