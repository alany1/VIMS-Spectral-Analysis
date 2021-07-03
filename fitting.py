from functions import *

def import_pickle(*file_lists):
    count = 0
    data = []
    for file_list in file_lists:
        for i,file in enumerate(file_list):
            with open(file,"rb") as f:
                data.append(pickle.load(f))
                count+=1
            if count%50000==0:
                print(f"Current progress: {count}")
    print("DONE")
    return data

data = import_pickle(belet,senkyo,shangrai)

def fit(info):
    """
    info: spectrum list.
    
    Returns: Parameters of fitting routine as a dictionary of dictionaries.
    """
    band_channels = [29,30,31,32,47,48,49,50,51,52,53,54,55,84,85,86,87,88,89,90]# + [i for i in range(160,181)] 
    plaw = False
    
    fits = {'1.0':{},'1.2':{},'1.6':{},'2.0':{}}
    
    #attempt to fit powerlaw:
    try:
        p_fit,p_cov = sco.curve_fit(powerlaw,vims_wave[band_channels],info[band_channels],p0=(0.005,-2,0),maxfev=100000)
        p=powerlaw(vims_wave,*p_fit)
        adjusted = info-p
        plaw=True
    except:
        adjusted = info
    
    #2.0:
    try:
        fit,cov=sco.curve_fit(gaussian,vims_wave[60:85],adjusted[60:85],p0=(2.0,.125,.1),maxfev=100000)
        if plaw:
            fits['2.0']={'p_amp': p_fit[0],'p_power': p_fit[1],'p_const': p_fit[2],'g_mean':fit[0],'g_sigma': fit[1],'g_amp':fit[2]} 
        else:
            fits['2.0']={'g_mean':fit[0],'g_sigma': fit[1],'g_amp':fit[2]} 
    except:
        return {}
    
    #1.6:
    try:
        fit,cov=sco.curve_fit(gaussian,vims_wave[35:54],adjusted[35:54],p0=(1.6,.125,.1),maxfev=100000)
        if plaw:
            fits['1.6'] = {'p_amp': p_fit[0],'p_power': p_fit[1],'p_const': p_fit[2],'g_mean':fit[0],'g_sigma': fit[1],'g_amp':fit[2]}
        else:
            fits['1.6']={'g_mean':fit[0],'g_sigma': fit[1],'g_amp':fit[2]} 
    except:
        return {}
    
    #1.2:
    try:
        fit,cov=sco.curve_fit(gaussian,vims_wave[12:30],adjusted[12:30],p0=(1.2,.125,.1),maxfev=100000)
        if plaw:
            fits['1.2'] = {'p_amp': p_fit[0],'p_power': p_fit[1],'p_const': p_fit[2],'g_mean':fit[0],'g_sigma': fit[1],'g_amp':fit[2]}
        else:
            fits['1.2']={'g_mean':fit[0],'g_sigma': fit[1],'g_amp':fit[2]} 
    except:
        return {}
    
    try:
        fit,cov=sco.curve_fit(gaussian,vims_wave[:18],adjusted[:18],p0=(1.0,.125,.1),maxfev=100000)
        if plaw:
            fits['1.0'] = {'p_amp': p_fit[0],'p_power': p_fit[1],'p_const': p_fit[2],'g_mean':fit[0],'g_sigma': fit[1],'g_amp':fit[2]}
        else:
            fits['1.0']={'g_mean':fit[0],'g_sigma': fit[1],'g_amp':fit[2]} 
    except:
        return {}
    
    fits['2.0']['channel']=info[69]
    fits['1.0']['channel']=info[8]
    fits['1.2']['channel']=info[20]
    fits['1.6']['channel']=info[45]
    
    return fits
