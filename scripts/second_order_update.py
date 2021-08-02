from create_pickle import *
from fitting import *
from fitting_routine import *
from functions import *
from libraries import *
from util import *


def update_pickles_second_order(path_to_pickles):
    """
    Updates pickles to include info about second order stefan correction and bump.
    """
    wings = {'2.0': (65,76),
            '1.2': (15, 27), #changed this for better results
            '1.6': (37, 47),
            '1.0': (9, 16)}
    
    k = {'2.0': 1.29,
        '1.2': 1.50,
        '1.6': 1.6,
        '1.0': 1.15}
    
    count = 0
    shape_name = path_to_pickles[0].split('/')[1]

    print(f"STARTING {shape_name}")
    
    for i,file in enumerate(path_to_pickles):
        with open(file, 'rb') as f:
            entry = pickle.load(f)
            
        x = entry
        spec = entry['stefan_spectrum']
        new = np.array(spec)

        for channel in wings:
            adjust = k[channel]*(new[wings[channel][0]] + new[wings[channel][1]])/2
            new[wings[channel][0]:wings[channel][1]] -= adjust
        
        temp = fit(new, False, {'1.2': (15,27), '1.6': (37,47), '2.0': (65,76), '1.0': (9,16)})
        
        x['second-stefan_spectrum'] = new
        x['stefan-second_fit'] = temp
        
        x['bump_info'] = examine_bump(entry['spectrum'])

        
        write = open(file,"wb")
        pickle.dump(x, write)
        write.close()

        if i % 100 == 0:
            print(f"Progress {i}")
        

if __name__ == '__main__':
    update_pickles_second_order(belet)
    update_pickles_second_order(senkyo)
    update_pickles_second_order(shangrai)
