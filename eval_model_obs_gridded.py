#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script for intercomparison of optical properties between models and 
"""
import os

import numpy as np
from functools import reduce
import pyaerocom as pya

from models import all_model_ids

### GLOBAL SETTINGS
class AnalysisSetup(pya.utils.BrowseDict):
    def __init__(self, **kwargs):
        self.vars = None
        
        self.model_id = None
        self.obs_id = None
        
        self.filer_name = None
        self.ts_types_read = None
        self.ts_types_ana = None
        self.years = None
        
# all temporal resolutions that are supposed to be read 
TS_TYPES_READ = ['monthly', 'daily']
TS_TYPES_READ_ALT = {'daily' : ['3hourly']}

# all temporal resolutions for which analysis is performed
TS_TYPES_ANA = ['yearly', 'monthly', 'daily']

# Years to be analysed
YEARS = sorted([2008, 2010])

ALL_MODELS = all_model_ids()

MODEL_ID = ALL_MODELS[0]
OBS_ID = 'MODIS6.terra'



VARS = ['od550aer']

FILTER = 'WORLD-noMOUNTAINS'

### output directories
OUT_DIR = './output/'

OUT_DIR_SCAT = os.path.join(OUT_DIR, 'scatter_plots')

OUT_DIR_RESULTS = os.path.join(OUT_DIR, 'results_csv')
                    
_PLOTNAME_BASESTR = 'mALLYEAR{}'   

TS_TYPES = pya.const.GRID_IO.TS_TYPES
   
def start_stop_from_year(year):
    start = pya.helpers.to_pandas_timestamp(year)
    stop = pya.helpers.to_pandas_timestamp('{}-12-31 23:59:59'.format(year))
    return (start, stop)

if __name__=="__main__":
    
    exceptions = []
    pya.change_verbosity('warning')
        
    model_reader = pya.io.ReadGridded(MODEL_ID)
    obs_reader = pya.io.ReadGridded(OBS_ID)
    
    var_matches = list(reduce(np.intersect1d, (VARS, 
                                          model_reader.vars,
                                          obs_reader.vars)))
    
    if len(var_matches) == 0:
        raise pya.exceptions.DataCoverageError('No variable matches between '
                                               '{} and {} for input vars: {}'
                                               .format(MODEL_ID, OBS_ID, 
                                                       VARS))
    
    year_matches = list(reduce(np.intersect1d, (YEARS, 
                                                model_reader.years,
                                                obs_reader.years)))
    
    if len(year_matches) == 0:
        raise pya.exceptions.DataCoverageError('No year matches between '
                                               '{} and {} for input vars: {}'
                                               .format(MODEL_ID, OBS_ID, 
                                                       VARS))
    ts_type_matches = list(np.intersect1d(TS_TYPES_READ, model_reader.ts_types))
    for ts_type, ts_types_alt in TS_TYPES_READ_ALT.items():
        if not ts_type in ts_type_matches:
            for ts_type_alt in ts_types_alt:
                if ts_type_alt in model_reader.ts_types:
                    ts_type_matches.append(ts_type_alt)
                    break
                
    if len(ts_type_matches) == 0:
        raise pya.exceptions.DataCoverageError('No ts_type matches between '
                                               '{} and {} for input vars: {}'
                                               .format(MODEL_ID, OBS_ID, 
                                                       VARS))
    for year in year_matches:
        start, stop = start_stop_from_year(year)
        for ts_type in ts_type_matches:
            
            model_reader.read(var_matches, start_time=year,
                              ts_type = ts_type,
                              flex_ts_type=False)
            
            obs_reader.read(var_matches, start_time=year,
                            ts_type = ts_type,
                            flex_ts_type=True)
            
            plotname = _PLOTNAME_BASESTR.format(ts_type)
            
            if len(model_reader.data) == 0:
                exceptions.append('{}_{}: No data available'.format(year, ts_type))
            else:
                for var, model_data in model_reader.data.items():
                    for ts_type_ana in TS_TYPES_ANA:
                        if TS_TYPES.index(ts_type_ana) >= TS_TYPES.index(ts_type):
                            if var in obs_reader.data:
                                obs_data = obs_reader.data[var]
                                data_coll = pya.collocation.collocate_gridded_gridded(
                                                model_data, obs_data, 
                                                ts_type=ts_type_ana, 
                                                start=start, stop=stop, 
                                                filter_name=FILTER)
                                    
                                data_coll.to_csv(OUT_DIR_RESULTS)
                                save_name_fig = data_coll.save_name_aerocom + '_SCAT.png'
                        
                                data_coll.plot_scatter(savefig=True, 
                                                   save_dir=OUT_DIR_SCAT,
                                                   save_name=save_name_fig)
                        
            
# =============================================================================
#         for year in YEARS:
# 
#             for var in VARS:
#                 if not var in model_reader.vars:
#                     continue
#                 
#             
#                     
#                         for obs_id, ungridded_obs in ungridded_obs_all.items():
#                             if not var in ungridded_obs.contains_vars:
#                                 continue
#                             if year == 9999:
#                                 msg =('Ignoring climatology data (model: {}, '
#                                       'obs: {}). '
#                                       'Not yet implemented'.format(model_id,
#                                                                    obs_id)) 
#                                 print(msg)
#                                 with open(OUT_STATS, 'a') as f:
#                                     f.write('\n{}\n\n'.format(msg))
#                                 
#                                 continue
#                             print('Analysing variable: {}\n'
#                                   'Model {} vs. obs {}\n'
#                                   'Year: {} ({} resolution)\n'
#                                   .format(var, model_id, obs_id, 
#                                           year, ts_type))
#                             
#                             model = model_reader.data_yearly[var][year]
#                             
#                             start_str = str(year) 
#                             stop_str = '{}-12-31 23:59:00'.format(year)      
#                             
#                             data = pya.collocation.collocate_gridded_ungridded_2D(
#                                         model, ungridded_obs, ts_type=ts_type, 
#                                         start=start_str, stop=stop_str, 
#                                         filter_name=filter_name)
#                             
#                             data.to_csv(OUT_DIR_RESULTS)
#                             
#                             stats = data.calc_statistics()
#                             append_result(OUT_STATS, stats, 
#                                           model_id, obs_id, var, year, ts_type)
#                         
#                             add_note=False
#                             if np.isnan(stats['R']):
#                                 if sum(data.data.values[1].flatten()) != 0:
#                                     raise Exception('Check...')
#                                 add_note = True
#                             
#                             save_name_fig = data.save_name_aerocom + '_SCAT.png'
#                             data.plot_scatter(savefig=True, 
#                                               save_dir=OUT_DIR_SCAT,
#                                               save_name=save_name_fig)
#                             
#                             plt.close('all')
#                                     
#                                 
#                             
#                             
#                                 
#                            
# =============================================================================

                