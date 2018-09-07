#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 24 14:48:03 2018

@author: jonasg
"""
import pyaerocom as pya


MODEL = 'TM5_AP3-CTRL2016'

OBS = 'CALIOP_V3.00_Cloudfree_day'
VAR = 'od550aer'

START=2007
STOP=2009

if __name__=='__main__':
    ### Model data
    read_model = pya.io.ReadGridded(MODEL)
    read_obs = pya.io.ReadGridded(OBS)
    
    model = read_model.read_var(VAR,
                                start_time=START, 
                                stop_time=STOP)
    
    ### CALIOP_V3.00_Cloudfree_day'
    

    obs = read_obs.read_var(VAR,
                               start_time=START, 
                               stop_time=STOP)
    

    print(obs)
    print(model.downscale_time('monthly'))
    
    #od_regrid = od_obs.regrid(model)
    
    