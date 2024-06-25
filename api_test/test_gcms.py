#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024 中基科生物保留所有权利
#
# Author(s):
# Andrew P. Hutchins,
#

import sys, os, shutil, uuid
sys.path.append('../')
from libmanager import libmanager, support, VERSION, gcms

home_path = os.path.join(os.path.expanduser('~'), 'GCMDataDEMO/')

man = libmanager.libmanager(home_path=home_path)
man.set_end_type('Doctorend')

def cmd_process(cmd):
    print(f'\n>>> {cmd}')
    res = eval(cmd)

    if isinstance(res, str):
        lines = res.split('\n')
        if len(lines) > 10:
            print('\n'.join(lines[0:9]))
            print(f'{len(lines):,} in total')
            return
    elif isinstance(res, list):
        if len(res) > 10:
            print(res[0:9])
            return
    print(res[0])

cmd_process("man.get_logs('tester', 'NA12878')")

print(man.get_qc('tester', 'NA12878'))
print(man.get_qc('tester', '72210953309787'))

gcm = gcms.gcm_file(os.path.join(man.data_path, f'PID.72210953309787', f'PID.72210953309787.data.gcm'), logger=man.log)
print(gcm.get_pharma())
print(gcm.get_risk())
#print(gcm.get_clinvar())

# Test conversion of a VCF to a GCM:

gcm = gcms.dbsnp_vcf_to_gcm(man.script_path, '../demo_data/vcfs/VCFANALYSIS.gatk.dbsnp.vcf.gz', '../demo_data/gcms/VCFANALYSIS.data.gcm')
gcm.logger = man.log
print(gcm.get_qc())
print(gcm.get_logs())
print(gcm.get_pharma())
print(gcm.get_risk())
