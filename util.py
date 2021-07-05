from libraries import *
from functions import *
from fitting import data

def fit_test(i, data, function, initial_guesses, window = '2.0'):
   
    if np.max(data[i]['spectrum']) < .01:
        print("Noise")
        plt.plot(vims_wave, data[i]['spectrum'])
        return None
    
    fit_windows = {'1.2':(15,28), '1.6':(32,55),'2.0':(60,85),'1.0':(7,18)}
    initial = {'1.2': {'gaussian': (1.2,.1,.1), 'function': initial_guesses['1.2']},\
               '1.6': {'gaussian': (1.6,.1,.1), 'function': initial_guesses['1.6']},\
               '1.0': {'gaussian': (1.0,.1,.1), 'function': initial_guesses['1.0']},\
               '2.0': {'gaussian': (2.0,.1,.1), 'function': initial_guesses['2.0']}}
    
    lower,upper = fit_windows[window]
    
    max_channel = vims_wave[lower+np.argmax(data[i]['spectrum'][lower:upper])]
    
    print(f"Max channel: {max_channel}")

    band_channels = [29,30,31,32,47,48,49,50,51,52,53,54,55,84,85,86,87,88,89,90]# + [i for i in range(160,181)] 
    
    p_fit,p_cov = sco.curve_fit(powerlaw_no_constant,vims_wave[band_channels],data[i]['spectrum'][band_channels],p0=(1,-2),maxfev=100000)
    p=powerlaw_no_constant(vims_wave,*p_fit)
    adjusted = data[i]['spectrum']-p
    plt.plot(vims_wave, adjusted, label="Powerlaw Adjustment")
    plt.plot(vims_wave,data[i]['spectrum'])
    plt.plot(vims_wave, p)
    
    f_fit,cov = sco.curve_fit(function,vims_wave[lower:upper],data[i]['spectrum'][lower:upper],p0 = initial[window]['function'],maxfev=100000)
    plt.plot(vims_wave, function(vims_wave,*f_fit), label = "Function")
    
    fp_fit,cov = sco.curve_fit(function,vims_wave[lower:upper],adjusted[lower:upper],p0 = initial[window]['function'],maxfev=100000)
    plt.plot(vims_wave, function(vims_wave,*fp_fit), label = "Powerlaw Function")
    
    g_fit,cov=sco.curve_fit(gaussian,vims_wave[lower:upper],data[i]['spectrum'][lower:upper],p0=initial[window]['gaussian'],maxfev=100000)
    plt.plot(vims_wave, gaussian(vims_wave, *g_fit), label = "Gaussian")
    
    gp_fit,cov=sco.curve_fit(gaussian,vims_wave[lower:upper],adjusted[lower:upper],p0=initial[window]['gaussian'],maxfev=100000)
    plt.plot(vims_wave, gaussian(vims_wave, *gp_fit), label = "Powerlaw Gaussian")
    
    plt.legend()
    print(f"Powerlaw: {p_fit} \n Gaussian: {g_fit} \n Powerlaw Gaussian: {gp_fit} \n Function: {f_fit} \n Powerlaw Function {fp_fit}")

