#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024
#
# Author(s):
# Andrew P. Hutchins,
#

import sys, os, shutil, uuid
sys.path.append('../')
from libmanager import libmanager, support, VERSION, security

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
    print(res)

os.remove(os.path.join(man.data_path, '.mac'))

cmd_process('man._already_registered()')

# Simulate registering for the first time;
ID = 'ABCDEFGHIJKLMMO'

# On the front end;
#k = man.get_public_key() # front end will deal with this
pubk = security.load_public_key(os.path.join(man.script_path, 'keys', 'demo.public_key.pem')) # emulate by getting the key directly
enc = security.encrypt(ID.encode(), pubk)

# Done in GCMan
cmd_process('man.register_frontend(enc)')

# Now check on start up
# Done on front end:
k = security.load_public_key(os.path.join(man.script_path, 'keys', 'demo.public_key.pem'))
enc = security.encrypt(ID.encode(), k)

# Done in GCMan
cmd_process('man.check_frontend_registration(enc)')
cmd_process('man._already_registered()')
