#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024 中基科生物保留所有权利
#
# Author(s):
# Andrew P. Hutchins,
#

import sys, os, shutil, uuid, base64
sys.path.append('../')
from libmanager import libmanager, support, VERSION, security

home_path = os.path.join(os.path.expanduser('~'), 'gcm', 'GCMDataDEMO/')

man = libmanager.libmanager(home_path=home_path)
man.set_end_type('Doctorend')

print(man.get_error('del_user_not_exist')) # unformatted;
print(man.get_error('del_user_not_exist', username_to_delete='demo_test'))
