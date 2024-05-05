
import sys, os
sys.path.append('../')
from libmanager import libmanager, support, VERSION

script_path = os.path.dirname(os.path.realpath(__file__))
log = support.prepare_logging()

if 'demo' in VERSION:
    home_path = os.path.join(script_path, '..', 'GC_demo') # Pre-initialised demo data
else:
    log.error('api_test only works in DEMO mode')
    sys.exit(-1)

if not os.path.exists(home_path):
    log.error(f"Panic! Data path {home_path} is missing")
    sys.exit(-1)

man = libmanager.libmanager(log=log, home_path=home_path)

########
# Testing;

print(man.api.populate_patient_list())
# Expected result:
# [('72210953309787', '1'), ('NA12878', '1'), ('PATIENTNOTSTARTED', '0')]

print(man.api.export_vcf('72210953309787'))
# Expected Result: (This returns the absolute PATH)
# ../GC_demo/data/PID.72210953309787/72210953309787.recalibrated_snps_recalibrated_indels.vcf.gz

print(man.api.populate_patient_data_list())
# Expected Result:
# [['72210953309787', '7.1Gb', '不', '不', '是'], ['NA12878', '12.0Gb', '不', '不', '是'], ['PATIENTNOTSTARTED', '0Gb', '不', '不', '不']]

print(man.clean_free_space())
# Expected Result:
# True
