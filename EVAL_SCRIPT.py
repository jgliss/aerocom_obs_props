#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script for intercomparison of optical properties between models and 
"""
import helpers as helpers
import os
from collections import OrderedDict as od

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pyaerocom as pya
import logging

### GLOBAL SETTINGS


YEARS = [2010, 2008, 9999]

MODEL_LIST = ['CAM6-Oslo_NF2kNucl_7jun2018AK',
              'OsloCTM2_INSITU',
              'TM5_AP3-CTRL2016',
              'TM5_AP3-INSITU']

GRIDDED_OBS_NETWORKS = ['MODIS6.terra', #od550aer
                        'MODIS6.aqua'] #od550aer
                        #'CALIOP3'] #od550aer

# will be filled during the import
READ_PROBLEMATIC = {}

# Obs data and variables
UNGRIDDED_OBS_NETWORKS = {'AeronetSunV2Lev2.daily' : 'od550aer',
                          'AeronetSunV3Lev2.daily' : 'od550aer',
                          'AeronetSDAV2Lev2.daily' : ['od550lt1aer', 
                                                      'od550gt1aer'],
                          'AeronetSDAV3Lev2.daily' : ['od550lt1aer', 
                                                      'od550gt1aer'],
                          pya.const.AERONET_INV_V2L2_DAILY_NAME : 'abs550aer',
                          pya.const.AERONET_INV_V3L2_DAILY_NAME : 'abs550aer'
                          }
               #'EBASMC'] # ec550aer, ...

### Paths and directories
MODEL_INFO_FILE = ('/lustre/storeA/project/aerocom/'
                   'aerocom-users-database/AEROCOM-PHASE-III/reference-list')

OUT_DIR = './output/'

OUT_DIR_SCAT = os.path.join(OUT_DIR, 'scatter_plots')

OUT_DIR_RESULTS = os.path.join(OUT_DIR, 'results_csv')

OUT_STATS = os.path.join(OUT_DIR, 'statistics_results.csv')


VARS = []
for k, v in UNGRIDDED_OBS_NETWORKS.items():
    if isinstance(v, str):
        VARS.append(v)
    else:
        VARS.extend(v)
VARS = list(dict.fromkeys(VARS))



def chk_make_dir(base, name):
    d = os.path.join(base, name)
    if not os.path.exists(d):
        os.mkdir(d)
    return d

def init_output_directories(model_reader, obs_data, out_base_dir):
    dirs = {}
    for name, data in model_reader.results.items():
        model_base = chk_make_dir(out_base_dir, name)
        dirs[name] = {}
        for y in data.years:
            year_sub = chk_make_dir(model_base, str(y))
            dirs[name][y] = {}
            for obs_network in obs_data:
                obs_sub = chk_make_dir(year_sub, obs_network)
                dirs[name][y][obs_network] = obs_sub
                chk_make_dir(obs_sub, 'series_plots')
    return dirs
    
def append_result(out_file, stats, model, obs, var, year, ts_type):
    with open(out_file, 'a') as f:
        f.write('Model: {}, Obs: {}, Var: {}, Year: {}, Freq: {}\n'.format(
                model, obs, var, year, ts_type))
        for k, v in stats.items():
            f.write('{}:\t{:.3f}\n'.format(k, v))
        f.write('\n')
                          

if __name__=="__main__":
    if os.path.exists(OUT_STATS):
        os.remove(OUT_STATS)
        
    plt.close('all')
    helpers.print_file(MODEL_INFO_FILE)
### OPTIONS 
    RELOAD = 1
    RUN_EVAL = 1
    EVAL_UNGRIDDED = 1
    EVAL_GRIDDED_OBS = 1
    TEST = 0
    PLOT_STATIONS = 0

    pya.change_verbosity('critical')
    
### DATA IMPORT        
    if RELOAD:
        print('Importing model and obs data, this could take some time')
        ### Read gridded model data
        read_models = pya.io.ReadGriddedMulti(MODEL_LIST)
        read_models.read_individual_years(VARS, YEARS)
        
        print('Reading satellite data')
        ### Read gridded obs data
        read_gridded_obs = pya.io.ReadGriddedMulti(GRIDDED_OBS_NETWORKS)
        read_gridded_obs.read_individual_years(VARS, YEARS)
        
        read_ungridded_obs = pya.io.ReadUngridded()
        read_ungridded_obs.logger.setLevel(logging.INFO)
        
        print('Reading ungridded obs data')
        # Load networks individually for now (easier for analysis below)
        ungridded_obs_all = od()
        if EVAL_UNGRIDDED:
            for network, vars_to_retrieve in UNGRIDDED_OBS_NETWORKS.items():
                ungridded_obs_all[network] = read_ungridded_obs.read_dataset(
                        network, vars_to_retrieve=vars_to_retrieve)
        
            dirs = init_output_directories(read_models, ungridded_obs_all, OUT_DIR)
        
    if RUN_EVAL:
### ANALYSIS           
        PLOT_STATIONS = 0
        # temporal resolution
        TS_TYPES = ['monthly']#, 'yearly']
        
        filter_name = 'WORLD-noMOUNTAINS'
        for ts_type in TS_TYPES:
            plotname = 'mALLYEAR{}'.format(ts_type)
            for model_id, model_reader in read_models.results.items():
                for year in YEARS:
                    if not year in model_reader.years:
                        continue
                    for var in VARS:
                        if not var in model_reader.vars:
                            continue
                        
                        if EVAL_GRIDDED_OBS:
                            for obs_id, obs_reader in read_gridded_obs.results.items():
                                if var in obs_reader.vars and year in obs_reader.years:
                                    if year == 9999:
                                        msg =('Ignoring climatology data (model: {}, '
                                              'obs: {}). '
                                              'Not yet implemented'.format(model_id,
                                                                           obs_id)) 
                                        print(msg)
                                        raise Exception
                                        with open(OUT_STATS, 'a') as f:
                                            f.write('\n{}\n\n'.format(msg))
                                        
                                        continue
                                    print('Analysing variable: {}\n'
                                          'Model {} vs. obs {}\n'
                                          'Year: {} ({} resolution)\n'
                                          .format(var, model_id, obs_id, 
                                                  year, ts_type))
                                    model = model_reader.data_yearly[var][year]
                                    obs = obs_reader.data_yearly[var][year]
                                    
                                    start_str = str(year) 
                                    stop_str = '{}-12-31 23:59:00'.format(year) 
                                    
                                    data = pya.collocation.collocate_gridded_gridded(
                                                             model, obs,
                                                             ts_type=ts_type,
                                                             filter_name=filter_name)
                                    
                                    stats = data.calc_statistics()
                                    append_result(OUT_STATS, stats, 
                                                  model_id, obs_id, var, year, ts_type)
                                    
                                    add_note=False
                                    if np.isnan(stats['R']):
                                        if sum(data.data.values[1].flatten()) != 0:
                                            raise Exception('Check...')
                                        add_note = True
                                    
                                    save_name_fig = data.save_name_aerocom + '_SCAT.png'
                                    data.plot_scatter(savefig=True, 
                                                      save_dir=OUT_DIR_SCAT,
                                                      save_name=save_name_fig, 
                                                      add_data_missing_note=add_note)
                                    
                                    data.to_csv(OUT_DIR_RESULTS)
                                    
                                    if TEST:
                                        raise Exception
                                    plt.close('all')
                                    
                        if EVAL_UNGRIDDED:       
                            for obs_id, ungridded_obs in ungridded_obs_all.items():
                                if not var in ungridded_obs.contains_vars:
                                    continue
                                if year == 9999:
                                    msg =('Ignoring climatology data (model: {}, '
                                          'obs: {}). '
                                          'Not yet implemented'.format(model_id,
                                                                       obs_id)) 
                                    print(msg)
                                    with open(OUT_STATS, 'a') as f:
                                        f.write('\n{}\n\n'.format(msg))
                                    
                                    continue
                                print('Analysing variable: {}\n'
                                      'Model {} vs. obs {}\n'
                                      'Year: {} ({} resolution)\n'
                                      .format(var, model_id, obs_id, 
                                              year, ts_type))
                                
                                model = model_reader.data_yearly[var][year]
                                
                                start_str = str(year) 
                                stop_str = '{}-12-31 23:59:00'.format(year)      
                                
                                data = pya.collocation.collocate_gridded_ungridded_2D(
                                            model, ungridded_obs, ts_type=ts_type, 
                                           start=start_str, stop=stop_str, 
                                           filter_name=filter_name)
                                
                                data.to_csv(OUT_DIR_RESULTS)
                                
                                stats = data.calc_statistics()
                                append_result(OUT_STATS, stats, 
                                              model_id, obs_id, var, year, ts_type)
                            
                                add_note=False
                                if np.isnan(stats['R']):
                                    if sum(data.data.values[1].flatten()) != 0:
                                        raise Exception('Check...')
                                    add_note = True
                                
                                save_name_fig = data.save_name_aerocom + '_SCAT.png'
                                data.plot_scatter(savefig=True, 
                                                  save_dir=OUT_DIR_SCAT,
                                                  save_name=save_name_fig, 
                                                  add_data_missing_note=add_note)
                                
                                plt.close('all')
                                    
                                
                            
                            
                                
                           