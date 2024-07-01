#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024 中基科生物保留所有权利
#
# Author(s):
# Andrew P. Hutchins,
#

import sys, os, shutil, uuid, time
sys.path.append('../')
from libmanager import libmanager, support, VERSION

if 'demo' in VERSION:
    home_path = os.path.join(os.path.expanduser('~'), 'gcm', 'GCMDataDEMO/') # Pre-initialised demo data
else:
    print('api_tests only work in DEMO mode')
    sys.exit(-1)

if not os.path.exists(home_path):
    print(f"Panic! Data path {home_path} is missing")
    sys.exit(-1)

man = libmanager.libmanager(home_path=home_path)

man.set_end_type('Doctorend')

# Must be a blank DB for this:
if os.path.exists(home_path):
    shutil.rmtree(home_path)
#os.mkdir(home_path)
#os.mkdir(os.path.join(home_path, 'data'))
#os.mkdir(os.path.join(home_path, 'dbs'))
#os.mkdir(os.path.join(home_path, 'logs'))
man.initialize('admin123', demo=True)

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
    print(res)

########
# Testing;
cmd_process('man.add_patient("tester", "ANEWPATIENT", "SEQIDNEW", "张XX", "女", 50, "PATH/TO/SEQ")')
cmd_process("man.get_patients_table('tester')")

time.sleep(5)

cmd_process("man.delete_patient('tester', 'ANEWPATIENT')")
cmd_process("man.get_patients_table('tester')")
