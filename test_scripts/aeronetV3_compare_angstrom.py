#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 24 14:48:03 2018

@author: jonasg
"""
import pyaerocom as pya

VARS = ['ang4487aer', 'ang4487aer_calc', 'od550aer']
FILTER_NAME = 'WORLD-noMOUNTAINS'

reader = pya.io.ReadUngridded()
reader.logger.setLevel('CRITICAL')
data = reader.read_dataset(pya.const.AERONET_SUN_V3L2_AOD_DAILY_NAME,
                           vars_to_retrieve=VARS)

regfilter = pya.Filter(FILTER_NAME)
data = regfilter(data)

