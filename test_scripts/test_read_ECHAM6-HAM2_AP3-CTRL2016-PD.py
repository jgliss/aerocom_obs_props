#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 24 14:48:03 2018

@author: jonasg
"""
import pyaerocom as pya


MODEL = 'ECHAM6-HAM2_AP3-CTRL2016-PD'

OBS = 'AeronetSunV3Lev2.daily'

VAR = 'od550aer'

START=2010

if __name__=='__main__':
    pya.change_verbosity('critical')
    reader = pya.io.ReadGridded(MODEL)
    obsr = pya.io.ReadUngridded(OBS)
    
    model = reader.read_var(VAR, start_time=START)
    obs = obsr.read(vars_to_retrieve=VAR)

    for i, f in enumerate(reader.files):
        data = pya.io.iris_io.load_cube_custom(f, grid_io=pya.const.GRID_IO)
        print(i)
        print(data.coord('longitude').points.min())
        print(data.coord('longitude').points.max())
        
    
    coll = pya.collocation.collocate_gridded_ungridded_2D(model, 
                                                          obs,
                                                          ts_type='monthly')
    
    ax = coll.plot_scatter()
    