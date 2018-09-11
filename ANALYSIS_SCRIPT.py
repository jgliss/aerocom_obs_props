#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script for intercomparison of optical properties between models and 
"""

from models import all_model_ids
import pyaerocom as pya
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

ALL_MODELS = all_model_ids()

OBS_INFO = {'MODIS6.terra'          :   ['od550aer'],
            'MODIS6.aqua'           :   ['od550aer'],
            'AeronetSunV2Lev2.daily' :  ['od550aer', 'ang4487aer'],
            'AeronetSunV3Lev2.daily' :  ['od550aer', 'ang4487aer'],
            'AeronetSDAV2Lev2.daily' :  ['od550lt1aer', 
                                         'od550gt1aer'],
            'AeronetSDAV3Lev2.daily' :  ['od550lt1aer', 
                                         'od550gt1aer'],
            pya.const.AERONET_INV_V2L2_DAILY_NAME : ['abs550aer'],
            pya.const.AERONET_INV_V3L2_DAILY_NAME : ['abs550aer']}

# =============================================================================
# OBS_INFO = {'EBASMC'    :   ['absc550aer', 
#                              'scatc550aer']}
# =============================================================================

OBS_IDS = list(OBS_INFO.keys())

FILTER = 'WORLD-noMOUNTAINS'

### output directories
OUT_DIR = './output/'       
             
if __name__ == '__main__':
    from time import time
    
    t0 = time()
    REANALYSE_EXISTING = True
    RUN_ANALYSIS = True
    ONLY_FIRST = False
    
    if ONLY_FIRST:
        OBS_IDS = [OBS_IDS[0]]
    
    for OBS_ID in OBS_IDS:  
        VARS = OBS_INFO[OBS_ID]
        stp = helpers.AnalysisSetup(vars_to_analyse=VARS, 
                                    obs_id=OBS_ID, 
                                    years=YEARS,
                                    filter_name=FILTER, 
                                    ts_type_setup=TS_TYPE_SETUP,
                                    out_basedir=OUT_DIR)
        
        with open('output/result_log_{}.csv'.format(OBS_ID), 'w+') as log:
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
            if RUN_ANALYSIS:
                models = all_model_ids()
                if ONLY_FIRST:
                    models = [models[0]]
                for model_id in models:
                    log.write('\n\nModel: {}\n'.format(model_id))
                    stp.model_id = model_id
                    try:
                        helpers.perform_analysis(logfile=log, 
                                                 reanalyse_existing=REANALYSE_EXISTING,
                                                 **stp)
                    except Exception as e:
                        log.write('{}\n'.format(repr(e)))
    dt = (time()-t0)/60
    print('Analysis finished. Total time: {} min'.format(dt))