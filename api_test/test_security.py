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

try:
    os.remove(os.path.join(man.data_path, '.mac'))
except FileNotFoundError:
    pass

def b64e(s):
    return base64.b64encode(s).decode("utf-8")

def b64d(s):
    return base64.b64decode(s)

# Simulate registering for the first time;
ID = 'ABCDEFGHIJKLMMO'
'''
# First test GCManager works fine:
cmd_process('man._already_registered()')
pubk = security.load_public_key(os.path.join(man.script_path, 'keys', 'demo.public_key.pem')) # emulate by getting the key directly
enc = security.encrypt(ID.encode(), pubk)
cmd_process('man.register_frontend(enc)')
cmd_process('man.check_frontend_registration(enc)')
cmd_process('man._already_registered()')
'''
try:
    os.remove(os.path.join(man.data_path, '.mac'))
except FileNotFoundError:
    pass

print()
# Now emulate the same process, but using base64 encoded strings:
cmd_process('man._already_registered()')

# On front end, they send as base64 encoded string
pubk = security.load_public_key(os.path.join(man.script_path, 'keys', 'demo.public_key.pem')) # emulate by getting the key directly
enc = security.encrypt(ID.encode(), pubk)

print('Original encoding')
print(enc)
print()

print('b64 encoding')
enc = b64e(enc)
print(isinstance(enc, str))
print(enc)
print()

cmd_process('man.register_frontend(enc)')

cmd_process('man.check_frontend_registration(enc)')
