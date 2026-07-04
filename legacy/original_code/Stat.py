# -*- coding: utf-8 -*-
"""
Created on Mon Aug 22 10:59:48 2022

@author: slopezd
"""

import matplotlib.pyplot as plt

dist_up=[900,1700,2500,3300,4100]
mean_up_1=[-0.000587319,-0.002139124,-0.002324416,-0.001352566,-4.90E-05]
min_up_1=[-0.000599665,-0.002190148,-0.002379545,-0.001437823,-0.000146379]
max_up_1=[-0.000576645,-0.00208614,-0.002274666,-0.001243495,4.80E-05]


dist_dwn=[900,1700,2500,4100]

means_dwn_1=[0.000580311,0.002330685,0.002662485,2.58E-05]
min_dwn_1=[0.000558415,0.002278871,0.002575644,-3.78E-05]
max_dwn_1=[0.000598415,0.00236604,0.002740027,9.63E-05]


plt.figure()
plt.plot(dist_up,min_up_1, 'o:k', label='First Test Minimum Values')
plt.plot(dist_up,mean_up_1, marker = 'o', label='First Test Mean Values')
plt.plot(dist_up,max_up_1, 'o:r', label='First Test Maximum Values')

plt.plot(dist_dwn,min_dwn_1, 'o:r', label='First Test Minimum Values')
plt.plot(dist_dwn,means_dwn_1, marker = 'o', label='First Test Mean Values')
plt.plot(dist_dwn,max_dwn_1, 'o:k', label='First Test Maximum Values')
# plt.gca().invert_xaxis()

plt.legend()
plt.title("Strain Gages Static test")
plt.xlabel("Distance from root [mm]")
plt.ylabel("Strain [$\epsilon$]")


dist_up=[900,1700,2500,3300,4100]
mean_up_2=[-0.000642559,-0.002096629,-0.002234834,-0.001064238,7.55E-06]
min_up_2=[-0.000673304,-0.002180606,-0.002329061,-0.00114075,-8.60E-05]
max_up_2=[-0.000613663,-0.002018295,-0.002152845,-0.001002138,8.57E-05]


dist_dwn=[900,1700,2500,4100]

means_dwn_2=[0.00057792,0.002305851,0.002546023,-6.21E-06]
min_dwn_2=[0.000556466,0.002223175,0.00245178,-7.98E-05]
max_dwn_2=[0.00059787,0.002390888,0.002651201,7.81E-05]


plt.figure()

# plt.plot(dist_up,min_up_1, 'o:k', label='First Test Minimum Values')
plt.plot(dist_up,mean_up_1, marker = 'o', label='First Test Mean Values')
# plt.plot(dist_up,max_up_1, 'o:r', label='First Test Maximum Values')
# plt.plot(dist_up,min_up_2, 'o:b', label='Second Test Minimum Values')
plt.plot(dist_up,mean_up_2, marker = 'o', label='Second Test Mean Values')
# plt.plot(dist_up,max_up_2, 'o:g', label='Second Test Maximum Values')

# plt.plot(dist_dwn,min_dwn_1, 'o:r', label='First Test Minimum Values')
plt.plot(dist_dwn,means_dwn_1, marker = 'o', label='First Test Mean Values')
# plt.plot(dist_dwn,max_dwn_1, 'o:k', label='First Test Maximum Values')
# plt.plot(dist_dwn,min_dwn_2, 'o:b', label='Second Test Minimum Values')
plt.plot(dist_dwn,means_dwn_2, marker = 'o', label='Second Test Mean Values')
# plt.plot(dist_dwn,max_dwn_2, 'o:g', label='Second Test Maximum Values')
# plt.gca().invert_xaxis()

plt.legend()
plt.title("Strain Gages Static test")
plt.xlabel("Distance from root [mm]")
plt.ylabel("Strain [$\epsilon$]")


plt.figure()
plt.plot(dist_up,min_up_2, 'o:k', label='Second Test Minimum Values')
plt.plot(dist_up,mean_up_2, marker = 'o', label='Second Test Mean Values')
plt.plot(dist_up,max_up_2, 'o:r', label='Second Test Maximum Values')

plt.plot(dist_dwn,min_dwn_2, 'o:r', label='Second Test Minimum Values')
plt.plot(dist_dwn,means_dwn_2, marker = 'o', label='Second Test Mean Values')
plt.plot(dist_dwn,max_dwn_2, 'o:k', label='Second Test Maximum Values')
# plt.gca().invert_xaxis()

plt.legend()
plt.title("Strain Gages Static test")
plt.xlabel("Distance from root [mm]")
plt.ylabel("Strain [$\epsilon$]")