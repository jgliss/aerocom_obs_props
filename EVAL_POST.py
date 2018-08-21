#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script for intercomparison of optical properties between models and 
"""
import pandas as pd
import numpy as np
import pyaerocom as pya
import os
import EVAL_SCRIPT as EVAL
### GLOBAL SETTINGS

def get_info_filename(fpath):
    return pya.collocateddata.CollocatedData().get_meta_from_filename(fpath)
        
        
def load_result_files(out_dir=EVAL.OUT_DIR_RESULTS):
    files = os.listdir(out_dir)
    results = []
    for file in files:
        info = get_info_filename(file)
        info['model_id'] = info['data_source_idx'][1]
        info['obs_id'] = info['data_source_idx'][0]
        info['year'] = info['start'].year
        info['data'] = pd.DataFrame.from_csv(os.path.join(out_dir, file))
        results.append(info)
    return results
    
def calc_stats(results):
    for result in results:
        obs = result['data']['ref'].values
        model = result['data']['data'].values
        stats = pya.mathutils.calc_statistics(model, obs)
        result.update(stats)
    return results

def to_multiindex_dataframe(results):
    header = ['Model', 'Year', 'Freq', 'Variable', 'Obs', 'Bias', 'RMS', 'R', 'FGE']
    data = []
    for r in results:
        file_data = [r['model_id'], r['year'], r['ts_type'], r['var_name'], r['obs_id'],
                     r['nmb'], r['rms'], r['R'], r['fge']]
        data.append(file_data)
    df = pd.DataFrame(data, columns=header)
    df.set_index(['Model', 'Year', 'Freq', 'Variable', 'Obs'], inplace=True)
    return df

if __name__=="__main__":
    results = load_result_files()
    results = calc_stats(results)
    
    result= to_multiindex_dataframe(results)
    
    print(result)
    
    bias = result['Bias']
    
    print(bias)
    
# =============================================================================
#     s = pd.Series(bias)
#     s2 = pd.Series(rms)
#     
# =============================================================================
    #pd.Dat
                            
                            
                                
                           