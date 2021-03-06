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

belet = glob.glob("new_pixels/belet/*.pkl")
senkyo = glob.glob("new_pixels/senkyo/*.pkl")
shangrai = glob.glob("new_pixels/shangrai/*.pkl")
data = import_pickle(belet,senkyo,shangrai)

fit_windows = {'1.2':(15,28), '1.6':(32,55),'2.0':(60,85),'1.0':(7,18)}

def examine_bump(spectra, START_0 = 70, START_f = 72, END_0 = 77, END_f = 79): 

    if np.max(spectra) < .0001:
        return {}

    bump_info = {}

    p = np.polyfit(np.append(vims_wave[START_0:START_f], vims_wave[END_0: END_f]),
                   np.append(spectra[START_0:START_f], spectra[END_0: END_f]), 1)

    fit = np.polyval(p, vims_wave[START_0:END_f])

    bump = spectra[START_0:END_f] - fit

    bump_info['bump'] = bump
    bump_info['bump_max'] = np.max(bump)
    bump_info['polyfit'] = p
    bump_info['bump_max_channel'] = np.argmax(bump) + START_0

    
    return bump_info

    
def fit(spectra, use_powerlaw, fit_windows = fit_windows):
    """
    Parameters:
        spectra [list]: list of spectra values
        use_powerlaw [boolean]: True if using powerlaw adjustment, False otherwise 

    Returns: Parameters of fitting routine as a dictionary of dictionaries.
    """

    if np.max(spectra) < .0001:
        return {}
    
    band_channels = [29,30,31,32,47,48,49,50,51,52,53,54,55,84,85,86,87,88,89,90]
    
        
    initial = {'1.2': {'gaussian': (1.2,.1,.1), 'skew': (.01,1.2,.1,-1)},\
               '1.6': {'gaussian': (1.6,.1,.1), 'skew': (.01,1.6,.1,-1)},\
               '1.0': {'gaussian': (1.0,.1,.1), 'skew': (.01,1.0,.1,-1)},\
               '2.0': {'gaussian': (2.0,.1,.1), 'skew': (.01,2.0,.1,-1)}}

    result = {window: {} for window in fit_windows}

    if use_powerlaw:
        try:
            p_fit, cov = sco.curve_fit(powerlaw_no_constant, vims_wave[band_channels], spectra[band_channels], p0 = (1, -2), maxfev = 7500)
            p = powerlaw_no_constant(vims_wave, *p_fit)
            spectra = spectra - p
            result['powerlaw'] = {'scale': p_fit[0], 'exponent': p_fit[1]}

        except:
            pass
        
        
    for window in fit_windows:
        lower, upper = fit_windows[window]

        try:
            gaussian_fit, cov = sco.curve_fit(gaussian, vims_wave[lower:upper], spectra[lower:upper], p0 = initial[window]['gaussian'], maxfev = 7500)

            skew_fit, cov = sco.curve_fit(skew, vims_wave[lower:upper], spectra[lower:upper], p0 = initial[window]['skew'], maxfev = 7500)

            result[window]['gaussian'] = {'mean': gaussian_fit[0], 'sigma': gaussian_fit[1], 'amp': gaussian_fit[2]}
            result[window]['skew'] = {'A': skew_fit[0], 'e': skew_fit[1], 'w': skew_fit[2], 'a': skew_fit[3]}

            
            skew_list = skew(vims_wave[lower:upper], *skew_fit)
            ind = np.argmax(skew_list)
            extended_domain = np.linspace(vims_wave[lower], vims_wave[upper], 10000)
            skew_list_extended = skew(extended_domain, *skew_fit)
            
            result[window]['skew']['peak_channel'] = vims_wave[lower + ind]
            result[window]['skew']['peak_value'] = skew_list[ind]
            result[window]['skew']['peak_channel_inferred'] = extended_domain[np.argmax(skew_list_extended)]
            result[window]['skew']['peak_value_inferred'] = skew(result[window]['skew']['peak_channel_inferred'], *skew_fit)
                
            ind = np.argmax(spectra[lower:upper])
            result[window]['raw_peak_channel'] = vims_wave[lower + ind]
            result[window]['raw_peak_value'] = spectra[lower:upper][ind]                                                               

        except:
            return {}
    return result
