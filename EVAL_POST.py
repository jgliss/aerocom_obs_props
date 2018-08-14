#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script for intercomparison of optical properties between models and 
"""
import pandas as pd
import numpy as np
import os
import EVAL_SCRIPT as EVAL
### GLOBAL SETTINGS

def get_info_filename(fpath):
    fname = os.path.basename(fpath).split('.csv')[0].strip()
    
    spl = fname.split('_')
    if len(spl) == 7:
        result = dict(var = spl[0],
                      model_id = spl[1] + '_' + spl[2],
                      obs_id = spl[3],
                      year = int(spl[4]),
                      ts_type = spl[5],
                      filtername = spl[6])
    else:
        result = dict(var = spl[0],
                      model_id = spl[1],
                      obs_id = spl[2],
                      year = int(spl[3]),
                      ts_type = spl[4],
                      filtername = spl[5])
    return result
        
        
def load_result_files(out_dir = EVAL.OUT_DIR_RESULTS):
    files = os.listdir(out_dir)
    results = []
    for file in files:
        print('Reading result file {}'.format(file))
        info = get_info_filename(file)
        info['data'] = pd.DataFrame.from_csv(os.path.join(out_dir, file))
        results.append(info)
    return results
    
def calc_stats(results):
    for result in results:
        obs = result['data']['obs'].values
        model = result['data']['model'].values
        result.update(EVAL.calc_statistics(model, obs))
    return results

def to_multiindex_dataframe(results):
    header = ['Model', 'Year', 'Variable', 'Obs', 'Bias', 'RMS', 'R']
    data = []
    for r in results:
        file_data = [r['model_id'], r['year'], r['var'], r['obs_id'],
                     r['nmb'], r['rms'], r['R_pearson']]
        data.append(file_data)
    df = pd.DataFrame(data, columns=header)
    df.set_index(['Model', 'Year', 'Variable', 'Obs'], inplace=True)
    return df

if __name__=="__main__":
    results = load_result_files()
    results = calc_stats(results)
    
    result= to_multiindex_dataframe(results)
    
    print(result)
    
    from seaborn import heatmap
    
    bias = result['Bias']
    
    print(bias)
    
    hea    
    
# =============================================================================
#     s = pd.Series(bias)
#     s2 = pd.Series(rms)
#     
# =============================================================================
    #pd.Dat
                            
                            
                                
                           