#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script for intercomparison of optical properties between models and 

Note
----
Bug was fixed
"""
import pyaerocom as pya

### GLOBAL SETTINGS
YEARS = [2010, 2008]


GRIDDED_OBS = 'MODIS6.terra'
        
VAR = 'od550aer'
            
                          

if __name__=="__main__":
    read_gridded_obs = pya.io.ReadGridded(GRIDDED_OBS)
    
    read_gridded_obs.read_individual_years(VAR, YEARS)
    
    d2008 = read_gridded_obs.data_yearly['od550aer'][2008]
    
    d2010 = read_gridded_obs.data_yearly['od550aer'][2010]
    
    print(d2008.suppl_info)
    print(d2010.suppl_info)