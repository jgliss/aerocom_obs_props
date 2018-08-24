#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script for intercomparison of optical properties between models and 
"""
import os
import pyaerocom as pya
import logging
import numpy as np
import shutil
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
    name = s['station_name'].replace('_','').replace('-','').replace(' ','')
    name = ''.join(name.split('-'))
    save_name = '{}_{}_{}.txt'.format(var, TS_TYPE, name)
    print(save_name)
    
    FILE = os.path.join(out_dir, save_name)
    HEAD_LINE = 'datestring\tyear\tmonth\tday\thour\tminute\tsecond\tvalue\n'
    
    data = s[var]
    if not len(data) == 1:
        times, vals = data.index, data.values
        with open(FILE, 'w') as f:
            f.write('      12\n')
            f.write('latitude:      {:.4f}\n'.format(s.latitude))
            f.write('longitude:      {:.4f}\n'.format(s.longitude))
            f.write('altitude:      {:.4f}\n'.format(s.altitude))
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


def _prep_dir(DIR):
    if RECOMPUTE_EXISTING and os.path.exists(DIR):
        print('Deleting existing directory and all its contents')
        shutil.rmtree(DIR)
    if not os.path.exists(DIR):
        os.mkdir(DIR)
    if len(os.listdir(DIR)) > 0:
        return True
    return False

def init_output_dirs():
    ignore_eval = []
    for model_or_obs, val in OUT_DIRS_RESULTS.items():
        if isinstance(val, str):
            if _prep_dir(val): #RECOMPUTE_EXISTING is False and there were already files in folder, will be ignored
                ignore_eval.append(model_or_obs)

        elif isinstance(val, dict):
            for obs, DIR in val.items():
                if isinstance(DIR, str):
                    if not _prep_dir(DIR) and model_or_obs in ignore_eval:
                        raise IOError
    return ignore_eval
                    
MODEL_LIST = ['ECMWF_CAMS_REAN']

# Obs data and variables
OBS_NETWORKS = {'EBASMC'                 : ['absc550aer', # light absorption coefficient
                                            'absc550lt1aer',
                                            'scatc550aer',
                                            'scatc550lt1aer'],
                'AeronetSunV3Lev2.daily' : ['od550aer',
                                            'ang4487aer'],
                'AeronetSunV2Lev2.daily' : ['od550aer',
                                            'ang4487aer']} # ec550aer, ...
                
OUT_DIR = './output/'

OUT_DIRS_RESULTS = od()

OUT_BASE = '/lustre/storeA/project/aerocom/aerocom1/AEROCOM_OBSDATA/Export/'

### output dirs obs data
OUT_DIRS_RESULTS['AeronetSunV2Lev2.daily'] = OUT_BASE + 'Jonas/AERONETSunV2/'
OUT_DIRS_RESULTS['AeronetSunV3Lev2.daily'] = OUT_BASE + 'Jonas/AERONETSunV3/'
OUT_DIRS_RESULTS['EBASMC'] = OUT_BASE + 'Jonas/EBASMC/'

### output dirs collocated model data
OUT_DIRS_RESULTS['ECMWF_CAMS_REAN'] = od()
OUT_DIRS_RESULTS['ECMWF_CAMS_REAN']['AeronetSunV2Lev2.daily'] = OUT_BASE + 'Jonas/AERONETSunV2-ECMWF2018/'
OUT_DIRS_RESULTS['ECMWF_CAMS_REAN']['AeronetSunV3Lev2.daily'] = OUT_BASE + 'Jonas/AERONETSunV3-ECMWF2018/'
OUT_DIRS_RESULTS['ECMWF_CAMS_REAN']['EBASMC'] = OUT_BASE + 'Jonas/EBASMC-ECMWF2018/'

INCLUDE_MODELS = True
RECOMPUTE_EXISTING = True
EVAL = 1

TS_TYPE='daily'
PD_FREQ = pya.helpers.TS_TYPE_TO_PANDAS_FREQ[TS_TYPE]
START='1990'
STOP='2020'

if __name__ == "__main__":
    ignore = init_output_dirs()
   
    #pya.change_verbosity('critical')
    VARS = var_list(OBS_NETWORKS)

    read_obs = pya.io.ReadUngridded()
    read_obs.logger.setLevel(logging.INFO)
    
    print('Reading obs data')
    # Load networks individually for now (easier for analysis below)
    obs_all = od()
    
    if EVAL:
        for network, vars_to_retrieve in OBS_NETWORKS.items():
                obs_all[network] = read_obs.read_dataset(
                        network, vars_to_retrieve=vars_to_retrieve)
        
        if INCLUDE_MODELS:
            model_reader = pya.io.ReadGriddedMulti(MODEL_LIST)
            model_reader.read(VARS)
        
        for obs_id, obs_data in obs_all.items():
            stat_data = obs_data.to_station_data_all(vars_to_convert=VARS,
                                                     start=START, 
                                                     stop=STOP, 
                                                     freq=PD_FREQ)
            
            for data in stat_data:
                if data is not None:
                    for var in VARS:
                        if var in data:
                            station_data_to_old_ascii(OUT_DIRS_RESULTS[obs_id], 
                                                      data, var)
                            if INCLUDE_MODELS:
                                for model in MODEL_LIST:
                                    m = model_reader[model]
                                    if var in m.vars:
                                        model_data = model_reader[model].data[var]
                                        model_tseries = model_data.to_time_series_single_coord(latitude=data.latitude, 
                                                                                               longitude=data.longitude)
                                        d = pya.StationData(latitude=data.latitude, 
                                                            longitude=data.longitude,
                                                            altitude=data.altitude, 
                                                            station_name=data.station_name)
                                        
                                        d[var] = model_tseries[var]
                                        
                                        station_data_to_old_ascii(OUT_DIRS_RESULTS[model][obs_id], 
                                                                  d, var)
                                
                                
                                
                                        
        
        
                                    
                                
                                
                                    
                               