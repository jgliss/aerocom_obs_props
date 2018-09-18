#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  7 08:19:06 2018

@author: jonasg
"""
import os
import numpy as np
import pyaerocom as pya
from functools import reduce
import pandas as pd
import matplotlib.pyplot as plt

class AnalysisSetup(pya._lowlevel_helpers.BrowseDict):
    """Setup class for model / obs intercomparison
    
    An instance of this setup class can be used to run a collocation analysis
    between a model and an observation network and will create a number of 
    :class:`pya.CollocatedData` instances and save them as netCDF file.
    
    Note
    ----
    This is a very first draft and may change
    
    Attributes
    ----------
    vars_to_analyse : list
        variables to be analysed (should be available in model and obs data)
    """
    
    def __init__(self, vars_to_analyse=None, model_id=None, obs_id=None, 
                 years=None, filter_name='WORLD-noMOUNTAINS',
                 ts_type_setup=None, out_basedir=None, **kwargs):
        
        self.vars_to_analyse = vars_to_analyse
        
        self.model_id = model_id
        self.obs_id = obs_id
        
        self.filter_name = filter_name
        if not isinstance(ts_type_setup, _TS_TYPESetup):
            ts_type_setup = _TS_TYPESetup(**ts_type_setup)
        self.ts_type_setup = ts_type_setup
        self.years = years
        
        self.out_basedir = out_basedir
        
        self.update(**kwargs)
        
 
def get_all_vars(OBS_INFO_DICT):
    all_vars = []
    for obs_id, variables in OBS_INFO_DICT.items():
        for variable in list(variables):
            if not variable in all_vars:
                all_vars.append(variable)
    return all_vars

class _TS_TYPESetup(pya._lowlevel_helpers.BrowseDict):
    def __init__(self, *args, **kwargs):
        self.read_alt = {}
        super(_TS_TYPESetup, self).__init__(*args, **kwargs)
        
    def __str__(self):
        s ='ts_type settings (<read>: <analyse>)\n'
        for key, val in self.items():
            if key == 'read_alt':
                continue
            s+=' {}:{}\n'.format(key, val)
        if self['read_alt']:
            s+=' Alternative ts_types (read)\n'
            for key, val in self['read_alt'].items():
                s+='   {}:{}\n'.format(key, val)
   
def check_prepare_dirs(basedir, model_id):
    def chk_make_dir(base, name):
        d = os.path.join(base, name)
        if not os.path.exists(d):
            os.mkdir(d)
        return d
    dirs = {}
    if not os.path.exists(basedir):
        basedir = pya.const.OUT_BASEDIR
    
    out_dir = chk_make_dir(basedir, model_id)
    dirs['data'] = chk_make_dir(out_dir, 'data')
    dirs['scatter_plots'] = chk_make_dir(out_dir, 'scatter_plots')
    return dirs
    
def prepare_ts_types(model_reader, ts_type_setup):
    ts_type_read = list(ts_type_setup.keys())
    ts_type_matches = list(np.intersect1d(ts_type_read, model_reader.ts_types))
    if 'read_alt' in ts_type_setup:
        ts_type_read_alt = ts_type_setup.read_alt
        for ts_type, ts_types_alt in ts_type_read_alt.items():
            if not ts_type in ts_type_matches:
                for ts_type_alt in ts_types_alt:
                    if ts_type_alt in model_reader.ts_types:
                        ts_type_matches.append(ts_type_alt)
                        ts_type_setup[ts_type_alt] = ts_type_setup[ts_type]
                        break
    return (ts_type_matches, ts_type_setup)

def start_stop_from_year(year):
    start = pya.helpers.to_pandas_timestamp(year)
    stop = pya.helpers.to_pandas_timestamp('{}-12-31 23:59:59'.format(year))
    return (start, stop)

def colldata_save_name(model_data, model_id, obs_id, ts_type_ana, filter_name,
                       start=None, stop=None):
    
    if start is None:
        start = model_data.start_time
    else:
        start = pya.helpers.to_pandas_timestamp(start)    
    if stop is None:
        stop = model_data.stop_time
    else:
        stop = pya.helpers.to_pandas_timestamp(stop)
    
    start_str = pya.helpers.to_datestring_YYYYMMDD(start)
    stop_str = pya.helpers.to_datestring_YYYYMMDD(stop)
    ts_type_src = model_data.ts_type
    coll_data_name = pya.CollocatedData._aerocom_savename(model_data.var_name, 
                                                          obs_id, 
                                                          model_id, 
                                                          ts_type_src, 
                                                          start_str, 
                                                          stop_str, 
                                                          ts_type_ana, 
                                                          filter_name)
    return coll_data_name + '.nc'

def check_colldata_exists(data_dir, colldata_save_name):
        
    files = os.listdir(data_dir)
    if colldata_save_name in files:
        return True
    return False

def get_file_list(result_dir, models, verbose=True):
    all_files = []
    for item in os.listdir(result_dir):
        if item in models:
            data_dir = os.path.join(result_dir, item, 'data/')
            files = os.listdir(data_dir)
            if len(files) > 0:
                if verbose:
                    print('Importing {} result files from model {}'
                          .format(len(files), item))
                for f in files:
                    if f.endswith('COLL.nc'):
                        all_files.append(os.path.join(data_dir, f))
    return all_files

def load_result_files(file_list, verbose=True):
    results = []
    data = pya.CollocatedData()
    try:
        from ipywidgets import FloatProgress
        from IPython.display import display
        
        max_count = len(file_list)
        
        f = FloatProgress(min=0, max=max_count) # instantiate the bar
        display(f) # display the bar
    except Exception as e:
        print('Failed to instantiate progress bar: {}'.format(repr(e)))
    
    for file in file_list:
        info = data.get_meta_from_filename(file)
        info['model_id'] = info['data_source'][1]
        info['obs_id'] = info['data_source'][0]
        info['year'] = info['start'].year
        info['data'] = data.read_netcdf(file).to_dataframe()
        obs = info['data']['ref'].values
        model = info['data']['data'].values
        stats = pya.mathutils.calc_statistics(model, obs)
        info.update(stats)
        
        results.append(info)
        if f is not None:
            f.value += 1
    return results
    
def results_to_dataframe(results):
    """Based on output of :func:`get_result_info`"""
    header = ['Model', 'Year', 'Variable', 'Obs', 'Freq', 'FreqSRC',
              'Bias', 'RMS', 'R', 'FGE']
    data = []
    for info in results:
        file_data = [info['model_id'], 
                     info['year'], 
                     info['var_name'], 
                     info['obs_id'],
                     info['ts_type'],
                     info['ts_type_src'],
                     info['nmb'], 
                     info['rms'], 
                     info['R'], 
                     info['fge']]
        
        data.append(file_data)
    df = pd.DataFrame(data, columns=header)
    df.set_index(['Model', 'Year', 'Variable', 'Obs'], inplace=True)
    df.sort_index(inplace=True)
    return df
    
def slice_dataframe(df, values, levels):
    """Crop a selection from a MultiIndex Dataframe
    
    Parameters
    ----------
    df : DataFrame
        
    
    """
    names = df.index.names
    num_indices = len(names)
    if num_indices == 1:
        # no Multiindex
        return df.loc[values, :]
    else:
        # Multiindex
        if levels is None:
            print("Input levels not defined for MultiIndex, assuming 0")
            levels = [0]
        elif isinstance(levels, str): #not a list
            levels, values = [levels], [values]
        else: #not a string and not None, so either a list or a number (can be checked using iter())
            try:
                iter(levels)
            except:
                #input is single level / value pair
                levels, values = [levels], [values]        
    
        if isinstance(levels[0], str):
            level_nums = [names.index(x) for x in levels]
        else:
            level_nums = levels
        
        indexer = []
        for idx in range(len(names)):
            if idx in level_nums:
                pos = level_nums.index(idx)
                indexer.append(values[pos])
            else:
                indexer.append(slice(None))
        df = df.loc[tuple(indexer), :]
        
        for i, level in enumerate(levels):
            if len(values[i]) == 1:
                df.index = df.index.droplevel(level)
        df.sort_index(inplace=True)
        return df
    
def perform_analysis(vars_to_analyse, model_id, obs_id, years, filter_name, 
                     ts_type_setup, out_basedir=None, logfile=None,
                     reanalyse_existing=False):
    plt.ioff()
    try:
        pya.io.ReadUngridded(obs_id)
        _run_gridded_ungridded(vars_to_analyse, model_id, obs_id, years, filter_name, 
                               ts_type_setup, out_basedir, logfile,
                               reanalyse_existing)
        
    except pya.exceptions.NetworkNotSupported:
        _run_gridded_gridded(vars_to_analyse, model_id, obs_id, years, 
                             filter_name, ts_type_setup, out_basedir, logfile,
                             reanalyse_existing)
    plt.ion()

def _run_gridded_ungridded(vars_to_analyse, model_id, obs_id, years, filter_name, 
                           ts_type_setup, out_basedir=None, logfile=None,
                           reanalyse_existing=False):
    # all temporal resolutions that are supposed to be read 
    dirs = check_prepare_dirs(out_basedir, model_id)
        
    obs_reader = pya.io.ReadUngridded()
    obs_data = obs_reader.read(obs_id, vars_to_analyse)
    
    ts_types = pya.const.GRID_IO.TS_TYPES
    
        
    model_reader = pya.io.ReadGridded(model_id)
    
    var_matches = list(reduce(np.intersect1d, (vars_to_analyse, 
                                               model_reader.vars_provided,
                                               obs_data.contains_vars)))
    
    if len(var_matches) == 0:
        raise pya.exceptions.DataCoverageError('No variable matches between '
                                               '{} and {} for input vars: {}'
                                               .format(model_id, obs_id, 
                                                       vars_to_analyse))
    
    year_matches = list(np.intersect1d(years, model_reader.years))
    if len(year_matches) == 0:
        raise pya.exceptions.DataCoverageError('No year matches between '
                                               '{} and {} for input vars: {}'
                                               .format(model_id, obs_id, 
                                                       vars_to_analyse))
    ts_type_matches, ts_type_setup = prepare_ts_types(model_reader,
                                                      ts_type_setup)            
    if len(ts_type_matches) == 0:
        raise pya.exceptions.DataCoverageError('No ts_type matches between '
                                               '{} and {} for input vars: {}'
                                               .format(model_id, obs_id, 
                                                       vars_to_analyse))
    
                
    for year in year_matches:
        start, stop = start_stop_from_year(year)
        for ts_type in ts_type_matches:
            ts_types_ana = ts_type_setup[ts_type]
            model_reader.read(var_matches, 
                              start_time=year,
                              ts_type=ts_type,
                              flex_ts_type=False)
                        
            if len(model_reader.data) == 0:
                if logfile:    
                    logfile.write('No model data available ({}, {})\n'.format(year, 
                                  ts_type))
                continue
            
            for var, model_data in model_reader.data.items():
                if not var in obs_reader.data:
                    if logfile:    
                        logfile.write('No obs data available ({}, {})\n'.format(year, 
                          ts_type))
                    continue
                for ts_type_ana in ts_types_ana:
                    if ts_types.index(ts_type_ana) >= ts_types.index(ts_type):
                    
                        out_dir = dirs['data']
                        savename = colldata_save_name(model_data, 
                                                      model_id, 
                                                      obs_id, 
                                                      ts_type_ana, 
                                                      filter_name,
                                                      start,
                                                      stop)
                        file_exists = check_colldata_exists(out_dir, 
                                                            savename)
                        if file_exists:
                            if not reanalyse_existing:
                                if logfile:
                                    logfile.write('SKIP: {}\n'.format(savename))
                                continue
                            else:
                                os.remove(os.path.join(out_dir, savename))
                        
                        data_coll = pya.collocation.collocate_gridded_ungridded_2D(
                                                model_data, obs_data, 
                                                ts_type=ts_type_ana, 
                                                start=start, stop=stop, 
                                                filter_name=filter_name)
                            
                        data_coll.to_netcdf(out_dir)
                        save_name_fig = data_coll.save_name_aerocom + '_SCAT.png'
                        if logfile:
                            logfile.write('WRITE: {}\n'.format(savename))
                            
                        data_coll.plot_scatter(savefig=True, 
                                               save_dir=dirs['scatter_plots'],
                                               save_name=save_name_fig)
                        plt.close('all')
                        
def _run_gridded_gridded(vars_to_analyse, model_id, obs_id, years, filter_name, 
                         ts_type_setup, out_basedir=None, logfile=None,
                         reanalyse_existing=False):
    # all temporal resolutions that are supposed to be read 
    dirs = check_prepare_dirs(out_basedir, model_id)
            
    ts_types = pya.const.GRID_IO.TS_TYPES
        
    model_reader = pya.io.ReadGridded(model_id)
    obs_reader = pya.io.ReadGridded(obs_id)

    var_matches = list(reduce(np.intersect1d, (vars_to_analyse, 
                                               model_reader.vars_provided,
                                               obs_reader.vars)))
    
    if len(var_matches) == 0:
        raise pya.exceptions.DataCoverageError('No variable matches between '
                                               '{} and {} for input vars: {}'
                                               .format(model_id, obs_id, 
                                                       vars_to_analyse))
    
    year_matches = list(reduce(np.intersect1d, (years, 
                                                model_reader.years,
                                                obs_reader.years)))
    
    if len(year_matches) == 0:
        raise pya.exceptions.DataCoverageError('No year matches between '
                                               '{} and {} for input vars: {}'
                                               .format(model_id, obs_id, 
                                                       vars_to_analyse))
        
    
    ts_type_matches, ts_type_setup = prepare_ts_types(model_reader,
                                                      ts_type_setup)            
    if len(ts_type_matches) == 0:
        raise pya.exceptions.DataCoverageError('No ts_type matches between '
                                               '{} and {} for input vars: {}'
                                               .format(model_id, obs_id, 
                                                       vars_to_analyse))
    
                
    for year in year_matches:
        start, stop = start_stop_from_year(year)
        for ts_type in ts_type_matches:
            ts_types_ana = ts_type_setup[ts_type]
            # reads only year if starttime is provided but not stop time
            model_reader.read(var_matches, 
                              start_time=year,
                              ts_type=ts_type,
                              flex_ts_type=False)
            
            obs_reader.read(var_matches, start_time=year,
                            ts_type = ts_type,
                            flex_ts_type=True)
            
            if len(model_reader.data) == 0:
                if logfile:    
                    logfile.write('No model data available ({}, {})\n'.format(year, 
                                  ts_type))
                continue
            
            for var, model_data in model_reader.data.items():
                if not var in obs_reader.data:
                    if logfile:    
                        logfile.write('No obs data available ({}, {})\n'.format(year, 
                          ts_type))
                    continue
                for ts_type_ana in ts_types_ana:
                    if ts_types.index(ts_type_ana) >= ts_types.index(ts_type):
                        obs_data = obs_reader.data[var]
                        out_dir = dirs['data']
                        savename = colldata_save_name(model_data, 
                                                      model_id, 
                                                      obs_id, 
                                                      ts_type_ana, 
                                                      filter_name,
                                                      start,
                                                      stop)
                        
                        file_exists = check_colldata_exists(out_dir, 
                                                            savename)
                        if file_exists:
                            if not reanalyse_existing:
                                if logfile:
                                    logfile.write('SKIP: {}\n'.format(savename))
                                continue
                            else:
                                os.remove(os.path.join(out_dir, savename))
                            
                        data_coll = pya.collocation.collocate_gridded_gridded(
                                        model_data, obs_data, 
                                        ts_type=ts_type_ana, 
                                        start=start, stop=stop, 
                                        filter_name=filter_name)
                            
                        if data_coll.save_name_aerocom + '.nc' != savename:
                            raise Exception
                        data_coll.to_netcdf(out_dir)
                        save_name_fig = data_coll.save_name_aerocom + '_SCAT.png'
                        if logfile:
                            logfile.write('WRITE: {}\n'.format(savename))
                            
                        data_coll.plot_scatter(savefig=True, 
                                           save_dir=dirs['scatter_plots'],
                                           save_name=save_name_fig)
                        plt.close('all')
                        
def print_file(file_path):
    if not os.path.exists(file_path):
        raise IOError('File not found...')
    with open(file_path) as f:
        for line in f:
            if line.strip():
                print(line)
                