#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024 中基科生物保留所有权利
#
# Author(s):
# Andrew P. Hutchins,
#

import sys, os
sys.path.append('../')
from libmanager import libmanager, support, VERSION

if 'demo' in VERSION:
    home_path = os.path.join(os.path.expanduser('~'), 'GCMDataDEMO/') # Pre-initialised demo data
else:
    print('api_test only works in DEMO mode')
    sys.exit(-1)

if not os.path.exists(home_path):
    print(f"Panic! Data path {home_path} is missing")
    sys.exit(-1)

man = libmanager.libmanager(home_path=home_path)
man.set_end_type('Doctorend')

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

cmd_process("man.api.export_vcf('72210953309787')")
# Expected Result: (This returns the absolute PATH)
# ../GC_demo/data/PID.72210953309787/72210953309787.recalibrated_snps_recalibrated_indels.vcf.gz
cmd_process("man.api.export_vcf('NA12878')")
# Expected Result: (This returns the absolute PATH)
# ../GC_demo/data/PID.NA12878/NA12878.recalibrated_snps_recalibrated_indels.vcf.gz
#cmd_process("man.api.export_vcf('PATIENTNOTSTARTED')")
# Expected Result:
# False

cmd_process("man.settings.set_doctor_setting('lang', 'EN')")
cmd_process("man.settings.get_doctor_setting('lang')")
# Expected Result
# 'EN'

cmd_process("man.api.populate_report_generator('Pharma')")