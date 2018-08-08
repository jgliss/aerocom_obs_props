#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script for intercomparison of optical properties between models and 
"""
import helpers as helpers
### GLOBAL SETTINGS

RUN_EVAL = 0

YEARS = [2010]

VARS = ['od550aer', 
        'od550gt1aer', 
        'od550lt1aer'
        'abs550aer']

MODEL_LIST = ['CAM6-Oslo_NF2kNucl_7jun2018AK',
              'OsloCTM2_INSITU',
              'TM5_AP3-CTRL2016',
              'TM5_AP3-INSITU']

### Paths and directories
MODEL_INFO_FILE = ('/lustre/storeA/project/aerocom/'
                   'aerocom-users-database/AEROCOM-PHASE-III/reference-list')
OUT_DIR = './output/'

if __name__=="__main__":
    helpers.print_file(MODEL_INFO_FILE)
    if RUN_EVAL:
        raise NotImplementedError