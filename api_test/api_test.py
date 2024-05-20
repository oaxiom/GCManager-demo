
import sys, os
sys.path.append('../')
from libmanager import libmanager, support, VERSION

script_path = os.path.dirname(os.path.realpath(__file__))
log = support.prepare_logging()

if 'demo' in VERSION:
    home_path = os.path.join(os.path.expanduser('~'), 'GCMDataDEMO/') # Pre-initialised demo data
else:
    log.error('api_test only works in DEMO mode')
    sys.exit(-1)

if not os.path.exists(home_path):
    log.error(f"Panic! Data path {home_path} is missing")
    sys.exit(-1)

man = libmanager.libmanager('Backend', log=log, home_path=home_path)

def cmd_process(cmd):
    print(f'\n>>> {cmd}')
    res = eval(cmd)
    print(res)

########
# Testing;

cmd_process('man.api.populate_patient_list()')
# Expected result:
# [('72210953309787', '何XX', 43, '男', '1'), ('NA12878', '王XX', 22, '男', '1'), ('PATIENTNOTSTARTED', '李XX', 24, '女', '0')]

cmd_process("man.api.export_vcf('72210953309787')")
# Expected Result: (This returns the absolute PATH)
# ../GC_demo/data/PID.72210953309787/72210953309787.recalibrated_snps_recalibrated_indels.vcf.gz
cmd_process("man.api.export_vcf('NA12878')")
# Expected Result: (This returns the absolute PATH)
# ../GC_demo/data/PID.NA12878/NA12878.recalibrated_snps_recalibrated_indels.vcf.gz
cmd_process("man.api.export_vcf('PATIENTNOTSTARTED')")
# Expected Result: (This returns the absolute PATH)
# False

cmd_process("man.api.export_cram('72210953309787')")
# Expected Result: (This returns the absolute PATH)
# False
cmd_process("man.api.export_cram('NA12878')")
# Expected Result: (This returns the absolute PATH)
# False
cmd_process("man.api.export_cram('PATIENTNOTSTARTED')")
# Expected Result: (This returns the absolute PATH)
# False

cmd_process("man.api.populate_patient_data_list()")
# Expected Result:
# [['72210953309787', '7.1Gb', '不', '不', '是'], ['NA12878', '12.0Gb', '不', '不', '是'], ['PATIENTNOTSTARTED', '0Gb', '不', '不', '不']]

cmd_process("man.api.clean_free_space()")
# Expected Result:
# True

cmd_process("man.api.populate_report_generator('pharma')")
# Expected Result:
# [Long table of results]

cmd_process("man.api.get_logs('72210953309787')")
# Expected Result

cmd_process("man.generate_report('72210953309787', 'Stroke')")
# Expected Result:
# /Users/andrew/GCMDataDEMO/data/PID.72210953309787/result.72210953309787.Stroke.html

cmd_process("man.settings.get_doctor_setting('lang')")
# Expected Results:
# 'CN'

cmd_process("man.settings.set_doctor_setting('lang', 'EN')")
cmd_process("man.settings.get_doctor_setting('lang')")
# Expected Result
# 'EN'
