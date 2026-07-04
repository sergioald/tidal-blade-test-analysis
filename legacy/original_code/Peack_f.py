# -*- coding: utf-8 -*-
"""
Created on Thu Aug 11 09:38:06 2022

@author: slopezd
"""

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


pathf="C:\path\to\test_data\Test Data\\LTD_22A01_FA_0013\\LTD_22A01_FA_0013_2022-08-03-14-27-24.tdms"

next_file = TdmsFile(pathf)

tot_load=next_file['Log']['Load_A_01'][:]*-1

sigma_est = estimate_sigma(tot_load, average_sigmas=True)
tot_load_f=denoise_wavelet(tot_load, method='VisuShrink', mode='soft',  
                       wavelet='sym9', 
                       sigma=sigma_est/2,
                       rescale_sigma='True')

peaks, properties = find_peaks(tot_load_f, prominence=(70))
peaks2, properties2 = find_peaks(tot_load_f*-1, prominence=(70))


# plt.plot(tot_load)
plt.plot(tot_load_f)
plt.plot(peaks, tot_load_f[peaks], "x")
plt.plot(peaks2, tot_load_f[peaks2], "x")
plt.show()