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

reasonable_output = {'1.0': {'gaussian': {'mean': (0.9,1.1)}, 'skew': {'peak_channel': (0.9, 1.1)}},
                         '1.2': {'gaussian': {'mean': (1.1, 1.3)}, 'skew': {'peak_channel': (1.1, 1.3)}},
                         '1.6': {'gaussian': {'mean': (1.5, 1.8)}, 'skew': {'peak_channel': (1.5, 1.8)}},
                          '2.0': {'gaussian': {'mean': (1.9, 2.2)}, 'skew': {'peak_channel': (1.9, 2.2)}}}

_params = {'stefan_fit': reasonable_output, 'regular_fit': reasonable_output, 'stefan-plaw_fit': reasonable_output}
# _params = {'stefan_fit': {'1.0': {'gaussian': {'mean': (0.9,1.1)}, 'skew': {'peak_channel': (0.9, 1.1)}},
#                          '1.2': {'gaussian': {'mean': (1.1, 1.3)}, 'skew': {'peak_channel': (1.1, 1.3)}},
#                          '1.6': {'gaussian': {'mean': (1.5, 1.8)}, 'skew': {'peak_channel': (1.5, 1.8)}},
#                           '2.0': {'gaussian': {'mean': (1.9, 2.2)}, 'skew': {'peak_channel': (1.9, 2.2)}}},
#           'regular_fit': {'1.0': {'gaussian': {'mean': (0.9,1.1)}, 'skew': {'peak_channel': (0.9, 1.1)}},
#                          '1.2': {'gaussian': {'mean': (1.1, 1.3)}, 'skew': {'peak_channel': (1.1, 1.3)}},
#                          '1.6': {'gaussian': {'mean': (1.5, 1.8)}, 'skew': {'peak_channel': (1.5, 1.8)}},
#                          '2.0': {'gaussian': {'mean': (1.9, 2.2)}, 'skew': {'peak_channel': (1.9, 2.2)}}}}

def filter_data(data, params = _params, spectra_bounds = (-0.1, 1)):
    filtered = []
    sample = False
    for i, entry in enumerate(data):

        if not entry['stefan_fit'] or not entry[ 'regular_fit'] or not entry['stefan-plaw_fit']:
            continue

        violate = False

        if np.max(entry['spectrum']) > spectra_bounds[1] or np.min(entry['spectrum']) < spectra_bounds[0]:
            continue
        
        for fit_type in params:
            for channel in params[fit_type]:
                for fn in params[fit_type][channel]:
                    for criteria in params[fit_type][channel][fn]:
                        low, high = params[fit_type][channel][fn][criteria]
                        if not low < entry[fit_type][channel][fn][criteria] < high:
                            violate = True

        if violate:
            if not sample:
                print(entry, i)
                sample = True
            continue

        filtered.append(entry)

    print(f"Total {len(data) - len(filtered)} entries removed")
    
    return filtered

def time_bucket(data, num_buckets = 20):
    """
    Data: list of spectra dictionaries
    
    Returns: Returns num_buckets lists containing spectra from each time bucket.
    """
    #REASONABLE_AMPLITUDES = (0,0.1)
    
    min_time, max_time = min(data, key = lambda x: x['ettime'])['ettime'],max(data, key = lambda x: x['ettime'])['ettime']
    
    bucket_length = (max_time - min_time) / num_buckets
    
    low = min_time
    up = max_time
    
    buckets = {}
    
    
    for i in range(num_buckets):
        up = bucket_length+low
        buckets[(low,up)] = []
        low = up
    
    
    for i,spec in enumerate(data):
        #if i%10000 == 0: print('Progress', i+1)
        for low,high in buckets:
            #insert cuts here if needed
            if spec['ettime'] <= high and spec['ettime'] >= low:
                buckets[(low,high)].append(spec)
                break
                
    return buckets

def viewing_geometry(data, incidence_range = (-float('inf'), float(inf)), emission_range=(-float('inf'), float('inf')), phase_range= (-float('inf'), float(inf))):
    return list(filter(lambda e: incidence_range[0] < e['incidence'] < incidence_range[1] and
                       emission_range[0] < e['emission'] < emission_range[1] and
                       phase_range[0] < e['phase'] < phase_range[1], data))
