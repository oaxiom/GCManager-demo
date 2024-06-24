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

if 'demo' in VERSION:
    home_path = os.path.join(os.path.expanduser('~'), 'GCMDataDEMO/') # Pre-initialised demo data
else:
    print('Only works in DEMO mode')
    sys.exit(-1)

if not os.path.exists(home_path):
    print(f"Panic! Data path {home_path} is missing")
    sys.exit(-1)

man = libmanager.libmanager(home_path=home_path)
man.set_end_type('Backend')

########
# Testing;

# We need to emulate add_patient parts of FastAPI

# This should be the same logical order as add_new_patient() in FASTAPI
# FASTAPI copies the FASTQs to a temporary location, validates them, and then adds a patient.

# delete the patient if it's already there;
try:
    #man.delete_patient('tester', 'TOOFEWREADS')
    man.delete_patient('tester', 'ANALYSISTEST')
except AssertionError:
    pass

###### A minimal fail;
'''
ret_code, sequence_data_path = man.api.add_new_patient(
    user='tester',
    patient_id='TOOFEWREADS',
    sequence_data_id='SQEQID2',
    name='WXY',
    sex='nan',
    age=35,
    institution_sending='Hospital',
    )

allfiles = glob.glob(os.path.join(man.script_path, 'demo_data', 'fastqs', '*_tiny_*.gz'))
for f in allfiles:
    src_path = os.path.join(man.script_path, 'demo_data', 'fastqs', f)
    dst_path = os.path.join(sequence_data_path, os.path.split(f)[1])
    shutil.copy(src_path, dst_path)
'''
###### A minimal succesful sample;

ret_code, sequence_data_path = man.api.add_new_patient(
    user='tester',
    patient_id='ANALYSISTEST',
    sequence_data_id='SQEQID2',
    name='WXY',
    sex='nan',
    age=35,
    institution_sending='Hospital',
    )

allfiles = glob.glob(os.path.join(man.script_path, 'demo_data', 'fastqs', '*_minimal_*.gz'))
for f in allfiles:
    src_path = os.path.join(man.script_path, 'demo_data', 'fastqs', f)
    dst_path = os.path.join(sequence_data_path, os.path.split(f)[1])
    shutil.copy(src_path, dst_path)

man.add_task('TOOFEWREADS')
man.add_task('ANALYSISTEST')

seconds = 60

while not man.analysis_complete('ANALYSISTEST'):
    man.process_analysis_queue()
    print(man.report_current_analysis_stage())
    print(man.get_patients_data_table())
    #print(man.analysis_queue.currently_processing)
    print(f'Sleeping for {seconds} seconds')
    time.sleep(seconds)
