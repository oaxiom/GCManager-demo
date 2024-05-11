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
from libmanager import libmanager, VERSION, logger

log = logger.logger()

script_path = os.path.dirname(os.path.realpath(__file__))
home_path = os.path.expanduser('~/GCMData/') # Production

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
    # if demo, then overwrite existing
    if os.path.exists(home_path):
        shutil.rmtree(home_path)

log.info('Setting up directory tree')
os.mkdir(home_path)
os.mkdir(os.path.join(home_path, 'data'))
os.mkdir(os.path.join(home_path, 'dbs'))

man = libmanager.libmanager(log=log, home_path=home_path)

man._security_check()

if 'demo' not in VERSION:
    res = man._initialize()
else:
    res = man._initialize(True)

sys.exit(res)
