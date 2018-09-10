#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 24 14:48:03 2018

@author: jonasg
"""
import pyaerocom as pya
import iris
import numpy as np

MODEL = 'INCA-BCext_CTRL2016-PD'
START =2010
VAR = 'ang4487aer'

if __name__=='__main__':
    ### Model data
    reader = pya.io.ReadGridded(MODEL)
    
    od443aer = reader.read_var('od443aer').grid
    od550aer = reader.read_var('od550aer').grid
    od865aer = reader.read_var('od865aer').grid
    
    r = od443aer / od865aer
    logr = iris.analysis.maths.log(r)
    
    wvl_r = np.log(443/865)
    
    ang4487aer = iris.analysis.maths.divide(logr, wvl_r)*-1
    
    ang4487aer_ = float(ang4487aer[0,0,0].data)
    
    od443aer_ = float(od443aer[0,0,0].data)
    od865aer_ = float(od865aer[0,0,0].data)
    
    od550aer_calc = od443aer_ * (443 / 550)**ang4487aer_
    
    od550aer_ = float(od550aer[0,0,0].data)
    
    diff = od550aer_ - od550aer_calc
    
    #model = reader.read_var(VAR, start_time=START)
    
    