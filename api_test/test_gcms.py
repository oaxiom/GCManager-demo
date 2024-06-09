#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024
#
# Author(s):
# Andrew P. Hutchins,
#

import sys, os, shutil, uuid
sys.path.append('../')
from libmanager import libmanager, support, VERSION

home_path = os.path.join(os.path.expanduser('~'), 'GCMDataDEMO/')

man = libmanager.libmanager(home_path=home_path)
man.set_end_type('Doctorend')

# I think it's not actually used though...
print(man.get_logs('tester', '72210953309787'))
