#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script for intercomparison of optical properties between models and 
"""

import helpers

# alternative ts_types in case one of the provided in setup is not in dataset
TS_TYPE_READ_ALT = {'daily'      :   ['hourly', '3hourly'],
                    'monthly'    :   ['daily', 'hourly', '3hourly']}            
# Todo: put this into class
TS_TYPE_SETUP = dict(monthly=['monthly', 'yearly'],
                     daily = ['monthly', 'yearly'],
                     read_alt=TS_TYPE_READ_ALT)

# Years to be analysed
YEARS = sorted([2008, 2010])

MODEL_ID = 'INCA-BCext_CTRL2016-PD'

OBS_ID = 'AeronetSunV3Lev2.daily' 
VARS = ['ang4487aer']

FILTER = 'WORLD-noMOUNTAINS'

### output directories
OUT_DIR = './output_TEMP/'       
             
if __name__ == '__main__':
    from time import time
    import os
    t0 = time()
    stp = helpers.AnalysisSetup(vars_to_analyse=VARS, 
                                obs_id=OBS_ID, 
                                years=YEARS,
                                filter_name=FILTER, 
                                ts_type_setup=TS_TYPE_SETUP,
                                out_basedir=OUT_DIR)
    
    with open(os.path.join(OUT_DIR, 'result_log_{}.csv'.format(OBS_ID)), 'w+') as log:
        log.write('Analysis configuration\n')
        for k, v in stp.items():
            if k == 'model_id':
                continue
            elif k == 'ts_type_setup':
                log.write('TS_TYPES (<read>: <analyse>)\n')
                for key, val in v.items():
                    if key == 'read_alt':
                        continue
                    log.write(' {}:{}\n'.format(key, val))
                if v['read_alt']:
                    log.write(' Alternative TS_TYPES (read)\n')
                    for key, val in v['read_alt'].items():
                        log.write('   {}:{}\n'.format(key, val))
            else:
                log.write('{}: {}\n'.format(k, v))
                    
                
    
        print(stp)
        
            
            
        
        log.write('\n\nModel: {}\n'.format(MODEL_ID))
        stp.model_id = MODEL_ID
        
        helpers.perform_analysis(logfile=log, 
                                 reanalyse_existing=True,
                                 **stp)
dt = (time()-t0)/60
print('Analysis finished. Total time: {} min'.format(dt))