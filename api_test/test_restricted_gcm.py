#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024 中基科生物保留所有权利
#
# Author(s):
# Andrew P. Hutchins,
#

import sys, os, shutil, time, glob
sys.path.append('../')
from libmanager import libmanager, support, VERSION

#from test_common import *

if 'demo' in VERSION:
    home_path = os.path.join(os.path.expanduser('~'), 'GCMDataDEMO/') # Pre-initialised demo data
else:
    print('Only works in DEMO mode')
    sys.exit(-1)

if not os.path.exists(home_path):
    print(f"Panic! Data path {home_path} is missing")
    sys.exit(-1)

def cmd_process(cmd):
    print(f'\n>>> {cmd}')
    res = eval(cmd)

    if len(res) == 0:
        print(None)
        return
    #print(res)
    print(res[0])

man = libmanager.libmanager(home_path=home_path)
man.set_end_type('Doctorend')

########
# Testing;

cmd_process('man.api.populate_report_generator("Pharma", "RESTRICTED1")')

cmd_process('man.api.populate_report_generator("Risk", "RESTRICTED1")')

# Try to force all reports by sending restricted reprot names;
pharma_reps = man.api.populate_report_generator('Pharma', '72210953309787')
print(pharma_reps)
for rep in pharma_reps:
    cmd_process(f"man.generate_report('tester', 'Pharma', 'RESTRICTED1', '{rep}')")

# Try to force all reports by sending restricted reprot names;
pharma_reps = man.api.populate_report_generator('Risk', '72210953309787')
print(pharma_reps)
for rep in pharma_reps:
    cmd_process(f"man.generate_report('tester', 'Risk', 'RESTRICTED1', '{rep}')")
