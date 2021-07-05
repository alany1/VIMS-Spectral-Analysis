from libraries import *
from functions import *
from fitting import *
from util import *
import time

def parse_csv(path_to_csv):
    """
    Returns dictionary containing all data including fits derived from csv contents.
    
    Parameters:
    path_to_csv: path to file containing spectra information for each shape file

    Returns:
    data: dictionary containing pixel information for all pixels in csv.
    """

    data = []
    count = 0
    shape_name = path_to_csv.split("_")[0]

    with open(path_to_csv, 'r') as f:

        print(f"STARTING PICKLE ON {path_to_csv}")
        
        header = f.readline().replace('"','').strip().split(',')

        while True:
            t0 = time.time()
            try:
                entry = f.readline()
            except:
                break

            if entry == '':
                break

            #split at spectra
            entry = entry.replace('"','').split('{')
            description = entry[0][:-1].split(',')
            spectra = list(map(float,entry[1].split('}')[0].split(',')))

            entry_dict = {}
            
            for i, col in enumerate(header[:-2]):
                if col not in ['name', 'sequenceid', 'observationid', 'starttime']:
                    entry_dict[col] = float(description[i])
                else:
                    entry_dict[col] = description[i]

            entry_dict['spectrum'] = np.array(spectra)

            entry_dict['stefan_spectrum'] = entry_dict['spectrum']/F(np.radians(entry_dict['incidence']),np.radians(entry_dict['emission']),np.radians(entry_dict['phase']))

            
            
            entry_dict['stefan_fit'] = fit(entry_dict['stefan_spectrum'], False)

            
            entry_dict['regular_fit'] = fit(entry_dict['spectrum'], True)

            
            
            #data.append(entry_dict)

            cube_name = entry_dict['name'].split('.cub')[0]
            latitude = entry_dict['latitude']
            longitude = entry_dict['longitude']
            
            file = open(f"new_pixels/{shape_name}/{shape_name}_{cube_name}_{latitude}_{longitude}.pkl","wb")
            pickle.dump(entry_dict,file)
            file.close()

            
                 
            count+=1
            
            if count%100 == 0:
                print("Progress",count)
            total = time.time() - t0

            if count % 10 == 0:
                print(f"TOTAL TIME {total}")

            if total > 5:
                print(spectra)
    #return data

if __name__ == '__main__':
    parse_csv('belet_pixels.csv')
    parse_csv('senkyo_pixels.csv')
    parse_csv('shangrai_pixels.csv')

    
            
        
