#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script for intercomparison of optical properties between models and 
"""
import os
import pyaerocom as pya
import logging
import numpy as np
from collections import OrderedDict as od

def var_list(networks):
    VARS = []
    for k, v in networks.items():
        if isinstance(v, str):
            VARS.append(v)
        else:
            VARS.extend(v)
    return list(dict.fromkeys(VARS))


def station_data_to_old_ascii(out_dir, station_data, var):
    print(out_dir)
    if not os.path.exists(out_dir):
        raise IOError('output directory does not exist')
    s = station_data
    name = s['station_name'].replace('_','').replace('-','')
    name = ''.join(name.split('-'))
    save_name = '{}_{}_{}.txt'.format(var, TS_TYPE, name)
    print(save_name)
    
    FILE = os.path.join(out_dir, save_name)
    HEAD_LINE = 'datestring\tyear\tmonth\tday\thour\tminute\tsecond\tvalue\n'
    
    data = s[var]
    times, vals = data.index, data.values
    with open(FILE, 'w') as f:
        f.write('      12\n')
        f.write('latitude:      {:.4f}\n'.format(s.latitude))
        f.write('longitude:      {:.4f}\n'.format(s.longitude))
        f.write('altitude:      {:.4f}\n'.format(s.longitude))
        f.write('station name:{}\n'.format(name))
        f.write('\n\n\n\n\n')
        f.write(HEAD_LINE)
        for i, t in enumerate(times):
            val = vals[i]
            if np.isnan(val):
                val = 'NaN'
                
            f.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(t,
                                                              t.year,
                                                              t.month, 
                                                              t.day,
                                                              t.hour, 
                                                              t.minute, 
                                                              t.second,
                                                              val))


MODEL_LIST = ['ECMWF_CAMS_REAN']

# Obs data and variables
OBS_NETWORKS = {'AeronetSunV2Lev2.daily' : ['od550aer',
                                            'ang4487aer']}
# =============================================================================
#                           'AeronetSunV3Lev2.daily' : ['od550aer',
#                                                       'ang4487aer']}
# =============================================================================
               #'EBASMC'] # ec550aer, ...
               
OUT_DIR = './output/'

OUT_DIRS_RESULTS = od()

OUT_BASE = '/lustre/storeA/project/aerocom/aerocom1/AEROCOM_OBSDATA/Export/'

OLD_DATA_DIR = OUT_BASE + 'AeronetSun2.0.bak/'
EXAMPLE_FILE = 'od550aer_daily_MunichUniversity.txt'

OUT_BASE = OUT_DIR
OUT_DIRS_RESULTS['AeronetSunV2Lev2.daily'] = OUT_BASE + 'Jonas/AERONETSunV2/'
OUT_DIRS_RESULTS['AeronetSunV3Lev2.daily'] = OUT_BASE + 'Jonas/AERONETSunV3/'
OUT_DIRS_RESULTS['ECMWF_CAMS_REAN'] = od()
OUT_DIRS_RESULTS['ECMWF_CAMS_REAN']['AeronetSunV2Lev2.daily'] = OUT_BASE + 'AERONETSunV2-ECMWF2018/'
OUT_DIRS_RESULTS['ECMWF_CAMS_REAN']['AeronetSunV3Lev2.daily'] = OUT_BASE + 'AERONETSunV3-ECMWF2018/'

for k, v in OUT_DIRS_RESULTS.items():
    if isinstance(v, str) and not os.path.exists(v):
        os.mkdir(v)
    elif isinstance(v, dict):
        for key, val in v.items():
            if isinstance(val, str) and not os.path.exists(val):
                os.mkdir(val)



INCLUDE_MODELS = False
EVAL = 1

TS_TYPE='daily'
PD_FREQ = pya.helpers.TS_TYPE_TO_PANDAS_FREQ[TS_TYPE]
START='1990'
STOP='2020'
if __name__ == "__main__":
    pya.change_verbosity('critical')
    VARS = var_list(OBS_NETWORKS)

    read_obs = pya.io.ReadUngridded()
    read_obs.logger.setLevel(logging.INFO)
    
    print('Reading obs data')
    # Load networks individually for now (easier for analysis below)
    obs_all = od()
    
    with open(os.path.join(OLD_DATA_DIR, EXAMPLE_FILE), 'r') as f:
        lines = f.readlines()
    
    if EVAL:
        for network, vars_to_retrieve in OBS_NETWORKS.items():
                obs_all[network] = read_obs.read_dataset(
                        network, vars_to_retrieve=vars_to_retrieve)
        
        data = obs_all['AeronetSunV2Lev2.daily']
        
        
        stat_data = data.to_station_data_all(vars_to_convert=VARS,
                                             start=START, 
                                             stop=STOP, 
                                             freq=PD_FREQ)
        
        for data in stat_data:
            if data is not None:
                for var in VARS:
                    station_data_to_old_ascii(OUT_DIRS_RESULTS['AeronetSunV2Lev2.daily'], 
                                              data, var)
        #test_file = os.path.join()
        if INCLUDE_MODELS:
            model_reader = pya.io.ReadGriddedMulti(MODEL_LIST)
            model_reader.read(VARS)
        
        
                                    
                                
                                
                                    
                               