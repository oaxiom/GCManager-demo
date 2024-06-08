#
# Initialise the databases, pack, etc, designed to be run once to setup a clean installation.
#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024
#
# Author(s):
# Andrew P. Hutchins,
#

import sys, os, shutil

sys.path.append('../')
from . import VERSION
from . import initialise_dbs

def initialize_system(gcmanager, end_type, log, script_path, home_path, backup_path, demo):
    assert end_type in ('Doctorend', 'Backend'), f'{end_type} must be one of Doctorend or Backend'

    log.info(f'GCManager {VERSION} initialise')
    log.info('Copyright 2024 Helixiome, all rights reserved')
    log.info("###### Initialising a clean GC")

    if demo:
        log.info('Initialising DEMO version')

    log.info(f'Home DBPATH={home_path}')

    if not demo:
        log.info('Check for existing data directory')
        if os.path.exists(home_path):
            log.error(f'Home DBPATH={home_path} already exists, will not overwrite!')
            sys.exit(-1)
        log.info(f'Started production DB at DBPATH={home_path}')

    else:
        # if demo, then overwrite existing
        if os.path.exists(home_path):
            shutil.rmtree(home_path)
        log.info('Demo version overwrote existing tree')

    log.info('Setting up directory tree')
    os.mkdir(home_path)
    os.mkdir(os.path.join(home_path, 'data'))
    os.mkdir(os.path.join(home_path, 'dbs'))
    try:
        os.mkdir(backup_path)
    except FileExistsError:
        pass # Never overwrite the backup_path

    initialise_dbs.init_dbs(home_path, script_path, log)

    if demo:
        initialise_dbs.build_demo_data(gcmanager, home_path, script_path, log)


