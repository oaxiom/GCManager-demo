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

sys.path.append('../')
from . import VERSION
from . import initialise_dbs
from . import security

def guid():
    def run(cmd):
        try:
            return subprocess.run(cmd, shell=True, capture_output=True, check=True, encoding="utf-8").stdout.strip()
        except:
            return None

    if sys.platform == 'darwin':
        return run("ioreg -d2 -c IOPlatformExpertDevice | awk -F\\\" '/IOPlatformUUID/{print $(NF-1)}'",)
    if sys.platform == 'win32' or sys.platform == 'cygwin' or sys.platform == 'msys':
        return run('wmic csproduct get uuid').split('\n')[2].strip()
    if sys.platform.startswith('linux'):
        return run('cat /var/lib/dbus/machine-id') or run('cat /etc/machine-id')

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
    os.mkdir(os.path.join(home_path, 'logs'))
    try:
        os.mkdir(backup_path)
    except FileExistsError:
        pass # Never overwrite the backup_path

    initialise_dbs.init_dbs(home_path, script_path, log)

    # set the machine id:
    # Simple to bypass I guess.
    with open(os.path.join(home_path, 'dbs', ".env"), "r") as f:
        gcs = f.read()

    with open(os.path.join(home_path, 'dbs', '.mchne'), "w") as f:
        # combine env and guid() then hash;
        v = security.hash_password(f'{guid()}{gcs}')
        f.write(v)

    if demo:
        initialise_dbs.build_demo_data(gcmanager, home_path, script_path, log)
