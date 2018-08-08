#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  7 08:19:06 2018

@author: jonasg
"""
import os


def print_file(file_path):
    if not os.path.exists(file_path):
        raise IOError('Model info file not found...')
    with open(file_path) as f:
        for line in f:
            if line.strip():
                print(line)
                