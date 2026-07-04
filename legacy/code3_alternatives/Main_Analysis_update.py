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
DO_ST=1
DO_FA=1

wavelet_n='db8'
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
#Start process

# tests_dir=tests_dir[10:]

nf=[]
# for indx, row in Test_Log.iterrows():
for indx in tests_dir:
    Type_Test=indx.split('_')[-2]
    print(indx,Type_Test)
    f_fname=indx
    f_path=os.path.join(Main_Input,f_fname)
    if Type_Test=='ZO':
        print('Reading Zero File')
        zero_tdms_file = TdmsFile(os.path.join(f_path,f_fname+'.tdms'))
        continue
###############################################################################
############################### NATUTAL FREQ###################################
###############################################################################    
    
    if Type_Test=='NF':
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
    if Type_Test=='ST':
        if DO_ST==1:
            
            static_data={}
                
            filt_lev=0.4
            
            # delt_0_st=int(900)
            # delt_0_end=int(2000)
            # delt_end=int((8*60)/0.004)
            
            sec_up=60
            sec_dwn=60
            
            delt_strt=int((1)/0.004)
            delt_end=int((1)/0.004)
            
            print('Reading Static File',f_fname)
            
            Main_ST_R=os.path.join(Main_ST,f_fname)
            
            if not os.path.exists(Main_ST_R):
                os.makedirs(Main_ST_R)
                
            
                
            with TdmsFile.open(os.path.join(f_path,f_fname+'.tdms')) as tdms_file:
            #tdms_file = TdmsFile(os.path.join(f_path,f_fname+'.tdms'))
                
                f_name_s=f_fname.replace('.tdms',"")+"_NEW_ST"
                Main_FT_2=Main_FT.split('Testing')[0]+"\\Testing\\All_Life\\Join_Data"
                f_name_s_f=os.path.join(Main_FT_2,f_name_s+".pickle")
                if os.path.exists(f_name_s_f):
                    continue
            
                all_lds_lst=[key for key in tdms_file['Log']._channels if key.__contains__("Load_A") and not key.__contains__("_PVE")]
                
                print(all_lds_lst)
                
                if len(all_lds_lst)==1:
                    ld_ch=all_lds_lst[0]
                    
                    tot_load=tdms_file['Log'][ld_ch][:]-np.mean(zero_tdms_file['Log'][all_lds_lst[0]][:])
                    
                    dist_act=np.array([3.56])
                    
                    if np.mean(tot_load)<0:
                        tot_load=tot_load*-1
                    
                    sigma_est = estimate_sigma(tot_load, average_sigmas=True)
                    tot_load=denoise_wavelet(tot_load, method='BayesShrink', mode='hard',  
                                           wavelet=wavelet_n, 
                                           sigma=sigma_est*filt_lev,
                                           rescale_sigma='True')
                    
                    all_loads_filt={}
                    all_loads_filt[ld_ch]=tot_load
                    all_loads_filt_m=tot_load
                    rbm_all=all_loads_filt_m*dist_act
                    rbm = rbm_all
                    rbm[rbm<0]=0
                    tot_load[tot_load<0]=0 
                    
                else:
                    dist_act=np.array([2.2751, 3.56, 4.477])
                    all_loads_filt={}
                    
                    for ld_ch in all_lds_lst:
                    
                        tot_load=(tdms_file['Log'][ld_ch][:]-np.mean(zero_tdms_file['Log'][ld_ch][:]))
                        
                        if np.mean(tot_load)<0:
                            tot_load=tot_load*-1
                        
                        a_tem=tot_load
                        sigma_est = estimate_sigma(tot_load, average_sigmas=True)
                        tot_load=denoise_wavelet(tot_load, method='VisuShrink', mode='soft',  
                                               wavelet=wavelet_n,
                                               sigma=sigma_est*filt_lev,
                                               rescale_sigma='True')
                        all_loads_filt[ld_ch]=tot_load
                    
                    len_d=all_loads_filt[ld_ch].shape[0]
                    all_loads_filt_m=np.empty((len_d, len(all_lds_lst)))
                    
                    cnt_l=0
                    for ld_ch in all_lds_lst:
                        if all_loads_filt[ld_ch].shape[0]!=len_d:
                           all_loads_filt[ld_ch]=all_loads_filt[ld_ch][:min(all_loads_filt[ld_ch].shape[0],len_d)] 
                            
                            # quit()
                        # else:
                        all_loads_filt_m[:,cnt_l]=all_loads_filt[ld_ch]
                        cnt_l+=1
                        
                    
                        # plt.plot(tot_load) 
                
                if len(all_lds_lst)>1:
                    rbm_all=all_loads_filt_m*dist_act
                    rbm = np.sum(rbm_all, axis=1)
                    rbm[rbm<0]=0
                    tot_load= np.sum(all_loads_filt_m, axis=1)
                    tot_load[tot_load<0]=0 
                    
                
                ###############################################################
                ################Target###########################################
                ###############################################################
                
                targ_load=statistics.mode(rbm.astype(int))
                stc_start0=tdms_file['Log'][ld_ch].time_track(absolute_time=True)[np.where(rbm.astype(int)==targ_load)[0][0]]
                stc_end0=tdms_file['Log'][ld_ch].time_track(absolute_time=True)[np.where(rbm.astype(int)==targ_load)[0][-1]]
                
                
                print('rbm',targ_load)
                print('min',(stc_end0-stc_start0)// np.timedelta64(1, 'm'))
                
                
                # print(stc_start,stc_end)
                
                stc_start=tdms_file['Log'][ld_ch].time_track(absolute_time=True)[np.argmin(abs(tdms_file['Log'][ld_ch].time_track(absolute_time=True)-stc_start0))]
                stc_end=tdms_file['Log'][ld_ch].time_track(absolute_time=True)[np.argmin(abs(tdms_file['Log'][ld_ch].time_track(absolute_time=True)-stc_end0))]
                
                print(stc_start,stc_end)
                
                strt=np.argmin(abs(tdms_file['Log'][all_lds_lst[0]].time_track(absolute_time=True)-stc_start0))
                end=np.argmin(abs(tdms_file['Log'][all_lds_lst[0]].time_track(absolute_time=True)-stc_end0))
                
                all_loads_filt_com={}
                tot_loads_up_filt={}
                tot_loads_mid_filt={}
                tot_loads_dwn_filt={}
                
                
                for ld_ch in all_lds_lst:
                    
                    ######
                    ######UP
                    ######
                    
                    tot_load_up=(tdms_file['Log'][ld_ch][:strt]-np.mean(zero_tdms_file['Log'][ld_ch][:]))
                    if np.mean(tot_load_up)<0:
                        tot_load_up=tot_load_up*-1
                    
                    sigma_est = estimate_sigma(tot_load_up, average_sigmas=True)
                    tot_load_up=denoise_wavelet(tot_load_up, method='VisuShrink', mode='soft',  
                                           wavelet=wavelet_n,
                                           sigma=sigma_est*filt_lev,
                                           rescale_sigma='True')
                    
                    tot_loads_up_filt[ld_ch]=tot_load_up
                    ######
                    ######MID
                    ######
                    
                    
                    tot_load_mid=(tdms_file['Log'][ld_ch][strt:end]-np.mean(zero_tdms_file['Log'][ld_ch][:]))
                    
                    if np.mean(tot_load_mid)<0:
                        tot_load_mid=tot_load_mid*-1
                    
                    sigma_est = estimate_sigma(tot_load_mid, average_sigmas=True)
                    tot_load_mid=denoise_wavelet(tot_load_mid, method='VisuShrink', mode='soft',  
                                          wavelet=wavelet_n, 
                                           sigma=sigma_est*filt_lev,
                                           rescale_sigma='True')

                    
                    tot_loads_mid_filt[ld_ch]=tot_load_mid
                    
                    ######
                    ######DOWN
                    ######
                    
                    
                    tot_load_dwn=(tdms_file['Log'][ld_ch][end:]-np.mean(zero_tdms_file['Log'][ld_ch][:]))
                    
                    if np.mean(tot_load_dwn)<0:
                        tot_load_dwn=tot_load_dwn*-1
                    
                    
                    
                    sigma_est = estimate_sigma(tot_load_dwn, average_sigmas=True)
                    tot_load_dwn=denoise_wavelet(tot_load_dwn, method='VisuShrink', mode='soft',  
                                           wavelet=wavelet_n,
                                           sigma=sigma_est*filt_lev,
                                           rescale_sigma='True')                    
                    
                    
                    tot_loads_dwn_filt[ld_ch]=tot_load_dwn
                    
                    ######
                    ######COMBINE
                    ######
                    tot_load= np.concatenate((tot_load_up, tot_load_mid, tot_load_dwn), axis=0)
                    all_loads_filt_com[ld_ch]=tot_load
                
                len_d=all_loads_filt_com[ld_ch].shape[0]
                all_loads_filt_m=np.empty((len_d, len(all_lds_lst)))
                
                cnt_l=0
                for ld_ch in all_lds_lst:
                    if all_loads_filt_com[ld_ch].shape[0]!=len_d:
                       all_loads_filt_m[ld_ch]=all_loads_filt_com[ld_ch][:min(all_loads_filt_com[ld_ch].shape[0],len_d)] 
                        
                        # quit()
                    else:
                        all_loads_filt_m[:,cnt_l]=all_loads_filt[ld_ch]
                    cnt_l+=1
                    
                
                if len(all_lds_lst)>1:
                    rbm_all=all_loads_filt_m*dist_act
                    rbm = np.sum(rbm_all, axis=1)
                    rbm[rbm<0]=0
                    tot_load= np.sum(all_loads_filt_m, axis=1)
                    tot_load[tot_load<0]=0
                    
                
                targ_load=statistics.mode(rbm.astype(int))
                
                
            
                ######################################
                ##############Save Data###############
                ######################################
                static_data['Load_Tot']=tot_load
                static_data['Moment_Tot']=rbm
                static_data['Loas_All']=all_loads_filt_m
                static_data['Moment_All']=rbm_all
                static_data['Targuet_Load']=statistics.mode(tot_load.astype(int))
                static_data['Targuet_RBM']=targ_load
                static_data['Satic_Duration']=(stc_end0-stc_start0)// np.timedelta64(1, 'm')
                static_data['Satic_Indx_Start']=strt
                static_data['Satic_Indx_End']=end
                static_data['dist_act']=dist_act
                static_data['All_loads_up_filt']=tot_loads_up_filt
                static_data['All_load_mid']=tot_loads_mid_filt
                static_data['Tot_RBM_mid']=rbm[strt:end]
                static_data['All_loads_dwn_filt']=tot_loads_dwn_filt
                static_data['Temp_S_T_10_Time']=tdms_file['Log']['Temp_S_T_10'].time_track(absolute_time=True,accuracy='ms')
                static_data['Temp_S_T_10']=tdms_file['Log']['Temp_S_T_10'][:]
                static_data['Temp_S_T_10_0']=tdms_file['Log']['Temp_S_T_10'][:]-np.mean(zero_tdms_file['Log']['Temp_S_T_10'][:])
                
                
                ###############################################################
                ###############################################################
                ###############################################################
                ###################Displacement################################
                ###############################################################
                ###############################################################
                ###############################################################
                
                ###Displacement
                
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
                    disp=tdms_file['Log'][dis][:]-np.mean(zero_tdms_file['Log'][dis][:])
                    strt=np.argmin(abs(tdms_file['Log'][dis].time_track(absolute_time=True)-stc_start))
                    end=np.argmin(abs(tdms_file['Log'][dis].time_track(absolute_time=True)-stc_end))
                    
                    ######
                    ######UP
                    ######
                    
                    dis_up=(tdms_file['Log'][dis][:strt]-np.mean(zero_tdms_file['Log'][dis][:]))
                    sigma_est = estimate_sigma(dis_up, average_sigmas=True)
                    dis_up=denoise_wavelet(dis_up, method='VisuShrink', mode='soft',  
                                           wavelet=wavelet_n,
                                           sigma=sigma_est*filt_lev,
                                           rescale_sigma='True')
                    
                    ######
                    ######MID
                    ######
                    
                    
                    dis_mid=(tdms_file['Log'][dis][strt:end]-np.mean(zero_tdms_file['Log'][dis][:]))
                    sigma_est = estimate_sigma(dis_mid, average_sigmas=True)
                    dis_mid=denoise_wavelet(dis_mid, method='VisuShrink', mode='soft',  
                                           wavelet=wavelet_n,
                                           sigma=sigma_est*filt_lev,
                                           rescale_sigma='True')
                    ######
                    ######DOWN
                    ######
                    
                    dis_dwn=(tdms_file['Log'][dis][end:]-np.mean(zero_tdms_file['Log'][dis][:]))
                    sigma_est = estimate_sigma(dis_dwn, average_sigmas=True)
                    dis_dwn=denoise_wavelet(dis_dwn, method='VisuShrink', mode='soft',  
                                           wavelet=wavelet_n, 
                                           sigma=sigma_est*filt_lev,
                                           rescale_sigma='True')                    
                    
                    
                    ######
                    ######COMBINE
                    ######
                    # disp= np.concatenate((dis_up, dis_mid, dis_dwn), axis=0)
                    
                    ######################################
                    ##############Save Data###############
                    ######################################
                    static_data[dis+'_u']=dis_up
                    static_data[dis+'_c']=dis_mid
                    static_data[dis+'_d']=dis_dwn
                    ######################################
                    ######################################
                    ######################################
                
                
                
            
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
                    
                    print(rst)
                    
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
                    
                    
                    a1=np.array(tdms_file['Log'][rst_cmp[0]]-np.mean(zero_tdms_file['Log'][rst_cmp[0]][:]))#.reshape((-1,1))
                    a2=np.array(tdms_file['Log'][rst_cmp[1]]-np.mean(zero_tdms_file['Log'][rst_cmp[1]][:]))#.reshape((-1,1))
                    a3=np.array(tdms_file['Log'][rst_cmp[2]]-np.mean(zero_tdms_file['Log'][rst_cmp[2]][:]))#.reshape((-1,1))
                    
                    ######
                    ######UP
                    ######
                    a1_up=a1[:strt]
                    a2_up=a2[:strt]
                    a3_up=a3[:strt]
                    
                    sigma_est = estimate_sigma(a1_up, average_sigmas=True)
                    a1_up=denoise_wavelet(a1_up, method='VisuShrink', mode='soft',  
                                           wavelet=wavelet_n,
                                           sigma=sigma_est*filt_lev,
                                           rescale_sigma='True')
                    sigma_est = estimate_sigma(a2_up, average_sigmas=True)
                    a2_up=denoise_wavelet(a2_up, method='VisuShrink', mode='soft',  
                                          wavelet=wavelet_n,
                                           sigma=sigma_est*filt_lev,
                                           rescale_sigma='True')
                    sigma_est = estimate_sigma(a3_up, average_sigmas=True)
                    a3_up=denoise_wavelet(a3_up, method='VisuShrink', mode='soft',  
                                           wavelet=wavelet_n,
                                           sigma=sigma_est*filt_lev,
                                           rescale_sigma='True')
                    
                    ######
                    ######MID
                    ######
                    a1_md=a1[strt:end]
                    a2_md=a2[strt:end]
                    a3_md=a3[strt:end]
                    
                    sigma_est = estimate_sigma(a1_md, average_sigmas=True)
                    a1_md=denoise_wavelet(a1_md, method='VisuShrink', mode='soft',  
                                           wavelet=wavelet_n, 
                                           sigma=sigma_est*filt_lev,
                                           rescale_sigma='True')
                    sigma_est = estimate_sigma(a2_md, average_sigmas=True)
                    a2_md=denoise_wavelet(a2_md, method='VisuShrink', mode='soft',  
                                           wavelet=wavelet_n,
                                           sigma=sigma_est*filt_lev,
                                           rescale_sigma='True')
                    sigma_est = estimate_sigma(a3_md, average_sigmas=True)
                    a3_md=denoise_wavelet(a3_md, method='VisuShrink', mode='soft',  
                                           wavelet=wavelet_n, 
                                           sigma=sigma_est*filt_lev,
                                           rescale_sigma='True')
                    ######
                    ######DOWN
                    ######
                    a1_dw=a1[end:]
                    a2_dw=a2[end:]
                    a3_dw=a3[end:]
                    
                    sigma_est = estimate_sigma(a1_dw, average_sigmas=True)
                    a1_dw=denoise_wavelet(a1_dw, method='VisuShrink', mode='soft',  
                                          wavelet=wavelet_n,
                                           sigma=sigma_est*filt_lev,
                                           rescale_sigma='True')
                    sigma_est = estimate_sigma(a2_dw, average_sigmas=True)
                    a2_dw=denoise_wavelet(a2_dw, method='VisuShrink', mode='soft',  
                                           wavelet=wavelet_n,
                                           sigma=sigma_est*filt_lev,
                                           rescale_sigma='True')
                    sigma_est = estimate_sigma(a3_dw, average_sigmas=True)
                    a3_dw=denoise_wavelet(a3_dw, method='VisuShrink', mode='soft',  
                                           wavelet=wavelet_n, 
                                           sigma=sigma_est*filt_lev,
                                           rescale_sigma='True')
                    
                    ######
                    ######COMBINE
                    ######
                    a1= np.concatenate((a1_up, a1_md, a1_dw), axis=0)
                    a2= np.concatenate((a2_up, a2_md, a2_dw), axis=0)
                    a3= np.concatenate((a3_up, a3_md, a3_dw), axis=0)
                    
                    ma=np.vstack([a1,a2,a3])
                    # ma=np.vstack([tdms_file['Log'][rst_cmp[0]][strt:end]-np.mean(zero_tdms_file['Log'][rst_cmp[0]][:]),
                    #              tdms_file['Log'][rst_cmp[1]][strt:end]-np.mean(zero_tdms_file['Log'][rst_cmp[1]][:]),
                    #              tdms_file['Log'][rst_cmp[2]][strt:end]-np.mean(zero_tdms_file['Log'][rst_cmp[2]][:])])
                    
                    rosstrain= np.linalg.inv(tran_matrix).dot(ma)
                    
                    
                    ######################################
                    ##############Save Data###############
                    ######################################
                    static_data['Str_Ros_120_'+rst+'_x_u']=rosstrain[0][:strt]
                    static_data['Str_Ros_120_'+rst+'_y_u']=rosstrain[1][:strt]
                    static_data['Str_Ros_120_'+rst+'_xy_u']=rosstrain[2][:strt]
                    
                    static_data['Str_Ros_120_'+rst+'_x_c']=rosstrain[0][strt:end]
                    static_data['Str_Ros_120_'+rst+'_y_c']=rosstrain[1][strt:end]
                    static_data['Str_Ros_120_'+rst+'_xy_c']=rosstrain[2][strt:end]
                    
                    static_data['Str_Ros_120_'+rst+'_x_d']=rosstrain[0][end:]
                    static_data['Str_Ros_120_'+rst+'_x_d']=rosstrain[1][end:]
                    static_data['Str_Ros_120_'+rst+'_x_d']=rosstrain[2][end:]
                    
                    ######################################
                    ######################################
                    ######################################
                    
                    #rosstrain= [εx,εy,γxy]
                    
                    #tran_matrix=[1 0 0; 0.5 0.5 0.5; 0.5 0.5 -0.5]
                    #Measured strain-1 (ε1)=εx(cosθ1)2+εy(sinθ1)2+γxysinθ1cosθ1
                    #Measured strain-1 (ε1)=εx(cosθ2)2+εy(sinθ2)2+γxysinθ2cosθ2
                    #Measured strain-1 (ε1)=εx(cosθ3)2+εy(sinθ3)2+γxysinθ3cosθ3
                    # Transformation matrix= [cos(a)^2 sin(a)^2 cos(a)sin(a);
                    #                         cos(b)^2 sin(b)^2 cos(b)sin(b);
                    #                         cos(c)^2 sin(c)^2 cos(c)sin(c)]
                    #  In this case: a=0°    b=45°   c= -45°
                    
                    
                
                
                
                
                with open(f_name_s_f, 'wb') as handle:
                    pickle.dump(static_data, handle, protocol=pickle.HIGHEST_PROTOCOL)
                
                
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
 
    if Type_Test=='FA':
        cnt=0
        
        if DO_FA==1:
            
            
            # f_name_s=f_fname.split("_")[0]+"_"+f_fname.split("_")[1]+"_FA"
            # f_name_s_f=os.path.join(Main_FT,f_name_s+".pickle")
            
            # f_name_s=f_fname+"_NEW_FA"
            # Main_FT_2=Main_FT.split('Testing')[0]+"\\Testing\\All_Life"
            # f_name_s_f=os.path.join(Main_FT_2,f_name_s+".pickle")
            
            # if os.path.exists(f_name_s_f):
            #     continue
            
            print('Reading Fatigue File')
            ft_files = [s for s in os.listdir(f_path) if s.__contains__(".tdms") and not s.__contains__("_index")]
            cnt2=0
            
            for ffiles in ft_files:
                cnt=0
                fatgigue_data={}
                
                filt_lev=3
                
                f_name_s=ffiles.replace('.tdms',"")+"_NEW_FA"
                Main_FT_2=Main_FT.split('Testing')[0]+"\\Testing\\All_Life\\Join_Data"
                f_name_s_f=os.path.join(Main_FT_2,f_name_s+".pickle")
                
                
                if os.path.exists(f_name_s_f):
                    continue
                
                # cnt2=0
                # if cnt2==0:
                    
                #     ffiles=f_fname+'.tdms'
                #     cnt2=cnt2+1
                # else:
                #     ffiles=f_fname+'_'+str(cnt2)+'.tdms'
                #     cnt2=cnt2+1
                    
                print(ffiles)
                
                with TdmsFile.open(os.path.join(f_path,ffiles)) as tdms_file:
                #tdms_file = TdmsFile(os.path.join(f_path,f_fname+'.tdms'))
                    all_lds_lst=[key for key in tdms_file['Log']._channels if key.__contains__("Load_A") and not key.__contains__("_PVE")]
                    
                    print(all_lds_lst)
                    
                    
                    
                    if len(all_lds_lst)==1:
                        ld_ch=all_lds_lst[0]
                        
                        tot_load=tdms_file['Log'][ld_ch][:]-np.mean(zero_tdms_file['Log'][all_lds_lst[0]][:])
                        
                        dist_act=np.array([3.56])
                        
                        if np.mean(tot_load)<0:
                            tot_load=tot_load*-1
                        # plt.figure()
                        # plt.plot(tot_load)
                        
                        sigma_est = estimate_sigma(tot_load, average_sigmas=True)
                        # tot_load=denoise_wavelet(tot_load, method='BayesShrink', mode='hard',  
                        #                        wavelet='sym9', 
                        #                        sigma=sigma_est*filt_lev,
                        #                        rescale_sigma='True')
                        
                        s=6
                        denoise_kwargs = dict( wavelet=wavelet_n,
                                              sigma=sigma_est*filt_lev,
                                              rescale_sigma=True)
                        tot_load = cycle_spin(tot_load, func=denoise_wavelet, max_shifts=s,
                            func_kw=denoise_kwargs, channel_axis=-1)
                        
                        all_loads_filt_m=tot_load
                        rbm_all=all_loads_filt_m*dist_act
                        rbm = rbm_all
                        rbm[rbm<0]=0
                        tot_load[tot_load<0]=0 
                        # plt.plot(tot_load)
                        # dasd
                    
                    else:
                        dist_act=np.array([2.2751, 3.56, 4.477])
                        all_loads_filt={}
                        
                        for ld_ch in all_lds_lst:
                        
                            # ld_ch='Load_A_01_PVE'
                            
                            tot_load=(tdms_file['Log'][ld_ch][:]-np.mean(zero_tdms_file['Log'][ld_ch][:]))
                            
                            if np.mean(tot_load)<0:
                                tot_load=tot_load*-1
                            
                            # plt.figure()
                            # plt.plot(tot_load)
                            
                            sigma_est = estimate_sigma(tot_load, average_sigmas=True)
                            # tot_load=denoise_wavelet(tot_load, method='VisuShrink', mode='soft',  
                            #                        wavelet='sym9', 
                            #                        sigma=sigma_est*filt_lev,
                            #                        rescale_sigma='True')
                            
                            s=6
                            denoise_kwargs = dict( wavelet=wavelet_n,
                                                  sigma=sigma_est*filt_lev,
                                                  rescale_sigma=True)
                            tot_load = cycle_spin(tot_load, func=denoise_wavelet, max_shifts=s,
                                func_kw=denoise_kwargs, channel_axis=-1)
                            
                            
                            # plt.plot(tot_load)
                          
                            # print(peak_signal_noise_ratio(a_tem,tot_load,data_range=a_tem.max() - a_tem.min()))
                            # plt.plot(tot_load)
                            # plt.title(ld_ch)
                            # plt.ylim(60, 90)
                            # plt.xlim(2600000,2601000)
                            
                            # print(len(tot_load))
                            
                            all_loads_filt[ld_ch]=tot_load
                        
                        len_d=all_loads_filt[ld_ch].shape[0]
                        all_loads_filt_m=np.empty((len_d, len(all_lds_lst)))
                        
                        cnt_l=0
                        for ld_ch in all_lds_lst:
                            if all_loads_filt[ld_ch].shape[0]!=len_d:
                               all_loads_filt[ld_ch]=all_loads_filt[ld_ch][:min(all_loads_filt[ld_ch].shape[0],len_d)] 
                                
                                # quit()
                            else:
                                all_loads_filt_m[:,cnt_l]=all_loads_filt[ld_ch]
                            cnt_l+=1
                            
                        
                            # plt.plot(tot_load) 
                    
                    if len(all_lds_lst)>1:
                        rbm_all=all_loads_filt_m*dist_act
                        rbm = np.sum(rbm_all, axis=1)
                        rbm[rbm<0]=0
                        tot_load= np.sum(all_loads_filt_m, axis=1)
                        tot_load[tot_load<0]=0 
                        
                    peaks_up, _ = find_peaks(rbm, prominence=(np.sum(dist_act*5)))#,distance=100)
                    peaks_dwn, _ = find_peaks(rbm*-1, prominence=(np.sum(dist_act*5)))#,distance=100)
                    
                    if peaks_up[0]<peaks_dwn[0]:
                        peaks_dwn=np.insert(peaks_dwn, 0,0)
                    if peaks_up[-1]>peaks_dwn[-1]:
                        peaks_dwn=np.append(peaks_dwn,tot_load.shape[0]-1)
                    
                    if (peaks_dwn.shape[0]-peaks_up.shape[0]) != 1 :
                        print('Add filter')
                        filt_lev=4
                        s=6
                        sigma_est = estimate_sigma(rbm, average_sigmas=True)
                        denoise_kwargs = dict( wavelet=wavelet_n,
                                              sigma=sigma_est*filt_lev,
                                              rescale_sigma=True)
                        rbm = cycle_spin(rbm, func=denoise_wavelet, max_shifts=s,
                            func_kw=denoise_kwargs, channel_axis=-1)
                        
                        peaks_up, _ = find_peaks(rbm, prominence=(np.sum(dist_act*5)))#,distance=100)
                        peaks_dwn, _ = find_peaks(rbm*-1, prominence=(np.sum(dist_act*5)))#,distance=100)
                        if peaks_up[0]<peaks_dwn[0]:
                            peaks_dwn=np.insert(peaks_dwn, 0,0)
                        if peaks_up[-1]>peaks_dwn[-1]:
                            peaks_dwn=np.append(peaks_dwn,tot_load.shape[0]-1)
                        
                    else:
                        print('No extra filter')
                    if (peaks_dwn.shape[0]-peaks_up.shape[0]) != 1 :
                        print('Error After  filter')
                    
                    for c_i in range(peaks_up.shape[0]):
                        if peaks_up[c_i]<peaks_dwn[c_i]:
                            print(c_i,'Error 1')
                            print('Add filter')
                            filt_lev=4
                            s=6
                            sigma_est = estimate_sigma(rbm, average_sigmas=True)
                            
                            denoise_kwargs = dict( wavelet=wavelet_n,
                                                  sigma=sigma_est*filt_lev,
                                                  rescale_sigma=True)
                            rbm = cycle_spin(rbm, func=denoise_wavelet, max_shifts=s,
                                func_kw=denoise_kwargs, channel_axis=-1)
                            peaks_up, _ = find_peaks(rbm, prominence=(np.sum(dist_act*5)))#,distance=100)
                            peaks_dwn, _ = find_peaks(rbm*-1, prominence=(np.sum(dist_act*5)))#,distance=100)
                            if peaks_up[0]<peaks_dwn[0]:
                                peaks_dwn=np.insert(peaks_dwn, 0,0)
                            if peaks_up[-1]>peaks_dwn[-1]:
                                peaks_dwn=np.append(peaks_dwn,tot_load.shape[0]-1)
                                
                            break
                        
                        if peaks_dwn[c_i+1]<peaks_up[c_i]:
                            print(c_i,'Error 2')
                            print('Add filter')
                            filt_lev=4
                            s=6
                            sigma_est = estimate_sigma(rbm, average_sigmas=True)
                            
                            denoise_kwargs = dict( wavelet=wavelet_n,
                                                  sigma=sigma_est*filt_lev,
                                                  rescale_sigma=True)
                            rbm = cycle_spin(rbm, func=denoise_wavelet, max_shifts=s,
                                func_kw=denoise_kwargs, channel_axis=-1)
                            peaks_up, _ = find_peaks(rbm, prominence=(np.sum(dist_act*5)))#),distance=100)
                            peaks_dwn, _ = find_peaks(rbm*-1, prominence=(np.sum(dist_act*5)))#),distance=100)
                            if peaks_up[0]<peaks_dwn[0]:
                                peaks_dwn=np.insert(peaks_dwn, 0,0)
                            if peaks_up[-1]>peaks_dwn[-1]:
                                peaks_dwn=np.append(peaks_dwn,tot_load.shape[0]-1)
                            
                            break      
                    
                    for ci in range(len(peaks_up)):
                        if peaks_up[ci]<peaks_dwn[ci]:
                            print(ci,'Error 1')
                            fdsf
                        if peaks_dwn[ci+1]<peaks_up[ci]:
                            print(ci,'Error 2')
                            dsfs
                    if (peaks_dwn.shape[0]-peaks_up.shape[0]) != 1 :
                        print('Error_count')
                        fdsf
                    print('No of cyles :',len(peaks_up),len(peaks_dwn))
                    # fatgigue_data[ld_ch].extend(tot_load)
                    
                     
                    # plt.figure()
                    # plt.plot(tot_load)
                    # plt.plot(peaks_up, tot_load[peaks_up], "x")
                    # plt.plot(peaks_dwn, tot_load[peaks_dwn], "o")
                    # plt.show()
                    
                    
                    #####Sort _indx peak
                    peaks_sot=[]
                    peaks_sot.append(peaks_dwn[0])
                    for ci in range(len(peaks_up)):
                        peaks_sot.append(peaks_up[ci])
                        peaks_sot.append(peaks_dwn[ci+1])
                        
                    
                    if peaks_dwn.shape[0]-peaks_up.shape[0]==1:
                        if peaks_dwn[0]<peaks_up[0]:
                            print('ENTER 0')
                            peaks_all=np.sort(np.concatenate((peaks_dwn,peaks_up)))
                            time_all=tdms_file['Log'][ld_ch].time_track(absolute_time=True,accuracy='ms')[peaks_dwn]
                            time_dwn=tdms_file['Log'][ld_ch].time_track(absolute_time=True,accuracy='ms')[peaks_all]
                            time_up =tdms_file['Log'][ld_ch].time_track(absolute_time=True,accuracy='ms')[peaks_up]
                            time_sort=tdms_file['Log'][ld_ch].time_track(absolute_time=True,accuracy='ms')[peaks_sot]
                            ###############################################################
                            ################Load###########################################
                            ###############################################################
                            
                            dif1=abs(tot_load[peaks_dwn[:-1]]-tot_load[peaks_up])
                            dif2=abs(tot_load[peaks_dwn[1:]]-tot_load[peaks_up])
                            Load_Diff=0.5*(dif1+dif2)
                            tot_load_max=tot_load[peaks_up]
                            tot_load_mmin=tot_load[peaks_dwn]
                            tot_load_pks=tot_load[peaks_all]
                            
                            ###############################################################
                            ##############Moment###########################################
                            ###############################################################
                            
                            dif1_m=abs(rbm[peaks_dwn[:-1]]-rbm[peaks_up])
                            dif2_m=abs(rbm[peaks_dwn[1:]]-rbm[peaks_up])
                            Moment_Diff=0.5*(dif1_m+dif2_m)
                            tot_rbm_max=rbm[peaks_up]
                            tot_rbm_mmin=rbm[peaks_dwn]
                            tot_rbm_pks=rbm[peaks_all]
                        
                        
                        else:
                            print('FAIL_1')
                            plt.figure()
                            plt.plot(tot_load)
                            plt.plot(peaks_up, tot_load[peaks_up], "x")
                            plt.plot(peaks_dwn, tot_load[peaks_dwn], "o")
                            figManager = plt.get_current_fig_manager()
                            figManager.window.showMaximized()
                            plt.show()
                            ffd
                            # exit()
                            
                    else :
                        print('FAIL_2')
                        plt.figure()
                        plt.plot(tot_load)
                        plt.plot(peaks_up, tot_load[peaks_up], "x", markersize=20)
                        plt.plot(peaks_dwn, tot_load[peaks_dwn], "o", markersize=20)
                        figManager = plt.get_current_fig_manager()
                        figManager.window.showMaximized()
                        plt.show()
                        sdfds
                        # exit()
                        
                    if cnt==0:
                        fatgigue_data['Load_Tot']=tot_load
                        fatgigue_data['Moment_Tot']=rbm
                        fatgigue_data['Load_All']=all_loads_filt_m
                        fatgigue_data['Moment_All']=rbm_all
                        fatgigue_data['peaks_all']=peaks_all
                        fatgigue_data['time_loads_p']=time_all
                        fatgigue_data['time_up']=tdms_file['Log'][ld_ch].time_track(absolute_time=True,accuracy='ms')[peaks_up]
                        fatgigue_data['time_dwn']=tdms_file['Log'][ld_ch].time_track(absolute_time=True,accuracy='ms')[peaks_dwn]
                        fatgigue_data['peaks_up']=peaks_up
                        fatgigue_data['peaks_dwn']=peaks_dwn
                        fatgigue_data['peaks_sot']=peaks_sot
                        fatgigue_data['Load_Diff']=Load_Diff
                        fatgigue_data['Moment_Diff']=Moment_Diff
                        try:
                            fatgigue_data['Temp_S_T_10_Time']=tdms_file['Log']['Temp_S_T_10'].time_track(absolute_time=True,accuracy='ms')
                            fatgigue_data['Temp_S_T_10']=tdms_file['Log']['Temp_S_T_10'][:]
                            fatgigue_data['Temp_S_T_10_0']=tdms_file['Log']['Temp_S_T_10'][:]-np.mean(zero_tdms_file['Log']['Temp_S_T_10'][:])
                        except:
                            print('No_temperature')
                    else:
                        
                        sdas
                
                    
                    
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
                        
                        disp=tdms_file['Log'][dis][:]-np.nanmean(zero_tdms_file['Log'][dis][:])
                        disp_o=tdms_file['Log'][dis+'_Filter'][:]
                        # print(np.nanmean(zero_tdms_file['Log'][dis][:]))
                        # plt.figure()
                        # plt.plot(disp)
                        # plt.plot(disp_o,c='k')
                        
                        sigma_est = estimate_sigma(disp, average_sigmas=True)
                        # disp=denoise_wavelet(disp, method='VisuShrink', mode='soft',  
                        #                         wavelet='sym9', 
                        #                         sigma=sigma_est*filt_lev,
                        #                         rescale_sigma='True')
                        
                        s=6
                        denoise_kwargs = dict( wavelet=wavelet_n,
                                              sigma=sigma_est*filt_lev,
                                              rescale_sigma=True)
                        disp = cycle_spin(disp, func=denoise_wavelet, max_shifts=s,
                            func_kw=denoise_kwargs, channel_axis=-1)
                        # plt.figure()
                        # plt.plot(disp)
                        # dsad
                        cnt_test=-1
                        up=1
                        time_dis=tdms_file['Log'][dis].time_track(absolute_time=True)
                        for k in time_sort:
                            
                            dtime=-1
                            while dtime<0:
                                cnt_test+=1
                                if cnt_test >=time_dis.shape[0]: 
                                    cnt_test=time_dis.shape[0]-1
                                    dtime=1
                                else:
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
                        
                        if peaks_dwn[-1]>=disp.shape[0]:
                            peaks_dwn_t=peaks_dwn
                            peaks_dwn_t[-1]=disp.shape[0]-1
                        else:
                            peaks_dwn_t=peaks_dwn
                        disp_max=disp[time_indx_max]
                        disp_min=disp[time_indx_min]
                        dif1=abs(disp[time_indx_min[:-1]]-disp[time_indx_max])
                        dif2=abs(disp[time_indx_min[1:]]-disp[time_indx_max])
                        disp_dif=0.5*(dif1+dif2)
                        # disp=disp[time_indx]
                        
                        # if cnt==0:
                        fatgigue_data[dis]=disp
                        fatgigue_data[dis+'_max']=disp_max
                        fatgigue_data[dis+'_min']=disp_min
                        fatgigue_data[dis+'_dif']=disp_dif
                        fatgigue_data[dis+'_indx_max']=time_indx_max
                        fatgigue_data[dis+'_indx_min']=time_indx_min
                        
                        
                        # plt.plot(disp)
                        # plt.plot(time_indx_max,disp[time_indx_max],'o')
                        # dsad
                        # else:
                            # dsad
                            
                    
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
                        print(rst)
                        
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
                        
                        
                        a1=np.array(tdms_file['Log'][rst_cmp[0]]-np.mean(zero_tdms_file['Log'][rst_cmp[0]][:])).reshape((-1,1))
                        a2=np.array(tdms_file['Log'][rst_cmp[1]]-np.mean(zero_tdms_file['Log'][rst_cmp[1]][:])).reshape((-1,1))
                        a3=np.array(tdms_file['Log'][rst_cmp[2]]-np.mean(zero_tdms_file['Log'][rst_cmp[2]][:])).reshape((-1,1))
                        
                        sigma_est = estimate_sigma(a1, average_sigmas=True)
                        a1=denoise_wavelet(a1, method='VisuShrink', mode='soft',  
                                               wavelet=wavelet_n,
                                               sigma=sigma_est*filt_lev,
                                               rescale_sigma='True')
                        sigma_est = estimate_sigma(a2, average_sigmas=True)
                        a2=denoise_wavelet(a2, method='VisuShrink', mode='soft',  
                                               wavelet=wavelet_n,
                                               sigma=sigma_est*filt_lev,
                                               rescale_sigma='True')
                        sigma_est = estimate_sigma(a3, average_sigmas=True)
                        a3=denoise_wavelet(a3, method='VisuShrink', mode='soft',  
                                               wavelet=wavelet_n, 
                                               sigma=sigma_est*filt_lev,
                                               rescale_sigma='True')
                        
                        ma=np.vstack([a1.reshape(-1),a2.reshape(-1),a3.reshape(-1)])
                        
                        
                        # ma=np.vstack([tdms_file['Log'][rst_cmp[0]]-np.mean(zero_tdms_file['Log'][rst_cmp[0]][:]),
                        #               tdms_file['Log'][rst_cmp[1]]-np.mean(zero_tdms_file['Log'][rst_cmp[1]][:]),
                        #               tdms_file['Log'][rst_cmp[2]]-np.mean(zero_tdms_file['Log'][rst_cmp[2]][:])])
                        
                        # ma=np.stack((a1,a2,a3), axis=0)
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
                        
                        time_indx=[]
                        time_indx_max=[]
                        time_indx_min=[]
                        # rosstrain_c= ['εx','εy','γxy']
                        rosstrain_c= ['x','y','xy']
                        for disp_i in range(rosstrain.shape[0]):
                            disp=rosstrain[disp_i,:]
                            dis2=rst_cmp[0][:-1]+str(0)
                            dis=rst_cmp[0][:-1]+rosstrain_c[disp_i]
                            
                            
                            
                            # cnt_test=-1
                            # up=1
                            # time_dis=tdms_file['Log'][rst_cmp[0]].time_track(absolute_time=True)
                            # for k in time_all:
                                
                            #     dtime=-1
                            #     while dtime<0:
                            #         cnt_test+=1
                            #         if cnt_test >=time_dis.shape[0]: 
                            #             cnt_test=time_dis.shape[0]-1
                            #             dtime=1
                            #         else:
                            #             dtime=time_dis[cnt_test]-k
                            #     if up==0:
                                    
                            #         if dtime<abs(time_dis[cnt_test-1]-k):
                                    
                            #             time_indx_max.append(cnt_test)
                            #         else:
                            #             time_indx_max.append(cnt_test-1)
                            #         up=1
                            #     elif up==1:
                            #         if dtime<abs(time_dis[cnt_test-1]-k):
                                    
                            #             time_indx_min.append(cnt_test)
                            #         else:
                            #             time_indx_min.append(cnt_test-1)
                            #         up=0
                            
                            # if peaks_dwn[-1]>=disp.shape[0]:
                            #     peaks_dwn_t=peaks_dwn
                            #     peaks_dwn_t[-1]=disp.shape[0]-1
                            # else:
                            #     peaks_dwn_t=peaks_dwn
                            
                            time_indx_max=fatgigue_data[dis2+'_indx_max']
                            time_indx_min=fatgigue_data[dis2+'_indx_min']
                            
                            disp_max=disp[time_indx_max]
                            disp_min=disp[time_indx_min]
                            dif1=abs(disp[time_indx_min[:-1]]-disp[time_indx_max])
                            dif2=abs(disp[time_indx_min[1:]]-disp[time_indx_max])
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
                    
                    c_num=np.arange(1,len(fatgigue_data['Load_Diff'])+1)
                    fatgigue_data['Cycle_Number']=c_num
                    
                    
                    ###################################################################
                    ####################Load###########################################
                    ###################################################################
                    
                    
                    fatgigue_data['Load_Up_Peack']=fatgigue_data['Load_Tot'][fatgigue_data['peaks_up']]
                    fatgigue_data['Load_Low_Peack']=fatgigue_data['Load_Tot'][fatgigue_data['peaks_dwn']]
                    fatgigue_data['R_value']=(fatgigue_data['Load_Up_Peack']-fatgigue_data['Load_Diff'])/fatgigue_data['Load_Up_Peack']
                    
                    
                    ###################################################################
                    ##################Moment###########################################
                    ###################################################################
                    
                    fatgigue_data['Moment_Up_Peack']=fatgigue_data['Moment_Tot'][fatgigue_data['peaks_up']]
                    fatgigue_data['Moment_Low_Peack']=fatgigue_data['Moment_Tot'][fatgigue_data['peaks_dwn']]
                    fatgigue_data['MR_value']=(fatgigue_data['Moment_Up_Peack']-fatgigue_data['Moment_Diff'])/fatgigue_data['Moment_Up_Peack']
                    
                    
                    with open(f_name_s_f, 'wb') as handle:
                        pickle.dump(fatgigue_data, handle, protocol=pickle.HIGHEST_PROTOCOL)
                    
                    cnt=1
                    