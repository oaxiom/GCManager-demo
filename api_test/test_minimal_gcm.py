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
    home_path = os.path.join(os.path.expanduser('~'), 'gcm', 'GCMDataDEMO/') # Pre-initialised demo data
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

try:
    man.delete_patient('tester', 'MINIMALGCM')
except AssertionError:
    pass

ret_code, sequence_data_path, safe_patient_id  = man.api.add_new_patient(
    user='tester',
    patient_id='MINIMALGCM',
    sequence_data_id='SQEQID2',
    name='WXY',
    sex='nan',
    age=35,
    institution_sending='Hospital',
    )

gcm = os.path.join(man.script_path, 'demo_data', 'gcms', 'PID.ANALYSISTEST.data.gcm')
print(sequence_data_path)
shutil.copy(gcm, os.path.join(sequence_data_path, 'PID.MINIMALGCM.data.gcm'))
man.set_analysis_complete('MINIMALGCM')

print(man.get_patients_data_table())

pharma_reps = man.api.populate_report_generator('Pharma', 'MINIMALGCM')
for rep in pharma_reps:
    cmd_process(f'man.generate_report("tester", "Pharma", "MINIMALGCM", "{rep}")') # formatting doens't escape string literals

pharma_reps = man.api.populate_report_generator('Risk', 'MINIMALGCM')
for rep in pharma_reps:
    cmd_process(f'man.generate_report("tester", "Risk", "MINIMALGCM", "{rep}")')
