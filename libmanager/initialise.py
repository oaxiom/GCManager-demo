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
import subprocess
import logging

sys.path.append('../')
from . import VERSION
from . import initialise_dbs
from . import security
from . import utils
from . import logger

def initialize_system(gcmanager, end_type, log, script_path, home_path, backup_path, demo):
    assert end_type in ('Doctorend', 'Backend'), f'{end_type} must be one of Doctorend or Backend'

    if not demo:
        #log.info('Check for existing data directory')
        if os.path.exists(home_path):
            log.error(f'Home DBPATH={home_path} already exists, will not overwrite!')
            sys.exit(-1)
        #log.info(f'Started production DB at DBPATH={home_path}')

    else:
        # if demo, then overwrite existing
        if os.path.exists(home_path):
            shutil.rmtree(home_path)
        #log.info('Demo version overwrote existing tree')

    os.mkdir(home_path)
    os.mkdir(os.path.join(home_path, 'logs'))
    os.mkdir(os.path.join(home_path, 'data'))
    os.mkdir(os.path.join(home_path, 'dbs'))
    try:
        os.mkdir(backup_path)
    except FileExistsError:
        pass # Never overwrite the backup_path

    # Rebuild the log system to save to a file
    file_handler = logging.FileHandler(os.path.join(home_path, 'logs', 'gcman.log'))
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M:%S',)
    file_handler.setFormatter(formatter)

    log.addHandler(file_handler)

    #log = logger.logger(os.path.join(home_path, 'logs'))

    # I can attach the full logger now:
    log.info(f'GCManager {VERSION} initialise')
    log.info('Copyright 2024 Helixiome, all rights reserved')
    log.info("###### Initialising a clean GC")

    if demo:
        log.info('Initialising DEMO version')

    log.info(f'Home DBPATH={home_path}')
    log.info('Set up directory tree')

    if not demo:
        log.info('Check for existing data directory')
        log.info(f'Started production DB at DBPATH={home_path}')
    else:
        log.info('Demo version overwrote existing tree')

    initialise_dbs.init_dbs(home_path, script_path, log)

    # set the machine id:
    with open(os.path.join(home_path, 'dbs', '.mchne'), "w") as f:
        v = security.hash_password(utils.guid())
        f.write(v)

    if demo:
        initialise_dbs.build_demo_data(gcmanager, home_path, script_path, log)

    return log
