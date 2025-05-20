# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 16:10:15 2024

@author: JacoPbass

obtained from https://stackoverflow.com/a/65600859
"""
import os

# Just add or remove values to this list based on the imports you don't want
excluded_modules = [
    'tensorflow',
    'torch',
    'jupyterlab',
    'notebook',
    'jedi',
    'PIL',
    'psutil',
    'ipython',
    'tcl',
    'tcl8',
    'tornado'
]

append_string = ''
for mod in excluded_modules:
    append_string += f' --exclude-module {mod}'

# Run the shell command with all the exclude module parameters
os.system(f'pyinstaller MRI_Areas.py --noconfirm {append_string}')
