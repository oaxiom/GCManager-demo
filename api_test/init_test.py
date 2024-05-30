#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024
#
# Author(s):
# Andrew P. Hutchins,
#

import sys, os, shutil, uuid
sys.path.append('../')
from libmanager import libmanager, support, VERSION

script_path = os.path.dirname(os.path.realpath(__file__))
log = support.prepare_logging()

if 'demo' in VERSION:
    home_path = os.path.join(os.path.expanduser('~'), 'GCMDataDEMO/') # Pre-initialised demo data
else:
    log.error('init_test only works in DEMO mode')
    sys.exit(-1)

'''
if not os.path.exists(home_path):
    log.error(f"Panic! Data path {home_path} is missing")
    sys.exit(-1)
'''

man = libmanager.libmanager('Doctorend', log=log, home_path=home_path)

man.initialize('admin123', demo=True)
