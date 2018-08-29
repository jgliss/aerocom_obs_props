#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 24 14:48:03 2018

@author: jonasg
"""
import pyaerocom as pya

MODEL = 'TM5_AP3-CTRL2016'
OBS = 'CALIOP3'

VAR = 'od550aer'
START=2008
STOP=2012
if __name__=='__main__':
    
    
    
    read_model = pya.io.ReadGridded(MODEL)
    read_obs = pya.io.ReadGridded(OBS)
    
    model = read_model.read_var(VAR,
                                start_time=START, 
                                stop_time=STOP)
    
    print(model)
    
    obs = read_obs.read_var(VAR,
                             start_time=START, 
                             stop_time=STOP)
    
    print(obs)
    
    obs_yearly = obs.regrid(model)