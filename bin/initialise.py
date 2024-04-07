#!/usr/bin/env python3
#
# Initialise the databases, pack, etc, designed to be run once to setup a clean installation.
# 
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024 
# 
# Author(s): 
# Andrew P. Hutchins,
#

import sys, os, shutil, logging

sys.path.append('../')
from libmanager import libmanager, VERSION

script_path = os.path.dirname(os.path.realpath(__file__))
home_path = os.path.expanduser('~/GC/') # Production
if 'demo' in VERSION:
    home_path = os.path.join(script_path, 'GC_demo') # Demo data

logging.basicConfig(
    filename = 'initialise.log', # TODO: This is not a safe place to put this...
    filemode = 'w',
    level=logging.DEBUG,
    format='%(levelname)-8s: %(message)s',
    datefmt='%m-%d %H:%M',
    )
log = logging.getLogger(f'GCmanager initialise')

log.info(f'GCManager {VERSION} initialise')
log.info('Copyright 2024 Helixiome, all rights reserved')

log.info("###### Initialising a clean GC")
log.info(f'Home PATH={home_path}')

if 'demo' not in VERSION:
    log.info('Check for existing data directory')
    if os.path.exists(home_path):
        log.error(f'Home PATH={home_path} already exists, will not overwrite!')
        sys.exit(-1)
else:
    if os.path.exists(home_path):
        shutil.rmtree(home_path)

log.info('Setting up directory tree') 
os.mkdir(home_path)
os.mkdir(os.path.join(home_path, 'data'))
os.mkdir(os.path.join(home_path, 'dbs'))

man = libmanager.libmanager(log=log, home_path=home_path)

man._security_check()
res = man._initialize()

if 'demo' in VERSION:
    # Setup two patients, and copy the data from 
    man.setup('72210953309787', 'seq_data1')
    man.setup('NA12878', 'seq_data2')

sys.exit(res)