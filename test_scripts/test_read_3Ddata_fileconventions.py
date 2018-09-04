#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 24 14:48:03 2018

@author: jonasg
"""
import pyaerocom as pya
from warnings import filterwarnings
import iris
import xarray


if __name__=='__main__':
    filterwarnings('ignore')
### AEROCOM 2
    d1 = '/lustre/storeA/project/aerocom/aerocom-users-database/AEROCOM-PHASE-II/OsloCTM2.A2.CTRL/renamed/'
    
    f11 = 'aerocom.OsloCTM2.A2.CTRL.monthly.abs5503Daer.2006.nc'
    f12 = 'aerocom.OsloCTM2.A2.CTRL.daily.od550oa.2006.nc'
    
    d11 = iris.load(d1 + f11)
    d12 = iris.load(d1 + f12)
    
### AEROCOM 3
    d2 = '/lustre/storeA/project/aerocom/aerocom-users-database/AEROCOM-PHASE-III/TM5_AP3-INSITU/renamed/'
    
    f21 = 'aerocom3_TM5_AP3-INSITU_vmrch4_ModelLevel_2010_monthly.nc'
    f22 = 'aerocom3_TM5_AP3-INSITU_ec870dryaer_Surface_2010_hourly.nc'
    f23 = 'aerocom3_TM5_AP3-INSITU_loadbc_Column_2010_monthly.nc'
    
    d21 = iris.load(d2 + f21)
    d22 = iris.load(d2 + f22)
    d23 = iris.load(d2 + f23)
    
    data = [d11, d12, d21, d22, d23]
    
    #reader = pya.io.ReadGridded('TM5_AP3-INSITU')
    #dat = reader.read_var('vmrch4')
    
    for i, cubes in enumerate(data):
        print('At iter {}'.format(i))
        for d in cubes:
            print('\n')
            print(d.var_name)
            print(d.shape)
            print(d.ndim)
            print([c.standard_name for c in d.dim_coords])
            print([c.var_name for c in d.dim_coords])
        
        print('\n\n')
        
    print(d11)
    
    ds11 = xarray.open_dataset(d1 + f11)
    ds21 = xarray.open_dataset(d2 + f21)
    
    data11 = pya.GriddedData(d1+f11, var_name='abs5503Daer')
    data21 = pya.GriddedData(d2+f21, var_name='vmrch4')
    
    print(ds21)