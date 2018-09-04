#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 24 14:48:03 2018

@author: jonasg
"""
import pyaerocom as pya
from warnings import filterwarnings

MODEL_ID = 'TM5_AP3-INSITU'
OBS_ID = 'AeronetSunV3Lev2.daily'
YEAR = 2010

if __name__=='__main__':
    filterwarnings('ignore')
    
    model_reader = pya.io.ReadGridded(MODEL_ID)
    
    obs_reader = pya.io.ReadUngridded()
    
    #obs_data = obs_reader.read(OBS_ID, VAR)
    VARS_FAILED = []
    RESULTS = {}
    
    for i, VAR in enumerate(model_reader.vars):
        
        try:
            h_avail = True
            model_h = model_reader.read_var(VAR, ts_type='hourly',
                                            flex_ts_type=False)
        except IOError:
            h_avail = False
        try:
            var_ok = True
            model_d = model_reader.read_var(VAR, ts_type='daily',
                                            flex_ts_type=False)
            model_m = model_reader.read_var(VAR, ts_type='monthly',
                                        flex_ts_type=False)
        except IOError:
            var_ok = False
            VARS_FAILED.append(VAR)
        
    
        
        
        
    


    
    
    
    
    
    