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
    log.error('api_test only works in DEMO mode')
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
    print(res)

########
# Testing;
cmd_process("man.generate_report('Pharma', '72210953309787', 'Stroke')")
cmd_process("man.generate_report('Pharma', '72210953309787', 'Diabetes mellitus, type 2')")
cmd_process("man.generate_report('Pharma', '72210953309787', 'Hypertension')")
cmd_process("man.generate_report('Pharma', '72210953309787', '中风')")
cmd_process("man.generate_report('Pharma', 'NA12878', 'qt 间期缩短')")

# Risk:
cmd_process("man.generate_report('Risk', '72210953309787', '克罗恩氏病')")
cmd_process("man.generate_report('Risk', '72210953309787', 'Amyotrophic lateral sclerosis')")
cmd_process("man.generate_report('Risk', '72210953309787', 'Rheumatoid arthritis')")
