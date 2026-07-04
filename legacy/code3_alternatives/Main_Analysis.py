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
# import sys
from nptdms import TdmsFile, TdmsWriter, RootObject, ChannelObject, GroupObject
# import shutil
# from scipy import fftpack
from scipy.signal import find_peaks
from scipy.fft import rfft, rfftfreq,   fft, fftfreq
# from scipy import signal
import statistics
from skimage.restoration import (denoise_wavelet, estimate_sigma)
import pywt
import re
# from scipy.interpolate import make_interp_spline, BSpline
import pickle
from sklearn import linear_model
from sklearn.metrics import mean_squared_error, r2_score
#%%
#Rear Main file
fname='Loadtide_Test_Log.xlsx'
#%%

DO_NF=0
DO_ST=0
DO_FA=1


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
def dff_f(data,SAMPLE_RATE,target_cut_h,target_cut_v,plot=0,tlt=''):

    tlt=str(tlt)
    n = len(data)
    # yf = rfft(data,n)                                 # Compute the FFT
    t=  np.arange(n)*SAMPLE_RATE



    
    
    ## Plots
    if plot==1:
        
        yf = rfft(data,n)                                # Compute the FFT
        xf = rfftfreq(n, 1 / SAMPLE_RATE)                # Create x-axis of frequencies in Hz
        PSD = yf * np.conj(yf) / n                      # Power spectrum (power per freq)
        
        
        plt.figure()
        plt.loglog(xf, np.abs(PSD),label='PSD')
        plt.loglog([xf[0], xf[-1]], [target_cut_h, target_cut_h], '--', label='Cut_h')
        plt.loglog([target_cut_v, target_cut_v],[max(PSD), min(PSD)], '--', label='Cut_v')
        plt.legend(loc="best")
        plt.title('PSD '+tlt)



    yf = fft(data,n)                                # Compute the FFT
    xf = fftfreq(n, 1 / SAMPLE_RATE)                # Create x-axis of frequencies in Hz
    PSD = yf * np.conj(yf) / n                      # Power spectrum (power per freq)
    

    indices = np.where(np.abs(xf) < target_cut_v)
    yf[indices] = 0

    indices = np.where(PSD <target_cut_h)      # Find all freqs with large power
    yf[indices] = 0    # Zero out small Fourier coeffs. in Y
    
    
    filtered_data = np.fft.ifft(yf).real # Inverse FFT for filtered time signal
    
    
    residual=data-filtered_data

            


    ## Plots
    if plot==1:
        

        
        plt.figure()
        
        
        ax1=plt.subplot(311)
        ax1.plot(t,data,color='r',linewidth=1.5,label='Noisy')
        ax1.plot(t,filtered_data,color='k',linewidth=2,label='Clean')
        plt.legend(loc="best")
        plt.suptitle('Results '+tlt)
        
        ax2=plt.subplot(312, sharex=ax1,sharey=ax1)
        ax2.plot(t,filtered_data,color='b',linewidth=2,label='Filtered')
        plt.legend(loc="best")
        
        ax3=plt.subplot(313, sharex=ax1)
        ax3.plot(t,residual,label='Residuals')
        plt.legend(loc="best")
        

        plt.figure()
        plt.psd(x=residual,Fs=SAMPLE_RATE)
        plt.title('PSD Residuals '+tlt)

    return filtered_data,residual

# Y,_=dff_f(Acc_NF,1,0,0.11,plot=1,tlt='P')
#%%
#Rear Main file
Test_Log= pd.read_excel(os.path.join(Main_Path,fname),sheet_name='Test_Log')
Test_Log.dropna(subset = ["Date_start"], inplace=True)
strt='LTD_23A01_ZO_0040'



strt_ind=Test_Log.index[Test_Log.Test_Reference == strt]


Test_Log=Test_Log[strt_ind[0]:]


#%%
#Start process
cnt=0

nf=[]
for indx, row in Test_Log.iterrows():
    print(indx,row['Type_Test'],row['Test_Reference'])
    f_fname=row['Test_Reference']
    f_path=os.path.join(Main_Input,f_fname)
    if row['Type_Test']=='ZO':
        print('Reading Zero File')
        zero_tdms_file = TdmsFile(os.path.join(f_path,f_fname+'.tdms'))
        continue
