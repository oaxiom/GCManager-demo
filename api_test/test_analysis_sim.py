#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024 中基科生物保留所有权利
#
# Author(s):
# Andrew P. Hutchins,
#

import sys, os, time
sys.path.append('../')
from libmanager import libmanager, support, VERSION

if 'demo' in VERSION:
    home_path = os.path.join(os.path.expanduser('~'), 'gcm', 'GCMDataDEMO/') # Pre-initialised demo data
else:
    print('api_test only works in DEMO mode')
    sys.exit(-1)

if not os.path.exists(home_path):
    print(f"Panic! Data path {home_path} is missing")
    sys.exit(-1)

man = libmanager.libmanager(home_path=home_path)
man.set_end_type('Backend')

########
# Testing;

# 72210953309787 is complete;
# PATIENTNOTSTARTED is incomplete

man.delete_patient('tester', 'PATIENTNOTSTARTED')
man.add_patient("tester", "PATIENTNOTSTARTED", "SEQIDNEW", "张XX", "女", 50, "PATH/TO/SEQ")

print(man.report_current_analysis_stage('72210953309787'))

print(man.report_current_analysis_stage('PATIENTNOTSTARTED'))

