#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 24 14:48:03 2018

@author: jonasg
"""
import pyaerocom as pya

OBS_DIR = '/lustre/storeA/project/aerocom/aerocom-users-database/SATELLITE-DATA/CALIOP3/renamed/'


if __name__=='__main__':
    ### Model data
     
    import os, iris
    files = os.listdir(OBS_DIR)
    
    
    
    data4D = []
    data4D_filename_wrong = []
    lacks_dim = []
    lacks_time_dim = []
    lacks_longitude_dim = []
    lacks_latitude_dim = []
    time_wrong = []
    var_not_found = []
    filename_invalid = []
    
    all_dim_varnames = []
    more_than_one = []
    
    fconv = pya.io.FileConventionRead('aerocom2')
    for f in files:
        fp = OBS_DIR + f
        if not fp.endswith('.nc'):
            continue
        cubes = iris.load(fp)
        data = None
        try:
            info = fconv.get_info_from_file(f)
            var = info['var_name']
        except pya.exceptions.FileConventionError:
            filename_invalid.append(f)
        else:
        
            if len(cubes) > 1:
                more_than_one.append(f)
            var_found = False
            for cube in cubes:
                if cube.var_name == var:
                    data = cube
                    var_found = True
                    
            if not var_found:
                var_not_found.append(f)
            else:
                is4d = False
                if data.ndim == 4:
                    data4D.append(f)
                    is4d = True
                    if not '3d' in var.lower():
                        data4D_filename_wrong.append(f)
                dim_names = [x.name() for x in data.dim_coords]
                print(dim_names)
                if not len(dim_names) == data.ndim:
                    lacks_dim.append(f)
                if not 'time' in dim_names:
                    lacks_time_dim.append(f)
                elif not 'longitude' in dim_names:
                    lacks_longitude_dim.append(f)
                elif not 'latitude' in dim_names:
                    lacks_latitude_dim.append(f)
                if 'time' in dim_names:
                    if not pya.io.iris_io.check_time_coord(data, 
                                                           info['ts_type'],
                                                           info['year']):
                        time_wrong.append(f)
                        
                for name in dim_names:
                    if not name in all_dim_varnames:
                        all_dim_varnames.append(name)
                        
    totnum = len(files)
    with open('CALIOP3_read_test.csv', 'w+') as f:
        f.write('# Files that contain 4D data but not conclusive from filename ({} of {})\n'.format(len(data4D_filename_wrong), totnum))
        for file in data4D_filename_wrong:
            f.write(file + '\n')
        f.write('\n')
        
        f.write('# Files that miss time dimension ({} of {})\n'.format(len(lacks_time_dim), totnum))
        for file in lacks_time_dim:
            f.write(file + '\n')
        f.write('\n')
        
        f.write('# Files that include time dimension but time in data does not match filename info ({} of {})\n'.format(len(time_wrong), totnum))
        for file in time_wrong:
            f.write(file + '\n')
        f.write('\n')
        
        f.write('# Files that miss longitude dimension ({} of {})\n'.format(len(lacks_longitude_dim), totnum))
        for file in lacks_longitude_dim:
            f.write(file + '\n')
        f.write('\n')
            
        f.write('# Files that miss latitude dimension ({} of {})\n'.format(len(lacks_latitude_dim), totnum))
        for file in lacks_latitude_dim:
            f.write(file + '\n')
        f.write('\n')
        
        f.write('# Files that do not match aerocom file naming convention({} of {})\n'.format(len(filename_invalid), totnum))
        for file in filename_invalid:
            f.write(file + '\n')
        f.write('\n')
        
        f.write('# Files that miss at least one dimension definition ({} of {})\n'.format(len(lacks_dim), totnum))
        for file in lacks_dim:
            f.write(file + '\n')
        f.write('\n')        
        

    
    
    