###############################################################################
############################### NATUTAL FREQ###################################
###############################################################################    
    
    if row['Type_Test']=='NF':
        if DO_NF==1:
            print('Reading Natural Frequency File')
            tdms_file = TdmsFile(os.path.join(f_path,f_fname+'.tdms'))
            #Get Accelerometers
            all_acc_lst=[key for key in tdms_file['Log']._channels if key.__contains__("Acc_S") ]
            
            all_acc_lst_z=[key for key in all_acc_lst if key.__contains__("_Z") ]
            
            df_ac=pd.DataFrame(columns=all_acc_lst_z)
            
            
            #####Special Case
            special_case=['0002','0008','0017','0024','0026']
            
            Main_TST=os.path.join(Main_NF,f_fname)
            Main_PSD=os.path.join(Main_TST,'PSD')
            Main_FFT=os.path.join(Main_TST,'FFT')
            Main_PSD_peaks=os.path.join(Main_TST,'PSD_peaks')
            Main_FFT_peak=os.path.join(Main_TST,'FFT_peak')
            
            if not os.path.exists(Main_PSD):
                os.makedirs(Main_PSD)
            if not os.path.exists(Main_FFT):
                os.makedirs(Main_FFT)
            if not os.path.exists(Main_PSD_peaks):
                os.makedirs(Main_PSD_peaks)
            if not os.path.exists(Main_FFT_peak):
                os.makedirs(Main_FFT_peak)     
                
            for acc in all_acc_lst_z:
                
                # temp=[]
                
                #Substrac Zero Data
                Acc_NF=tdms_file['Log'][acc][:]-np.mean(zero_tdms_file['Log'][acc][:])
                f_s = tdms_file['Log'][acc].properties['wf_increment']
                
                strt=np.argmax(Acc_NF)-20
                end=strt+4000+20
                plt.figure()
                plt.plot(tdms_file['Log'][acc].time_track()[strt:end],Acc_NF[strt:end])
                plt.ylabel(str('Acceleration '+tdms_file['Log'][acc].properties['unit_string']))
                plt.xlabel("Test time s")
                plt.ylim(-4, 4)
                plt.title(f_fname+'_'+acc)
                plt.savefig(os.path.join(Main_TST,f_fname+'_'+acc+'_g.png'),bbox_inches='tight')
                # plt.savefig(os.path.join(Main_FFT,f_fname+'_'+acc+'_FFT.svg'))
                plt.close()
                # Acc_NF,_=dff_f(Acc_NF,1/f_s,0,10,plot=0,tlt=acc)
                
                # X = np.fft.fft(Acc_NF)
                # N=len(X)
                # freqs = np.fft.fftfreq(N, f_s)
                
               
                
                N=Acc_NF.shape[0]
                
                fft_v = np.abs(rfft(Acc_NF,N) )                               # Compute the FFT
                freq = rfftfreq(N,  f_s)                # Create x-axis of frequencies in Hz
                # PSD = yf * np.conj(yf) / N                      # Power spectrum (power per freq)
                
                
                
                peaks, _ = find_peaks(fft_v, height=np.max(fft_v)*0.1,distance=0.5/f_s)
                
                pf=freq[peaks]
                pv=fft_v[peaks]
                
                df_FFT=pd.DataFrame(columns=['Freq','FFT'])
                df_FFT['Freq']=freq
                df_FFT['FFT']=fft_v
                df_FFT2=pd.DataFrame(columns=['Peak_Freq','Peak_FFT'])
                df_FFT2['Peak_Freq']=pf
                df_FFT2['Peak_FFT']=pv
                
                df_FFT=pd.concat([df_FFT, df_FFT2], axis=1) 

                fig, ax1 = plt.subplots()
                # plt.bar(freqs[:N // 2], np.abs(X)[:N // 2] * 1 / N, width=0.5)  # 1 / N is a normalization factor
                ax1.plot(freq, fft_v)  # 1 / N is a normalization factor                
                # # ax.stem(np.abs(freqs), np.abs(X))
                ax1.set_xlabel('Frequency [Hz]')
                ax1.set_ylabel('Frequency Domain (Spectrum) Magnitude')
                plt.yscale('log')
                plt.title(f_fname+'_'+acc)
                plt.savefig(os.path.join(Main_FFT,f_fname+'_'+acc+'_FFT.png'),bbox_inches='tight')
                # plt.savefig(os.path.join(Main_FFT,f_fname+'_'+acc+'_FFT.svg'))
                plt.close()
                
                if f_fname.split("_")[-1] in special_case:
                    
                    fig, ax1 = plt.subplots()
                    # plt.bar(freqs[:N // 2], np.abs(X)[:N // 2] * 1 / N, width=0.5)  # 1 / N is a normalization factor
                    ax1.plot(freq, fft_v)  # 1 / N is a normalization factor                
                    # # ax.stem(np.abs(freqs), np.abs(X))
                    ax1.set_xlabel('Frequency [Hz]')
                    ax1.set_ylabel('Frequency Domain (Spectrum) Magnitude')
                    plt.title(f_fname+'_'+acc)
                    plt.xlim(10, 22)
                    plt.yscale('log')
                    plt.savefig(os.path.join(Main_FFT,f_fname+'_'+acc+'_FFT_zoom.png'),bbox_inches='tight')
                    # plt.savefig(os.path.join(Main_FFT,f_fname+'_'+acc+'_FFT.svg'))
                    plt.close()
                
                
                fig, ax1 = plt.subplots()
                # plt.bar(freqs[:N // 2], np.abs(X)[:N // 2] * 1 / N, width=0.5)  # 1 / N is a normalization factor
                ax1.plot(freq, fft_v)  # 1 / N is a normalization factor                
                # # ax.stem(np.abs(freqs), np.abs(X))
                ax1.plot(pf,pv, 'o', color='green', markersize=12)
                ax1.set_xlabel('Frequency [Hz]')
                ax1.set_ylabel('Frequency Domain (Spectrum) Magnitude')
                plt.yscale('log')
                plt.title(f_fname+'_'+acc)
                plt.savefig(os.path.join(Main_FFT_peak,f_fname+'_'+acc+'_FFT_peak.png'),bbox_inches='tight')
                # plt.savefig(os.path.join(Main_FFT_peak,f_fname+'_'+acc+'_FFT_peak.svg'))
                plt.close()
                
                
                ta=plt.psd(Acc_NF,Fs=1/f_s,NFFT=int(N))
                plt.close()
                df_FFT['Freq_PSD']=ta[1]
                df_FFT['PSD']=ta[0]
                
                
                peaks, _ = find_peaks(ta[0], height=np.max(ta[0])*0.1,distance=5*ta[0].shape[0]/(0.5/f_s))
                pf=ta[1][peaks]
                pv=ta[0][peaks]
                
                
                df_FFT2=pd.DataFrame(columns=['Peak_Freq_PSD','Peak_PSD'])
                df_FFT2['Peak_Freq_PSD']=pf
                df_FFT2['Peak_PSD']=pv
                
                df_FFT=pd.concat([df_FFT, df_FFT2], axis=1)
                
                df_FFT.to_excel(os.path.join(Main_TST,f_fname+'_'+acc+".xlsx"), sheet_name=f_fname+'_'+acc)
                
                ta=plt.psd(Acc_NF,Fs=1/f_s,NFFT=int(2*1/f_s))
                plt.close()
                
                peaks, _ = find_peaks(ta[0], height=np.max(ta[0])*0.1,distance=5*ta[0].shape[0]/(0.5/f_s))
                pf=ta[1][peaks]
                pv=ta[0][peaks]
                
                plt.figure()
                plt.psd(Acc_NF,Fs=1/f_s,NFFT=int(2*1/f_s))
                plt.title(f_fname+'_'+acc)
                plt.savefig(os.path.join(Main_PSD,f_fname+'_'+acc+'_PSD.png'),bbox_inches='tight')
                # plt.savefig(os.path.join(Main_PSD,f_fname+'_'+acc+'_PSD.svg'))
                plt.plot(pf,10*np.log10(pv), 'o', color='green', markersize=12)
                plt.savefig(os.path.join(Main_PSD_peaks,f_fname+'_'+acc+'_Peak_PSD.png'),bbox_inches='tight')
                # plt.savefig(os.path.join(Main_PSD_peaks,f_fname+'_'+acc+'_Peak_PSD.svg'))
                plt.close()
            continue

