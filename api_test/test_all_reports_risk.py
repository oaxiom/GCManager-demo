#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024
#
# Author(s):
# Andrew P. Hutchins,
#

import sys, os
sys.path.append('../')
from libmanager import libmanager, support, VERSION

script_path = os.path.dirname(os.path.realpath(__file__))
log = support.prepare_logging()

if 'demo' in VERSION:
    home_path = os.path.join(os.path.expanduser('~'), 'GCMDataDEMO/') # Pre-initialised demo data
else:
    log.error('Only works in DEMO mode')
    sys.exit(-1)

if not os.path.exists(home_path):
    log.error(f"Panic! Data path {home_path} is missing")
    sys.exit(-1)

man = libmanager.libmanager('Doctorend', log=log, home_path=home_path)

def cmd_process(cmd):
    print(f'\n>>> {cmd}')
    res = eval(cmd)
    if isinstance(res, str):
        lines = res.split('\n')
        if len(lines) > 10:
            print('\n'.join(lines[0:9]))
            return
    elif isinstance(res, list):
        if len(res) > 10:
            print(res[0:9])
            return
    print(res[0])

########
# Testing;
risk_reps = man.api.populate_report_generator('Risk', 'CN')
print(risk_reps)
for rep in risk_reps:
    cmd_process(f"man.generate_report('andrew', 'Risk', '72210953309787', '{rep}')")

