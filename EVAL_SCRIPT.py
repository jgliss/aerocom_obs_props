#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script for intercomparison of optical properties between models and 
"""
import helpers as helpers
import os
from collections import OrderedDict as od

from time import time
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pyaerocom as pya
from scipy.stats import pearsonr, spearmanr
import logging
from matplotlib.ticker import ScalarFormatter
### GLOBAL SETTINGS


YEARS = [2010, 2008, 9999]

MODEL_LIST = ['CAM6-Oslo_NF2kNucl_7jun2018AK',
              'OsloCTM2_INSITU',
              'TM5_AP3-CTRL2016',
              'TM5_AP3-INSITU']

GRIDDED_OBS_NETWORKS = ['MODIS6.terra', #od550aer
                        'MODIS6.aqua', #od550aer
                        'CALIOP3'] #od550aer

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
 
# some helper dictionaries for conversion of temporal resolution
TS_TYPE_TO_PANDAS_FREQ = {'hourly'  :   'H',
                          '3hourly' :   '3H',
                          'daily'   :   'D',
                          'monthly' :   'M'}


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
   
def calc_statistics(model_vals, obs_vals):
    result = {}
    difference = model_vals - obs_vals
    num_points = len(model_vals)
    
    result['obs_mean'] = obs_vals.mean()
    result['model_mean'] = model_vals.mean()
    result['rms'] = np.sqrt(np.nansum(np.power(difference, 2)) / num_points)
    result['nmb'] = np.sum(difference) / np.sum(obs_vals)*100.
    tmp = difference / (model_vals + obs_vals)
    
    result['mnmb'] = 2. / num_points * np.sum(tmp) * 100.
    result['fge'] = 2. / np.sum(np.abs(tmp)) * 100.
    
    result['R_pearson'] = pearsonr(model_vals, obs_vals)[0]
    result['R_spearman'] = spearmanr(model_vals, obs_vals)[0]
    
    return result
  
def plot_scatter(model_vals, obs_vals, model_id, var, obs_id, year, stations_ok,
                 plotname, filter_name, statistics=None, savefig=True,
                 save_dir=None, save_name=None, add_data_missing_note=False):
    
    if statistics is None:
        statistics = calc_statistics(model_vals, obs_vals)
        
    VAR_PARAM = pya.const.VAR_PARAM[var]

    fig, ax = plt.subplots(figsize=(8,6))
    ax.loglog(obs_vals, model_vals, ' k+')
    
    ax.set_xlim(VAR_PARAM['scat_xlim'])
    ax.set_ylim(VAR_PARAM['scat_ylim'])
    ax.set_xlabel('Obs: {} ({})'.format(obs_id, year), fontsize=14)
    ax.set_ylabel('{} ({})'.format(model_id, year), fontsize=14)
    ax.xaxis.set_major_formatter(ScalarFormatter())
    ax.yaxis.set_major_formatter(ScalarFormatter())
    
    plt.plot(VAR_PARAM['scat_xlim'], VAR_PARAM['scat_ylim'], '-', 
             color='grey')
    
    # text positions for the scatter plot annotations
    xypos=[]
    xypos.append((.01, 0.95))
    xypos.append((0.01, 0.90))
    xypos.append((0.3, 0.90))
    xypos.append((0.01, 0.86))
    xypos.append((0.3, 0.86))
    xypos.append((0.01, 0.82))
    xypos.append((0.3, 0.82))
    xypos.append((0.01, 0.78))
    xypos.append((0.3, 0.78))
    xypos.append((0.8, 0.1))
    xypos.append((0.8, 0.06))
    xypos_index = 0
    
    
    var_str = var + VAR_PARAM.unit_str
    ax.annotate("{} #: {} # st: {}".format(var_str, 
                        len(obs_vals), stations_ok),
                        xy=xypos[xypos_index], xycoords='axes fraction', 
                        fontsize=14, color='red')
    xypos_index += 1
    ax.annotate('Obs: {:.3f}'.format(statistics['obs_mean']),
                        xy=xypos[xypos_index], xycoords='axes fraction', 
                        fontsize=10, color='red')
    xypos_index += 1
    ax.annotate('Mod: {:.3f}'.format(statistics['model_mean']),
                        xy=xypos[xypos_index], xycoords='axes fraction', 
                        fontsize=10, color='red')
    xypos_index += 1
    ax.annotate('NMB: {:.1f}%'.format(statistics['nmb']),
                        xy=xypos[xypos_index], xycoords='axes fraction', 
                        fontsize=10, color='red')
    xypos_index += 1
    ax.annotate('MNMB: {:.1f}%'.format(statistics['mnmb']),
                        xy=xypos[xypos_index], xycoords='axes fraction', 
                        fontsize=10, color='red')
    xypos_index += 1
    ax.annotate('R: {:.3f}'.format(statistics['R_pearson']),
                        xy=xypos[xypos_index], xycoords='axes fraction', 
                        fontsize=10, color='red')
    xypos_index += 1
    ax.annotate('RMS: {:.3f}'.format(statistics['rms']),
                        xy=xypos[xypos_index], xycoords='axes fraction', 
                        fontsize=10, color='red')
    xypos_index += 1
    ax.annotate('FGE: {:.3f}'.format(statistics['fge']),
                        xy=xypos[xypos_index], xycoords='axes fraction', 
                        fontsize=10, color='red')
    # right lower part
    ax.annotate('{}'.format(plotname),
                        xy=xypos[-2], xycoords='axes fraction', 
                        ha='center', 
                        fontsize=10, color='black')
    ax.annotate('{}'.format(filter_name),
                        xy=xypos[-1], xycoords='axes fraction', ha='center', 
                        fontsize=10, color='black')
    if add_data_missing_note:
        ax.annotate('NO MODEL DATA',
                    xy=(0.4, 0.3), xycoords='axes fraction', ha='center', 
                        fontsize=20, color='red')
    ax.set_aspect('equal')
    
    if savefig:
        if any([x is None for x in (save_dir, save_name)]):
            raise IOError
            
        fig.savefig(os.path.join(save_dir, save_name))
    return ax
        
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
    
    RUN_EVAL = 1
    RELOAD = 1
    TEST_FIRST = 0
    PLOT_STATIONS = 0

    pya.change_verbosity('critical')
    if RUN_EVAL:
        
        if RELOAD:
            print('Importing model and obs data, this could take some time')
            ### Read gridded model data
            read_models = pya.io.ReadGriddedMulti(MODEL_LIST)
            read_models.read_individual_years(VARS, YEARS)
            
            ### Read gridded obs data
            read_gridded_obs = pya.io.ReadGriddedMulti(GRIDDED_OBS_NETWORKS)
            read_gridded_obs.read_individual_years(VARS, YEARS)
            
            read_ungridded_obs = pya.io.ReadUngridded()
            read_ungridded_obs.logger.setLevel(logging.INFO)
            # Load networks individually for now (easier for analysis below)
            ungridded_obs_all = od()
            for network, vars_to_retrieve in UNGRIDDED_OBS_NETWORKS.items():
                ungridded_obs_all[network] = read_ungridded_obs.read_dataset(
                        network, vars_to_retrieve=vars_to_retrieve)
        
            dirs = init_output_directories(read_models, ungridded_obs_all, OUT_DIR)
        
        
        if TEST_FIRST:
            # Ungridded data for Aeronet v2 level 2 daily
            ungridded_obs = ungridded_obs_all['AeronetSunV2Lev2.daily']
        
            # get coordinates of stations
            station_lons = ungridded_obs.longitude
            station_lats = ungridded_obs.latitude
            var = 'od550aer'
            # 2010
            year = YEARS[0]
            
            # temporal resolution
            ts_type = 'monthly'

            start_str = str(year) 
            stop_str = '{}-12-31 23:59:00'.format(year)
            
            
            model_id = 'TM5_AP3-CTRL2016'

            obs_id = ungridded_obs.metadata[0]['dataset_name']            
            filter_name = 'WORLD'
            
            plotname = 'mALLYEAR{}'.format(ts_type)
            # TM5_AP3-CTRL2016
            model = read_models[model_id].data_yearly[var][year]
            
            # extract year (it should be actually already the year, since 
            # we used the method read_individual_years above)
            data_cropped = model.crop(time_range=(start_str,
                                                       stop_str))
            
            # converted to daily resolution (Aeronet is daily)
            model_data = data_cropped.downscale_time(to_ts_type='monthly')
            
            RELOAD_SERIES = 1
            
            if RELOAD_SERIES:
                
                t10 = time()
                model_stat_data = model_data.to_time_series(longitude=station_lons,
                                                            latitude=station_lats)
                t11 = time()
                freq = TS_TYPE_TO_PANDAS_FREQ[model_data.ts_type]
                t20 = time()
                obs_stat_data = ungridded_obs.to_station_data_all(vars_to_convert=var, 
                                                                  start=start_str, 
                                                                  stop=stop_str, 
                                                                  freq=freq, 
                                                                  interp_nans=False, 
                                                                  min_coverage_interp=0.68)
                t21 = time()
                
            
            
            ax = pya.plot.plot_series_year(obs_stat_data[3], 
                                           model_stat_data[3],
                                           var, save_dir=OUT_DIR)

            obs_vals = []
            model_vals = []
            num_valid_obs = 0
            stations_ok = 0
            
            t30 = time()
            for i, obs_data in enumerate(obs_stat_data):
                if obs_data is not None:
                    if PLOT_STATIONS:
                        plt.close('all')
                        print('Plotting station {}'.format(i))
                        save_dir = os.path.join(dirs[model_id][year][obs_id], 'series_plots')
                        ax = pya.plot.plot_series_year(obs_data, 
                                                       model_stat_data[i],
                                                       var, 
                                                       save_dir=save_dir)
                    
                    # get model data corresponding to station
                    model_values = model_stat_data[i][var]
                    if sum(model_values.isnull()) > 0:
                        raise Exception
                    model_values.index = model_values.index.values.astype('<M8[{}]'.format(freq))
                    
                    # get all days that are not nan
                    obs = obs_data[var]
                    obs_ok = ~obs.isnull()
                    obs_dates_ok = obs.index[obs_ok].values.astype('<M8[{}]'.format(freq))
                    obs_vals.extend(obs.values[obs_ok])
                    
                    mv = model_values[obs_dates_ok].values
                    if sum(np.isnan(mv)) > 0:
                        raise Exception
                    model_vals.extend(mv)
                    
                    num_valid_obs += sum(obs_ok)
                    stations_ok += 1
                    
            model_vals = np.asarray(model_vals)
            obs_vals = np.asarray(obs_vals)
            
            if np.sum(np.isnan(model_vals)) > 0:
                raise Exception('Model stuff wrong...')
            elif np.sum(np.isnan(obs_vals)) > 0:
                raise Exception('Obs stuff wrong...')
                
            stats = calc_statistics(model_vals, obs_vals)
            
            save_name = ('{}_SCATTER_{}_{}_{}_{}_WORLD.png'.format(var, model_id, obs_id, 
                         year, ts_type))
            plot_scatter(model_vals, obs_vals, stats, save_dir=OUT_DIR,
                         save_name=save_name)
            
            
                
            t31 = time()
            print('Elapsed time computing model time series at stations: {:.2f} s'.format(t11-t10))
            print('Elapsed time computing model time series at stations: {:.2f} s'.format(t21-t20))
            print('Elapsed time merging all: {:.2f} s'.format(t31-t30))
            
            
        else:
            PLOT_STATIONS = 0
            # temporal resolution
            ts_type = 'monthly'
            plotname = 'mALLYEAR{}'.format(ts_type)
            filter_name = 'WORLD'
    
            # init results dictionary
            REEVAL = True
            for model_id, model_reader in read_models.results.items():
                for year in YEARS:
                    if not year in model_reader.years:
                        continue
                    for var in VARS:
                        if not var in model_reader.vars:
                            continue
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
                            save_name_csv = ('{}_{}_{}_{}_{}_WORLD.csv'
                                         .format(var, model_id, obs_id,  
                                                 year, ts_type))
                            loc_csv = os.path.join(OUT_DIR_RESULTS,
                                                   save_name_csv)
                            if os.path.exists(loc_csv) and not REEVAL:
                                print('Result file {} already exists'
                                      .format(loc_csv))
                            else:
                                station_lons = ungridded_obs.longitude
                                station_lats = ungridded_obs.latitude
                                
                                start_str = str(year) 
                                stop_str = '{}-12-31 23:59:00'.format(year)                
                
                                model = model_reader.data_yearly[var][year]
                
                                # extract year (it should be actually already the year, since 
                                # we used the method read_individual_years above)
                                model = model.crop(time_range=(start_str, stop_str))
                                # converted to daily resolution (Aeronet is daily)
                                model_data = downscale_time(model, 
                                                            to_ts_type='monthly')
                                
                                
                                model_stat_data = model_data.to_time_series(longitude=station_lons,
                                                                            latitude=station_lats)
                            
                                freq = TS_TYPE_TO_PANDAS_FREQ[model_data.ts_type]
                                
                                obs_stat_data = ungridded_obs.to_station_data_all(vars_to_convert=var, 
                                                                                  start=start_str, 
                                                                                  stop=stop_str, 
                                                                                  freq=freq, 
                                                                                  interp_nans=False, 
                                                                                  min_coverage_interp=0.68)
                                
                                    
                                
                                
                                
                                obs_vals = []
                                model_vals = []
                                num_valid_obs = 0
                                stations_ok = 0
                                
                                for i, obs_data in enumerate(obs_stat_data):
                                    if obs_data is not None:
                                        if PLOT_STATIONS:
                                            plt.close('all')
                                            print('Plotting station {}'.format(i))
                                            save_dir = os.path.join(dirs[model_id][year][obs_id], 'series_plots')
                                            ax = pya.plot.plot_series_year(obs_data, 
                                                                           model_stat_data[i],
                                                                           var, 
                                                                           save_dir=save_dir)
                                        
                                        # get model data corresponding to station
                                        model_values = model_stat_data[i][var]
                                        if sum(model_values.isnull()) > 0:
                                            raise Exception
                                        model_values.index = model_values.index.values.astype('<M8[{}]'.format(freq))
                                        
                                        # get all days that are not nan
                                        obs = obs_data[var]
                                        obs_ok = ~obs.isnull()
                                        obs_dates_ok = obs.index[obs_ok].values.astype('<M8[{}]'.format(freq))
                                        obs_vals.extend(obs.values[obs_ok])
                                        
                                        mv = model_values[obs_dates_ok].values
                                        if sum(np.isnan(mv)) > 0:
                                            raise Exception
                                        model_vals.extend(mv)
                                        
                                        num_valid_obs += sum(obs_ok)
                                        stations_ok += 1
                                        
                                model_vals = np.asarray(model_vals)
                                obs_vals = np.asarray(obs_vals)
                                
                                if np.sum(np.isnan(model_vals)) > 0:
                                    raise Exception('Model stuff wrong...')
                                elif np.sum(np.isnan(obs_vals)) > 0:
                                    raise Exception('Obs stuff wrong...')
                                    
                                stats = calc_statistics(model_vals, obs_vals)
                                print(stats)
                                
                                append_result(OUT_STATS, stats, model_id, obs_id, 
                                              var, year, ts_type)
                                save_name = ('{}_{}_{}_{}_{}_WORLD_SCATTER.png'
                                             .format(var, model_id, obs_id, 
                                                     year, ts_type))
                            
                                df = pd.DataFrame({'obs':obs_vals, 
                                                   'model': model_vals})
                                df.to_csv(os.path.join(OUT_DIR_RESULTS, save_name_csv))
                                
                                add_note=False
                                if np.isnan(stats['R_pearson']):
                                    if sum(model_vals) != 0:
                                        raise Exception('Check...')
                                    add_note = True
                                
                                
                                plot_scatter(model_vals, obs_vals, 
                                             model_id, var, obs_id, year, 
                                             stations_ok,
                                             plotname, filter_name,
                                             stats, save_dir=OUT_DIR_SCAT,
                                             save_name=save_name, 
                                             add_data_missing_note=add_note)
                                
                                
                                plt.close('all')
                                
                                
                            
                            
                                
                           