
import sys, os
sys.path.append('../')
from libmanager import libmanager, support, VERSION

script_path = os.path.dirname(os.path.realpath(__file__))
log = support.prepare_logging()

if 'demo' in VERSION:
    home_path = os.path.expanduser('~/GCMDataDEMO/') # Pre-initialised demo data
else:
    log.error('api_test only works in DEMO mode')
    sys.exit(-1)

if not os.path.exists(home_path):
    log.error(f"Panic! Data path {home_path} is missing")
    sys.exit(-1)

man = libmanager.libmanager(log=log, home_path=home_path)

def cmd_process(cmd):
    print(f'\n>>> {cmd}')
    res = eval(cmd)
    print(res)

########
# Testing;

cmd_process('man.api.populate_patient_list()')
# Expected result:
# [('72210953309787', '1'), ('NA12878', '1'), ('PATIENTNOTSTARTED', '0')]

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

cmd_process("man.api.populate_report_generator()")
# Expected Result:
# [('DT00001', 'Stroke', '中风'), ('DT00002', 'Type 1 Diabetes (T1D)', '1 型糖尿病 (T1D)'), ('DT00003', 'Type 2 Diabetes (T2D)', '二型糖尿病（T2D）'), ('DT00004', 'Amyotrophic Lateral Sclerosis (ALS)', '肌萎缩侧索硬化症（ALS）'), ('DT00006', 'Chronic Obstructive Pulmonary Disease (COPD)', '慢性阻塞性肺病（COPD）'), ('DT00007', 'Chronic Obstructive Pulmonary Disease (COPD) in never smokers', '从不吸烟者的慢性阻塞性肺病（COPD）'), ('DT00008', 'Rheumatoid Arthritis (RA)', '类风湿性关节炎（RA）'), ('DT00009', "Parkinson's Disease (PD)", '帕金森病（PD）'), ('DT00010', "Crohn's Disease (CD)", '克罗恩病（CD）'), ('DT00011', 'Hypertension', '高血压'), ('DT00012', 'Nasopharyngeal Carcinoma', '鼻咽癌'), ('DT00013', 'Systemic Lupus Erythematosus (SLE)', '系统性红斑狼疮（SLE）'), ('DT00014', 'Idiopathic Pulmonary Fibrosis (IPF)', '特发性肺纤维化（IPF）'), ('DT00015', 'Osteoarthritis (OA)', '骨关节炎（OA）'), ('DT00016', 'Ulcerative Colitis', '溃疡性结肠炎')]

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
