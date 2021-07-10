from IPython.core.display import HTML
import numpy as np
import matplotlib
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from pylab import *
import pysis
import os
import scipy.optimize as sco
import time
import ast
from tkinter import *



def gaussian(x,mean,sigma,A):
    
    return A*np.exp( -((x-mean)**2.) / (2.*sigma**2.) )

def powerlaw(x,a, k, c):
    
    return a*x**k + c


def create_gaussian_array(cube,nav,x,y):
    """
    Given cube data (cube) and navigation information (nav), adjusts data by subtracting fitted powerlaw and returns x by y arrays of:
    
    1) Gaussian means
    2) Gaussian widths
    3) Gaussian amplitudes
    
    4) Powerlaw amplitudes
    5) Powerlaw exponent
    6) Powerlaw constant
    
    """
    
    band_channels = [29,30,31,32,47,48,49,50,51,52,53,54,55,84,85,86,87,88,89,90] + [i for i in range(160,181)] 
    
    max_mean = 0
    max_sigma=0
    max_amp = 0
    means = np.zeros((x,y))
    sigmas = np.zeros((x,y))
    amps = np.zeros((x,y))
    plaw = np.zeros((x,y))
    plaw2 = np.zeros((x,y))
    plaw3 = np.zeros((x,y))
    
    for i in range(x):
        for j in range(y):
            #incidence and emission < 70
            if nav[6,i,j] < -90:# and nav[2,i,j]<70 and nav[3,i,j]<70:
                continue
            else:
                try:
                    #Fit power law
                    p_fit, p_cov = sco.curve_fit(powerlaw, vims_wave[band_channels], cube[band_channels, i,j], p0 = (.005,-2,0), maxfev = 10000)
                    p = powerlaw(vims_wave, *p_fit)
                    
                    #Subtract power law
                    new_data = cube[:,i,j] - p

                    #Fit gaussian
                    fit,cov = sco.curve_fit(gaussian, vims_wave[64:85],new_data[64:85], \
                                        p0=(2.08,.125,.1), maxfev=100000)

                    plaw[i,j] = p_fit[0]
                    plaw2[i,j] = p_fit[1]
                    plaw3[i,j] = p_fit[2]
                    
                except:
                    #If powerlaw fit fails, directly fit gaussian
                    fit,cov = sco.curve_fit(gaussian, vims_wave[64:85],cube[64:85,i,j], p0=(2.08,.125,.1), maxfev=10000)
                    
                    
                means[i,j] = fit[0]
                if fit[0]>max_mean:
                    max_mean = fit[0]
                sigmas[i,j] = fit[1] 
                if fit[1]>max_sigma:
                    max_sigma = fit[1]
                amps[i,j] = fit[2]
                if fit[2] > max_amp:
                    max_amp = fit[2]
    
    return (means,sigmas,amps,plaw,plaw2,plaw3,max_mean,max_sigma,max_amp)

def create_panels(data, nav,x,y,cb=[(0,.2),(0,.2),(2.02,2.04),(27,30),(0,80),(0,100),(0,0.1),(-3,-2)]):  
    """
    Given cube data and navigation information, creates 9 panels summarizing variation of different variables. Cb is a list of tuples representing 
    min and max values of the colorbar for each variable.
    
    1) Gaussian Amplitudes
    2) Gaussian Width
    3) Gaussian Mean
    
    4) Navigation Phase
    5) Navigation Emission
    6) Navigation Incidence
    
    7) Powerlaw Amplitude
    8) Powerlaw Exponent
    
    9) Channel 69 
    """
    t0=time.time()
    array = create_gaussian_array(data,nav,x,y)
    #print(array[6])
    #print(array[7])
    #print(array[8])
    print(array[2])
    print(np.min(array[2]))
#     print(np.max(array[1]))
#     print(np.max(array[0]))
#     print(np.max(array[2]))
    print(f'Time: {time.time()-t0}')
    A = array[2]
    W = array[1]
    M = array[0]
    plaw_amp = array[3]
    plaw_power = array[4]
    plaw_constant = array[5]
    #Subplots
    f = plt.figure(figsize=(10,3))
    ax = f.add_subplot(331)
    ax2 = f.add_subplot(332)
    ax3 = f.add_subplot(333)
    ax4 = f.add_subplot(334)
    ax5 = f.add_subplot(335)
    ax6 = f.add_subplot(336)
    ax7 = f.add_subplot(337)
    ax8 = f.add_subplot(338)
    ax9 = f.add_subplot(339)

    #GAUSSIAN
    ax.title.set_text("Gaussian - Amplitudes")
    amps = ax.imshow(A,vmin=cb[0][0],vmax=cb[0][1])
    plt.colorbar(amps,ax=ax)

    ax2.title.set_text("Gaussian - Width")
    width = ax2.imshow(W, vmin = cb[1][0], vmax=cb[1][1])
    plt.colorbar(width,ax=ax2)

    ax3.title.set_text("Gaussian - Mean")
    mean = ax3.imshow(M, vmin=cb[2][0],vmax=cb[2][1])
    plt.colorbar(mean,ax=ax3)

    #NAVIGATION
    ax4.title.set_text("Navigation - Latitude")
    phase = ax4.imshow(nav[6,:,:], vmin=cb[3][0],vmax=cb[3][1])
    plt.colorbar(phase, ax=ax4)

    ax5.title.set_text("Navigation - Longitude")
    emission = ax5.imshow(nav[7,:,:], vmin=cb[4][0], vmax=cb[4][1])
    plt.colorbar(emission,ax = ax5)

    ax6.title.set_text("Navigation - Resolution")
    incidence = ax6.imshow(nav[8,:,:], vmin = cb[5][0], vmax=cb[5][1])
    plt.colorbar(incidence,ax=ax6)

    ax7.title.set_text("Powerlaw - Amplitude")
    plaw = ax7.imshow(plaw_amp, vmin = cb[6][0], vmax=cb[6][1])
    plt.colorbar(plaw,ax=ax7)

    ax8.title.set_text("Powerlaw - Exponent")
    plaw2 = ax8.imshow(plaw_power, vmin=cb[7][0],vmax=cb[7][1])
    plt.colorbar(plaw2,ax=ax8)

    ax9.title.set_text("Channel 69")
    channel = ax9.imshow(data[69,:,:])
    plt.colorbar(channel,ax=ax9)
    
    return array
