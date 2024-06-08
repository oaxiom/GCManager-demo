#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024
#
# Author(s):
# Andrew P. Hutchins,
#

import sys, os, time
sys.path.append('../')
from libmanager import libmanager, support, VERSION

log = support.prepare_logging()

if 'demo' in VERSION:
    home_path = os.path.join(os.path.expanduser('~'), 'GCMDataDEMO/') # Pre-initialised demo data
else:
    log.error('api_test only works in DEMO mode')
    sys.exit(-1)

if not os.path.exists(home_path):
    log.error(f"Panic! Data path {home_path} is missing")
    sys.exit(-1)

man = libmanager.libmanager(log=log, home_path=home_path)
man.set_end_type('Doctorend')

man._check_if_its_time_to_backup_db()
