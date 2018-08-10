#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script for intercomparison of optical properties between models and 
"""
import helpers as helpers
import iris
import pandas as pd
import matplotlib.pyplot as plt
import pyaerocom as pya
import logging
### GLOBAL SETTINGS

RUN_EVAL = 1
RELOAD = 0
TEST_FIRST = 1
YEARS = [2010, 2008, 9999]

VARS = ['od550aer', 
        'od550gt1aer', 
        'od550lt1aer',
        'abs550aer']

MODEL_LIST = ['CAM6-Oslo_NF2kNucl_7jun2018AK',
              'OsloCTM2_INSITU',
              'TM5_AP3-CTRL2016',
              'TM5_AP3-INSITU']

GRIDDED_OBS_NETWORKS = ['MODIS6.terra', #od550aer
                        'MODIS6.aqua', #od550aer
                        'CALIOP3'] #od550aer

# will be filled during the import
READ_PROBLEMATIC = {}

UNGRIDDED_OBS_NETWORKS = [#'AeronetSDAV2Lev2.daily',] # od550aer, od550lt1aer, od550gt1aer
                          #'AeronetSDAV3Lev2.daily', # od550aer, od550lt1aer, od550gt1aer
                          'AeronetSunV2Lev2.daily', # od550aer
                          #'AeronetSunV3Lev2.daily',# od550aer
                          #pya.const.AERONET_INV_V2L2_DAILY_NAME, #abs550aer, od550aer
                          #pya.const.AERONET_INV_V3L2_DAILY_NAME #abs550aer, od550aer
                          ]
               #'EBASMC'] # ec550aer, ...

### Paths and directories
MODEL_INFO_FILE = ('/lustre/storeA/project/aerocom/'
                   'aerocom-users-database/AEROCOM-PHASE-III/reference-list')

OUT_DIR = './output/'
  
def data_to_daily(gridded_data):
    """Downscale gridded data to daily resolution"""
# =============================================================================
#     if not isinstance(gridded_data, pya.griddeddata.GriddedData):
#         raise TypeError('Invalid input, need instance of GriddedData class, '
#                         'got {}'.format(type(gridded_data)))
# =============================================================================
    ts_types_avail = pya.const.GRID_IO.TS_TYPES
    idx_daily = ts_types_avail.index('daily')
    ts_type = gridded_data.ts_type
    if ts_type == 'daily':
        pya.logger.info('Data is already in daily resolution')
        return gridded_data
    if not ts_type in ts_types_avail:
        raise pya.exceptions.TemporalResolutionError('Resolution {} cannot '
            'converted'.format(ts_type))
    elif ts_types_avail.index(ts_type) >= idx_daily:
        raise pya.exceptions.TemporalResolutionError('Cannot increase temp. '
            'resolution from {} to daily'.format(ts_type))
    cube = gridded_data.grid
    iris.coord_categorisation.add_day_of_year(cube, 'time')
    aggregated = cube.aggregated_by('day_of_year', iris.analysis.MEAN)
    data = pya.GriddedData(aggregated, **gridded_data.suppl_info)
    data.suppl_info['ts_type'] = 'daily'
    return data
    
TS_TYPE_TO_PANDAS_FREQ = {'hourly'  :   'H',
                          '3hourly' :   '3H',
                          'daily'   :   'D',
                          'monthly' :   'M'}
if __name__=="__main__":
    helpers.print_file(MODEL_INFO_FILE)
    
    if RUN_EVAL:
        
        if RELOAD:
            ### Read gridded model data
            read_models = pya.io.ReadGriddedMulti(MODEL_LIST)
            read_models.read_individual_years(VARS, YEARS)
            
            
            
            ### Read gridded obs data
            read_gridded_obs = pya.io.ReadGriddedMulti(GRIDDED_OBS_NETWORKS)
            read_gridded_obs.read_individual_years(VARS, YEARS)
            
            ### Read ungridded obs data
            pya.change_verbosity('critical')
        read_ungridded_obs = pya.io.ReadUngridded(datasets_to_read=
                                                  UNGRIDDED_OBS_NETWORKS,
                                                  vars_to_retrieve=VARS)
        read_ungridded_obs.logger.setLevel(logging.INFO)
        ungridded_obs = read_ungridded_obs.read()
        
        # get coordinates of stations
        station_lons = ungridded_obs.longitude
        station_lats = ungridded_obs.latitude
        
        STOP_IDX = 20
        for stat_idx, info in ungridded_obs.metadata.items():
            print(stat_idx, info['station_name'], info['dataset_name'])
            if stat_idx == STOP_IDX:
                break
        
        # TEST access single station data
        station1 = ungridded_obs.to_station_data(0, ['od550aer', 'od550gt1aer'],
                                                 start='2013-10', 
                                                 stop='2015',
                                                 freq='M')
        
        print(read_models)   
        print(read_gridded_obs)
        print(station1)
        
        if TEST_FIRST:
            # od550aer
            var = VARS[0]
            # 2010
            year = YEARS[0]

            start_str, stop_str = str(year), str(year + 1)
            # TM5_AP3-CTRL2016
            model_data = read_models[2].data_yearly[var][year]
            
            # extract year (it should be actually already the year, since 
            # we used the method read_individual_years above)
            data_cropped = model_data.crop(time_range=(start_str,
                                                       stop_str))
            # converted to daily resolution (Aeronet is daily)
            model_daily = data_to_daily(data_cropped)
            
            from time import time
            t10 = time()
            model_stat_data = model_daily.to_time_series(longitude=station_lons,
                                                         latitude=station_lats)
            t11 = time()
            
            
            freq = TS_TYPE_TO_PANDAS_FREQ[model_daily.ts_type]
            t20 = time()
            obs_stat_data = ungridded_obs.to_station_data_all(vars_to_convert=var, 
                                                              start=start_str, 
                                                              stop=stop_str, 
                                                              freq=freq, interp_nans=False, 
                                                              min_coverage_interp=0.68)
            t21 = time()
            
            miss_stats = 0
            
            obs_vals = []
            model_vals = []
            num_valid_obs = 0
            
            
            for i, obs_data in enumerate(obs_stat_data):
                if obs_data is not None:
                    # get model data corresponding to station
                    model_data = model_stat_data[i][var]
                    model_data.index = model_data.index.values.astype('<M8[{}]'.format(freq))
                    
                    # get all days that are not nan
                    obs = obs_data[var]
                    obs_ok = ~obs.isnull()
                    obs_dates_ok = obs.index[obs_ok].values.astype('<M8[{}]'.format(freq))
                    obs_vals.extend(obs.values[obs_ok])
                    
                    model_vals.extend(model_data[obs_dates_ok].values)
                    
                    num_valid_obs += sum(obs_ok)
                    
                else:
                    miss_stats += 1
            
            print('Elapsed time computing model time series at stations: {:.2f} s'.format(t11-t10))
            print('Elapsed time computing model time series at stations: {:.2f} s'.format(t21-t20))
        else:
            raise NotImplementedError
        
        # now 
        
        
        
        
        
        