###############################################################################
###############################################################################
###############################################################################
###############################################################################
############################### STATIC ########################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################

    ###STATIC
    if row['Type_Test']=='ST':
        if DO_ST==1:
            
            
            filt_lev=2
            
            # delt_0_st=int(900)
            # delt_0_end=int(2000)
            # delt_end=int((8*60)/0.004)
            
            sec_up=120
            sec_dwn=120
            
            delt_strt=int((1)/0.004)
            delt_end=int((1)/0.004)
            
            print('Reading Static File',f_fname)
            
            Main_ST_R=os.path.join(Main_ST,f_fname)
            
            if not os.path.exists(Main_ST_R):
                os.makedirs(Main_ST_R)
                
            with TdmsFile.open(os.path.join(f_path,f_fname+'.tdms')) as tdms_file:
            #tdms_file = TdmsFile(os.path.join(f_path,f_fname+'.tdms'))
                all_lds_lst=[key for key in tdms_file['Log']._channels if key.__contains__("Load_A") and not key.__contains__("_PVE")]
                
                print(all_lds_lst)
                
                
                
                if len(all_lds_lst)==1:
                    ld_ch=all_lds_lst[0]
                    tot_load=tdms_file['Log'][ld_ch][:]-np.mean(zero_tdms_file['Log'][all_lds_lst[0]][:])
                    # plt.figure()
                    # plt.plot(tot_load)
                    
                    sigma_est = estimate_sigma(tot_load, average_sigmas=True)
                    tot_load=denoise_wavelet(tot_load, method='VisuShrink', mode='soft',  
                                           wavelet='sym20', 
                                           sigma=sigma_est*filt_lev,
                                           rescale_sigma='True')
                    # plt.plot(tot_load)
                
                else:
                    
                    all_loads_filt={}
                    
                    for ld_ch in all_lds_lst:
                    
                        # ld_ch='Load_A_01_PVE'
                        
                        tot_load=(tdms_file['Log'][ld_ch][:]-np.mean(zero_tdms_file['Log'][ld_ch][:]))
                        
                        if np.mean(tot_load)<0:
                            tot_load=tot_load*-1
                        
                        # plt.figure()
                        # plt.plot(tot_load)
                        
                        
                        sigma_est = estimate_sigma(tot_load, average_sigmas=True)
                        tot_load=denoise_wavelet(tot_load, method='VisuShrink', mode='soft',  
                                               wavelet='sym20', 
                                               sigma=sigma_est*filt_lev,
                                               rescale_sigma='True')
                        
                        # plt.plot(tot_load)
                        # plt.title(ld_ch)
                        # plt.ylim(92, 102)
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
                
                ###############################################################
                ################Target###########################################
                ###############################################################
                
                targ_load=statistics.mode(rbm.astype(int))
                stc_start0=tdms_file['Log'][ld_ch].time_track(absolute_time=True)[np.where(rbm.astype(int)==targ_load)[0][0]]
                stc_end0=tdms_file['Log'][ld_ch].time_track(absolute_time=True)[np.where(rbm.astype(int)==targ_load)[0][-1]]
                
                
                print('rbm',targ_load)
                print('min',(stc_end0-stc_start0)// np.timedelta64(1, 'm'))
                stc_start0=stc_start0 + np.timedelta64(sec_up,'s')
                stc_end0=stc_end0 - np.timedelta64(sec_dwn,'s')
                
                
                # print(stc_start,stc_end)
                
                stc_start=tdms_file['Log'][ld_ch].time_track(absolute_time=True)[np.argmin(abs(tdms_file['Log'][ld_ch].time_track(absolute_time=True)-stc_start0))]
                stc_end=tdms_file['Log'][ld_ch].time_track(absolute_time=True)[np.argmin(abs(tdms_file['Log'][ld_ch].time_track(absolute_time=True)-stc_end0))]
                
                print(stc_start,stc_end)
                
                
                # targ_load=statistics.mode(tot_load.astype(int))
                # stc_start=tdms_file['Log'][ld_ch].time_track(absolute_time=True)[np.where(tot_load.astype(int)==targ_load)[0][delt_0_st]]
                # stc_end=tdms_file['Log'][ld_ch].time_track(absolute_time=True)[np.where(tot_load.astype(int)==targ_load)[0][-delt_0_end]]
                
                # print(stc_start,stc_end)
                
                
                strt=np.argmin(abs(tdms_file['Log'][all_lds_lst[0]].time_track(absolute_time=True)-stc_start0))
                end=np.argmin(abs(tdms_file['Log'][all_lds_lst[0]].time_track(absolute_time=True)-stc_end0))
                
                
                
                for ld_ch in all_lds_lst:
                    
                       
                    ######
                    ######UP
                    ######
                    
                    tot_load_up=(tdms_file['Log'][ld_ch][:strt]-np.mean(zero_tdms_file['Log'][ld_ch][:]))
                    
                    if np.mean(tot_load_up)<0:
                        tot_load_up=tot_load_up*-1
                    
                    
                    
                    sigma_est = estimate_sigma(tot_load_up, average_sigmas=True)
                    tot_load_up=denoise_wavelet(tot_load_up, method='VisuShrink', mode='soft',  
                                           wavelet='sym20', 
                                           sigma=sigma_est*filt_lev,
                                           rescale_sigma='True')
                    

                    ######
                    ######MID
                    ######
                    
                    tot_load_mid=(tdms_file['Log'][ld_ch][strt:end]-np.mean(zero_tdms_file['Log'][ld_ch][:]))
                    
                    if np.mean(tot_load_mid)<0:
                        tot_load_mid=tot_load_mid*-1
                    
                    
                    
                    sigma_est = estimate_sigma(tot_load_mid, average_sigmas=True)
                    tot_load_mid=denoise_wavelet(tot_load_mid, method='VisuShrink', mode='soft',  
                                           wavelet='sym20', 
                                           sigma=sigma_est*filt_lev,
                                           rescale_sigma='True')


                    ######
                    ######DOWN
                    ######
                    
                    tot_load_dwn=(tdms_file['Log'][ld_ch][end:]-np.mean(zero_tdms_file['Log'][ld_ch][:]))
                    
                    if np.mean(tot_load_dwn)<0:
                        tot_load_dwn=tot_load_dwn*-1
                    
                    
                    
                    sigma_est = estimate_sigma(tot_load_dwn, average_sigmas=True)
                    tot_load_dwn=denoise_wavelet(tot_load_dwn, method='VisuShrink', mode='soft',  
                                           wavelet='sym20', 
                                           sigma=sigma_est*filt_lev,
                                           rescale_sigma='True')                    
                    
                    
                    
                    tot_load= np.concatenate((tot_load_up, tot_load_mid, tot_load_dwn), axis=0)
                    all_loads_filt[ld_ch]=tot_load
                    
                
                    
                strt=np.argmin(abs(tdms_file['Log'][all_lds_lst[0]].time_track(absolute_time=True)-stc_start0))
                end=np.argmin(abs(tdms_file['Log'][all_lds_lst[0]].time_track(absolute_time=True)-stc_end0))
                
                
                
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
                
                
                
                
                
                ###############################################################
                ################Load###########################################
                ###############################################################
                # plt.plot(tot_load[np.where(tot_load.astype(int)==targ_load)[0][0]:np.where(tot_load.astype(int)==targ_load)[0][-1]])
                plt.figure()
                plt.plot(tdms_file['Log'][ld_ch].time_track(accuracy='s')[:]/60,tot_load)
                plt.title('Load_'+f_fname)
                plt.ylabel(str('Force '+tdms_file['Log'][ld_ch].properties['unit_string']))
                plt.xlabel(str('Time minutes'))
                figManager = plt.get_current_fig_manager()
                figManager.window.showMaximized()
                plt.show()
                plt.savefig(os.path.join(Main_ST_R,f_fname+'_Full_Load.png'),bbox_inches='tight', dpi=500)
                plt.close()
                
                
                ###############################################################
                ##############Moment###########################################
                ###############################################################
                plt.figure()
                plt.plot(tdms_file['Log'][ld_ch].time_track(accuracy='s')[:]/60,rbm)
                plt.title('Moment_'+f_fname)
                plt.ylabel(str('Moment '+tdms_file['Log'][ld_ch].properties['unit_string']+'-m'))
                plt.xlabel(str('Time minutes'))
                figManager = plt.get_current_fig_manager()
                figManager.window.showMaximized()
                plt.show()
                plt.savefig(os.path.join(Main_ST_R,f_fname+'_Moment_Load.png'),bbox_inches='tight', dpi=500)
                plt.close()
                
                
                
                
                
                ###############################################################
                ################Load###########################################
                ###############################################################
                
                power=tot_load[:strt+delt_strt]
                T=tdms_file['Log'][ld_ch].time_track(accuracy='s')[:strt+delt_strt]/60
                # # 300 represents number of points to make between T.min and T.max
                # xnew = np.linspace(T.min(), T.max(), 25) 
                
                # spl = make_interp_spline(T, power, k=99)  # type: BSpline
                # power_smooth = spl(xnew)
                
                plt.figure()
                plt.plot(T,power)
                plt.title('Load_'+f_fname)
                plt.ylabel(str('Force '+tdms_file['Log'][ld_ch].properties['unit_string']))
                plt.xlabel(str('Time minutes'))
                figManager = plt.get_current_fig_manager()
                figManager.window.showMaximized()
                plt.show()
                plt.savefig(os.path.join(Main_ST_R,f_fname+'_Full_Load_start.png'),bbox_inches='tight', dpi=500)
                plt.close()
                plt.close()
                
                
                
                ###############################################################
                ##############Moment###########################################
                ###############################################################
                
                
                power=rbm[:strt+delt_strt]
                T=tdms_file['Log'][ld_ch].time_track(accuracy='s')[:strt+delt_strt]/60
                # # 300 represents number of points to make between T.min and T.max
                # xnew = np.linspace(T.min(), T.max(), 25) 
                
                # spl = make_interp_spline(T, power, k=99)  # type: BSpline
                # power_smooth = spl(xnew)
                
                plt.figure()
                plt.plot(T,power)
                plt.title('Moment_'+f_fname)
                plt.ylabel(str('Moment '+tdms_file['Log'][ld_ch].properties['unit_string']+'-m'))
                plt.xlabel(str('Time minutes'))
                figManager = plt.get_current_fig_manager()
                figManager.window.showMaximized()
                plt.show()
                plt.savefig(os.path.join(Main_ST_R,f_fname+'_Full_Moment_start.png'),bbox_inches='tight',dpi=500)
                plt.close()
                plt.close()
                
                
                
                ###############################################################
                ################Load###########################################
                ###############################################################
                
                power=tot_load[end-delt_end:]
                T=tdms_file['Log'][ld_ch].time_track(accuracy='s')[end-delt_end:]/60
                # # 300 represents number of points to make between T.min and T.max
                # xnew = np.linspace(T.min(), T.max(), 25) 
                
                # spl = make_interp_spline(T, power, k=99)  # type: BSpline
                # power_smooth = spl(xnew)
                
                
                plt.figure()
                # plt.plot(tdms_file['Log'][ld_ch].time_track(accuracy='s')[end-800:]/60,tot_load[end-800:])
                plt.plot(T,power)
                plt.title('Load_'+f_fname)
                plt.ylabel(str('Force '+tdms_file['Log'][ld_ch].properties['unit_string']))
                plt.xlabel(str('Time minutes'))
                figManager = plt.get_current_fig_manager()
                figManager.window.showMaximized()
                plt.show()
                plt.savefig(os.path.join(Main_ST_R,f_fname+'_Full_Load_end.png'),bbox_inches='tight',dpi=500)
                # plt.savefig(os.path.join(Main_ST_R,f_fname+'_Full_Load_end.svg'))
                plt.close()
                
                
                
                ###############################################################
                ##############Moment###########################################
                ###############################################################
                
                
                power=rbm[end-delt_end:]
                T=tdms_file['Log'][ld_ch].time_track(accuracy='s')[end-delt_end:]/60
                # # 300 represents number of points to make between T.min and T.max
                # xnew = np.linspace(T.min(), T.max(), 25) 
                
                # spl = make_interp_spline(T, power, k=99)  # type: BSpline
                # power_smooth = spl(xnew)
                
                
                plt.figure()
                # plt.plot(tdms_file['Log'][ld_ch].time_track(accuracy='s')[end-800:]/60,tot_load[end-800:])
                plt.plot(T,power)
                plt.title('Moment_'+f_fname)
                plt.ylabel(str('Moment '+tdms_file['Log'][ld_ch].properties['unit_string']+'-m'))
                plt.xlabel(str('Time minutes'))
                figManager = plt.get_current_fig_manager()
                figManager.window.showMaximized()
                plt.show()
                plt.savefig(os.path.join(Main_ST_R,f_fname+'_Full_Moment_end.png'),bbox_inches='tight',dpi=500)
                # plt.savefig(os.path.join(Main_ST_R,f_fname+'_Full_Load_end.svg'))
                plt.close()
                
                
                
                ###############################################################
                ################Load###########################################
                ###############################################################
                
                
                plt.figure()
                plt.plot(tdms_file['Log'][ld_ch].time_track(accuracy='s')[strt:end]/60,tot_load[strt:end])
                plt.title('Load_'+f_fname)
                plt.ylabel(str('Force '+tdms_file['Log'][ld_ch].properties['unit_string']))
                plt.xlabel(str('Time minutes'))
                figManager = plt.get_current_fig_manager()
                figManager.window.showMaximized()
                plt.show()
                plt.savefig(os.path.join(Main_ST_R,f_fname+'_Full_Load_center.png'),bbox_inches='tight',dpi=500)
                plt.close()
                
                
                ###############################################################
                ##############Moment###########################################
                ###############################################################
                
                plt.figure()
                plt.plot(tdms_file['Log'][ld_ch].time_track(accuracy='s')[strt:end]/60,rbm[strt:end])
                plt.title('Moment_'+f_fname)
                plt.ylabel(str('Moment '+tdms_file['Log'][ld_ch].properties['unit_string']))
                plt.xlabel(str('Time minutes'))
                figManager = plt.get_current_fig_manager()
                figManager.window.showMaximized()
                plt.show()
                plt.savefig(os.path.join(Main_ST_R,f_fname+'_Full_Moment_center.png'),bbox_inches='tight',dpi=500)
                plt.close()
                
                ###############################################################
                ###############################################################
                ###############################################################
                ###################Displacement################################
                ###############################################################
                ###############################################################
                ###############################################################
                
                
                strt=strt+delt_strt
                end=end-delt_end
                
                tot_load=tot_load[strt:end]
                rbm=rbm[strt:end]
                
                
                
                ###Displacement
                print('Displacements')
                all_pos_lst=[key for key in tdms_file['Log']._channels if key.__contains__("Pos_S") ]
                all_pos_lst=[key for key in all_pos_lst if not  key.__contains__("Filter") ]
                
                for dis in all_pos_lst:
                    disp=tdms_file['Log'][dis][:]-np.mean(zero_tdms_file['Log'][dis][:])
                    strt=np.argmin(abs(tdms_file['Log'][dis].time_track(absolute_time=True)-stc_start))
                    end=np.argmin(abs(tdms_file['Log'][dis].time_track(absolute_time=True)-stc_end))
                    strt=strt+delt_strt
                    end=end-delt_end
                    
                    # plt.figure()
                    # plt.plot(disp[strt:end])
                    
                    sigma_est = estimate_sigma(disp, average_sigmas=True)
                    disp=denoise_wavelet(disp, method='VisuShrink', mode='soft',  
                                           wavelet='sym20', 
                                            sigma=sigma_est*filt_lev,
                                           rescale_sigma='True')

                    
                    disp=disp[strt:end]
                    
                    # plt.figure()
                    # plt.plot(disp)
                    # stop
                    
                    ###############################################################
                    ################Load###########################################
                    ###############################################################
                    
                    
                    if len(disp)==len(tot_load):
                        plt.figure()
                        tt=tdms_file['Log'][dis].time_track(accuracy='s')[strt:end]/60
                        plt.scatter(tot_load,disp,s=5,c=tt)
                        cbar=plt.colorbar()
                        cbar.ax.set_ylabel('Minutes', rotation=90)
                        plt.title(dis+'_'+f_fname)
                        plt.xlabel(str('Force '+tdms_file['Log'][all_lds_lst[0]].properties['unit_string']))
                        plt.ylabel(str('Displacement '+tdms_file['Log'][dis].properties['unit_string']))
                        figManager = plt.get_current_fig_manager()
                        figManager.window.showMaximized()
                        plt.show()
                        plt.savefig(os.path.join(Main_ST_R,f_fname+'_'+dis+'_LOADvsDISP_2D.png'),bbox_inches='tight',dpi=500)
                        # plt.savefig(os.path.join(Main_ST_R,f_fname+'_'+dis+'_LOADvsDISP_2D.svg'))
                        plt.close()
                        
                        fig=plt.figure()
                        ax = fig.add_subplot(projection='3d')
                        p=ax.scatter3D(tot_load,disp, tt, c=tt)
                        plt.title(dis+'_'+f_fname)
                        ax.set_xlabel(str('Force '+tdms_file['Log'][all_lds_lst[0]].properties['unit_string']))
                        ax.set_ylabel(str('Displacement '+tdms_file['Log'][dis].properties['unit_string']))
                        ax.set_zlabel('Time Minutes')
                        fcbar =fig.colorbar(p, ax=ax, pad=0.1)
                        cbar.ax.set_ylabel('Minutes', rotation=90)
                        figManager = plt.get_current_fig_manager()
                        figManager.window.showMaximized()
                        plt.show()
                        plt.savefig(os.path.join(Main_ST_R,f_fname+'_'+dis+'_LOADvsDISP_3D.png'),bbox_inches='tight',dpi=500)
                        # plt.savefig(os.path.join(Main_ST_R,f_fname+'_'+dis+'_LOADvsDISP_3D.svg'))
                        plt.close()
                    else:
                        print('error lenghts')
                        
                        
                    ###############################################################
                    ##############Moment###########################################
                    ###############################################################
                
                    if len(disp)==len(tot_load):
                        plt.figure()
                        tt=tdms_file['Log'][dis].time_track(accuracy='s')[strt:end]/60
                        plt.scatter(rbm,disp,s=5,c=tt)
                        cbar=plt.colorbar()
                        cbar.ax.set_ylabel('Minutes', rotation=90)
                        plt.title(dis+'_'+f_fname)
                        plt.xlabel(str('Moment '+tdms_file['Log'][all_lds_lst[0]].properties['unit_string']+'-m'))
                        plt.ylabel(str('Displacement '+tdms_file['Log'][dis].properties['unit_string']))
                        figManager = plt.get_current_fig_manager()
                        figManager.window.showMaximized()
                        plt.show()
                        plt.savefig(os.path.join(Main_ST_R,f_fname+'_'+dis+'_Moment_vs_DISP_2D.png'),bbox_inches='tight',dpi=500)
                        # plt.savefig(os.path.join(Main_ST_R,f_fname+'_'+dis+'_LOADvsDISP_2D.svg'))
                        plt.close()
                        
                        fig=plt.figure()
                        ax = fig.add_subplot(projection='3d')
                        p=ax.scatter(rbm,disp, tt, c=tt)
                        plt.title(dis+'_'+f_fname)
                        ax.set_xlabel(str('Moment '+tdms_file['Log'][all_lds_lst[0]].properties['unit_string']+'-m'))
                        ax.set_ylabel(str('Displacement '+tdms_file['Log'][dis].properties['unit_string']))
                        ax.set_zlabel('Time Minutes')
                        cbar =fig.colorbar(p, ax=ax, pad=0.1)
                        cbar.ax.set_ylabel('Minutes', rotation=90)
                        figManager = plt.get_current_fig_manager()
                        figManager.window.showMaximized()
                        plt.show()
                        plt.savefig(os.path.join(Main_ST_R,f_fname+'_'+dis+'_Moment_vs_DISP_3D.png'),bbox_inches='tight',dpi=500)
                        # plt.savefig(os.path.join(Main_ST_R,f_fname+'_'+dis+'_LOADvsDISP_3D.svg'))
                        plt.close()
                    else:
                        print('error lenghts')

                
                # dsadsad
                
                ###Strain
                all_str_lst=[key for key in tdms_file['Log']._channels if key.__contains__("Str_Lin") ]
                all_str_lst=[key for key in all_str_lst if not  key.__contains__("Filter") ]
                all_str_lst=[key for key in all_str_lst if  key.__contains__("120") ]
                all_str_lst= sorted(all_str_lst)
                
                
                all_str=[]
                df_str_l=pd.DataFrame()
                for strl in all_str_lst:
                    
                    
                    #Substrac Zero Data
                    Str_ST=tdms_file['Log'][strl][:]-np.mean(zero_tdms_file['Log'][strl][:])
                    
                    strt=np.argmin(abs(tdms_file['Log'][strl].time_track(absolute_time=True)-stc_start))
                    end=np.argmin(abs(tdms_file['Log'][strl].time_track(absolute_time=True)-stc_end))
                    
                    strt=strt+delt_strt
                    end=end-delt_end
                    # print(end)
                    
                    
                    # ###Low pass
                    # sos = signal.butter(N=1, Wn=30, btype='lowpass', fs=1/tdms_file['Log'][strl].properties['wf_increment'], output='sos')
                    
                    # Str_ST1= signal.sosfilt(sos, Str_ST)
                    
                    sigma_est = estimate_sigma(Str_ST, average_sigmas=True)
                    # print(f'Estimated Gaussian noise standard deviation = {sigma_est}')
                    
                    
                    
                    ###Wavelet Filter 
                    wvl_lst=pywt.wavelist(kind='discrete')
                    
                    #hard VisuShrink
                    
                    Str_ST=denoise_wavelet(Str_ST, method='VisuShrink', mode='soft',  
                                           wavelet='sym20', 
                                            sigma=sigma_est*filt_lev,
                                           rescale_sigma='True')#
                    
                    # Str_ST2=denoise_wavelet(Str_ST, method='VisuShrink', mode='hard',  
                    #                        wavelet='sym20', 
                    #                         sigma=sigma_est/8,
                    #                        rescale_sigma='True')#wavelet_levels=5,)
                    
                    
                    
                    all_str.append(Str_ST[strt:end])
                    
                    df_str_l[strl]=Str_ST[strt:end]
                    
                df_str_l.describe().to_csv(os.path.join(Main_ST_R,f_fname+'_Strain_Line.csv'))
                    
                    # plt.figure()
                    # plt.plot(Str_ST[strt:strt+500],c='b')
                    # plt.plot(Str_ST0[strt:strt+500],c='k')
                    # plt.plot(Str_ST2[strt:strt+500],c='y')
                    # plt.plot(Str_ST1[strt:strt+500],c='r')
                    
                    
                fig, ax1 = plt.subplots()
                ax1.boxplot(all_str)
                ax1.set_xlim(0.5, len(all_str_lst) + 0.5)
                ax1.set_xticklabels(all_str_lst,
                    rotation=45, fontsize=8)
                fig.suptitle('Strain Line '+f_fname)
                plt.savefig(os.path.join(Main_ST_R,f_fname+'_Strain_Line.png'),bbox_inches='tight',dpi=500)
                plt.close()
                
            
                ###Ross 
                
                all_ros_lst_all=[key for key in tdms_file['Log']._channels if key.__contains__("Ros") ]
                all_ros_lst_all=[key for key in all_ros_lst_all if not  key.__contains__("Filter") ]
                all_ros_lst_120=[key for key in all_ros_lst_all if  key.__contains__("120") ]
                all_ros_lst_350=[key for key in all_ros_lst_all if  key.__contains__("350") ]
                
                ### Broken sensr
                all_ros_lst_120=[key for key in all_ros_lst_120 if not  key.__contains__("Str_Ros_120_4_4") ]
                
                unique_ros_120=sorted(list(set([key[12:15] for key in all_ros_lst_120])))
                
                all_ros_lst_120_0=[key for key in all_ros_lst_120 if  key.__contains__("_0") ]
                
                for rst in unique_ros_120:
                    
                    rst_cmp=[key for key in all_ros_lst_120 if  key.__contains__('Str_Ros_120_'+rst) ]
                    
                    
                    deg=[key.split('_')[-1] for key in rst_cmp]
                    
                    for dd in range(len(deg)):
                        if 'N' in deg[dd]:
                            deg[dd]=int(re.findall(r'\d+', deg[dd])[0])*-1
                        else:
                            deg[dd]=int(re.findall(r'\d+', deg[dd])[0])
                    
                    deg=np.radians(deg)
                    
                    tran_matrix=np.array([[np.cos(deg[0])**2, np.sin(deg[0])**2, np.cos(deg[0])*np.sin(deg[0])],
                                 [np.cos(deg[1])**2, np.sin(deg[1])**2, np.cos(deg[1])*np.sin(deg[1])],
                                 [np.cos(deg[2])**2, np.sin(deg[2])**2, np.cos(deg[2])*np.sin(deg[2])]])
                    
                    tran_matrix_f=np.linalg.inv(tran_matrix)
                    
                    
                    strt=np.argmin(abs(tdms_file['Log'][rst_cmp[0]].time_track(absolute_time=True)-stc_start))
                    end=np.argmin(abs(tdms_file['Log'][rst_cmp[0]].time_track(absolute_time=True)-stc_end))
                    
                    strt=strt+delt_strt
                    end=end-delt_end
                    
                    
                    a1=np.array(tdms_file['Log'][rst_cmp[0]][strt:end]-np.mean(zero_tdms_file['Log'][rst_cmp[0]][:])).reshape((-1,1))
                    a2=np.array(tdms_file['Log'][rst_cmp[1]][strt:end]-np.mean(zero_tdms_file['Log'][rst_cmp[1]][:])).reshape((-1,1))
                    a3=np.array(tdms_file['Log'][rst_cmp[2]][strt:end]-np.mean(zero_tdms_file['Log'][rst_cmp[2]][:])).reshape((-1,1))
                    
                    ma=np.vstack([tdms_file['Log'][rst_cmp[0]][strt:end]-np.mean(zero_tdms_file['Log'][rst_cmp[0]][:]),
                                 tdms_file['Log'][rst_cmp[1]][strt:end]-np.mean(zero_tdms_file['Log'][rst_cmp[1]][:]),
                                 tdms_file['Log'][rst_cmp[2]][strt:end]-np.mean(zero_tdms_file['Log'][rst_cmp[2]][:])])
                    
                    rosstrain= np.linalg.inv(tran_matrix).dot(ma)
                    
                    #rosstrain= [εx,εy,γxy]
                    
                    #tran_matrix=[1 0 0; 0.5 0.5 0.5; 0.5 0.5 -0.5]
                    #Measured strain-1 (ε1)=εx(cosθ1)2+εy(sinθ1)2+γxysinθ1cosθ1
                    #Measured strain-1 (ε1)=εx(cosθ2)2+εy(sinθ2)2+γxysinθ2cosθ2
                    #Measured strain-1 (ε1)=εx(cosθ3)2+εy(sinθ3)2+γxysinθ3cosθ3
                    # Transformation matrix= [cos(a)^2 sin(a)^2 cos(a)sin(a);
                    #                         cos(b)^2 sin(b)^2 cos(b)sin(b);
                    #                         cos(c)^2 sin(c)^2 cos(c)sin(c)]
                    #  In this case: a=0°    b=45°   c= -45°
                    
                    
                
                
                all_str_120_0_c=[]
                df_120=pd.DataFrame()
                for strl in all_ros_lst_120_0:
                    
                    
                    
                    #Substrac Zero Data
                    Str_ST=tdms_file['Log'][strl][:]-np.mean(zero_tdms_file['Log'][strl][:])
                    
                    strt=np.argmin(abs(tdms_file['Log'][strl].time_track(absolute_time=True)-stc_start))
                    end=np.argmin(abs(tdms_file['Log'][strl].time_track(absolute_time=True)-stc_end))
                    
                    strt=strt+delt_strt
                    end=end-delt_end
                    # print(end)
                    
                    
                    # ###Low pass
                    # sos = signal.butter(N=1, Wn=30, btype='lowpass', fs=1/tdms_file['Log'][strl].properties['wf_increment'], output='sos')
                    
                    # Str_ST1= signal.sosfilt(sos, Str_ST)
                    
                    sigma_est = estimate_sigma(Str_ST, average_sigmas=True)
                    # print(f'Estimated Gaussian noise standard deviation = {sigma_est}')
                    
                    
                    
                    ###Wavelet Filter 
                    wvl_lst=pywt.wavelist(kind='discrete')
                    
                    #hard VisuShrink
                    
                    Str_ST=denoise_wavelet(Str_ST, method='VisuShrink', mode='soft',  
                                           wavelet='sym20', 
                                            sigma=sigma_est*filt_lev,
                                           rescale_sigma='True')#
                    
                    # Str_ST2=denoise_wavelet(Str_ST, method='VisuShrink', mode='hard',  
                    #                        wavelet='sym20', 
                    #                         sigma=sigma_est/8,
                    #                        rescale_sigma='True')#wavelet_levels=5,)
                    
                    
                    
                    all_str_120_0_c.append(Str_ST[strt:end])
                    
                    df_120[strl]=Str_ST[strt:end]
                
                df_120.describe().to_csv(os.path.join(Main_ST_R,f_fname+'_Strain_Ross_0_Deg.csv'))
                    
                fig, ax1 = plt.subplots()
                ax1.boxplot(all_str_120_0_c)
                ax1.set_xlim(0.5, len(all_str_120_0_c) + 0.5)
                ax1.set_xticklabels(all_ros_lst_120_0,
                    rotation=45, fontsize=8)
                fig.suptitle('Strain Ross 0 Deg '+f_fname)
                plt.savefig(os.path.join(Main_ST_R,f_fname+'_Strain_Ross_0_Deg.png'),bbox_inches='tight',dpi=500)
                plt.close()
                
                
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
            
            fatgigue_data={}
            
            filt_lev=2
            
            f_name_s=f_fname.split("_")[0]+"_"+f_fname.split("_")[1]+"_FA"
            f_name_s_f=os.path.join(Main_FT,f_name_s+".pickle")
            
            # if os.path.exists(f_name_s_f):
            #     continue
            
            print('Reading Fatigue File')
            ft_files = [s for s in os.listdir(f_path) if s.__contains__(".tdms") and not s.__contains__("_index")]
            cnt2=0
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
                    
                    
                    
                    if len(all_lds_lst)==1:
                        ld_ch=all_lds_lst[0]
                        tot_load=tdms_file['Log'][ld_ch][:]-np.mean(zero_tdms_file['Log'][all_lds_lst[0]][:])
                        # plt.figure()
                        # plt.plot(tot_load)
                        
                        sigma_est = estimate_sigma(tot_load, average_sigmas=True)
                        tot_load=denoise_wavelet(tot_load, method='VisuShrink', mode='soft',  
                                               wavelet='sym20', 
                                               sigma=sigma_est*filt_lev,
                                               rescale_sigma='True')
                        # plt.plot(tot_load)
                    
                    else:
                        
                        all_loads_filt={}
                        
                        for ld_ch in all_lds_lst:
                        
                            # ld_ch='Load_A_01_PVE'
                            
                            tot_load=(tdms_file['Log'][ld_ch][:]-np.mean(zero_tdms_file['Log'][ld_ch][:]))
                            
                            if np.mean(tot_load)<0:
                                tot_load=tot_load*-1
                            
                            # plt.figure()
                            # plt.plot(tot_load)
                            
                            
                            sigma_est = estimate_sigma(tot_load, average_sigmas=True)
                            tot_load=denoise_wavelet(tot_load, method='VisuShrink', mode='soft',  
                                                   wavelet='sym20', 
                                                   sigma=sigma_est*filt_lev,
                                                   rescale_sigma='True')
                            
                            # plt.plot(tot_load)
                            # plt.title(ld_ch)
                            # plt.ylim(92, 102)
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
                    
                    

                    # fatgigue_data[ld_ch].extend(tot_load)
                    
                     
                    # plt.figure()
                    # contour_heights = tot_load[peaks_up] - properties['prominences']
                    # plt.plot(tot_load,c='k')
                    # plt.plot(peaks, tot_load[peaks], "x")
                    # plt.vlines(x=peaks_up, ymin=contour_heights, ymax=tot_load[peaks_up])
                    # plt.show()
                    
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
                            dif1=abs(tot_load[peaks_up[:-1]]-tot_load[peaks_dwn])
                            dif2=abs(tot_load[peaks_up[1:]]-tot_load[peaks_dwn])
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
                        fatgigue_data['Temp_S_T_10_0']=tdms_file['Log']['Temp_S_T_10'][:]-np.mean(zero_tdms_file['Log']['Temp_S_T_10'][:])
                    else:
                        
                        fsdfdsf
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
                    
                    # print(all_ros_lst_120)
                    
                    unique_ros_120=sorted(list(set([key[12:15] for key in all_ros_lst_120])))
                    
                    all_ros_lst_120_0=[key for key in all_ros_lst_all if  key.__contains__("_0") ]
                    all_ros_lst_120=[key for key in all_ros_lst_120_0 if not  key.__contains__("Str_Ros_120_4_4") ]
                    
                    
                    
                    all_sen_lst=all_pos_lst+all_ros_lst_120_0
                    
                    print(all_sen_lst)
                    
                    
                    for dis in all_sen_lst:
                        print(dis)
                        time_indx=[]
                        time_indx_max=[]
                        time_indx_min=[]
                        
                        disp=tdms_file['Log'][dis][:]-np.mean(zero_tdms_file['Log'][dis][:])
                        
                        
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
                    #                         wavelet='sym20', 
                    #                         sigma=sigma_est*filt_lev,
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
                    
                                 
    # print('No reading')
#%%
    
    
        ###############################################################################
        ############################### FATIGUE 2 #####################################
        ###############################################################################
        
        
        if DO_FA==1:
            
            f_name_s=f_fname.split("_")[0]+"_"+f_fname.split("_")[1]+"_FA"
            f_name_s_f=os.path.join(Main_FT,f_name_s+".pickle")
            
            # with open(f_name_s_f, 'wb') as handle:
            #     pickle.dump(fatgigue_data, handle, protocol=pickle.HIGHEST_PROTOCOL)
                
            # if os.path.exists(f_name_s_f):
            #     fatgigue_data=open(f_name_s_f, 'rb')
            #     # with open(f_name_s_f, 'rb') as fatgigue_data:
            #     fatgigue_data=pickle.load(fatgigue_data)
                
            # else:
            #     with open(f_name_s_f, 'wb') as handle:
            #         pickle.dump(fatgigue_data, handle, protocol=pickle.HIGHEST_PROTOCOL)
            
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
            
            
            with open(f_name_s_f, 'wb') as handle:
                pickle.dump(fatgigue_data, handle, protocol=pickle.HIGHEST_PROTOCOL)
            
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