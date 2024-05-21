#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024
#
# Author(s):
# Andrew P. Hutchins
#

import sys, os
sys.path.append('../')

from libmanager import support, VERSION, libmanager

log = support.prepare_logging()
if 'demo' in VERSION:
    home_path = os.path.join(os.path.expanduser('~'), 'GCMDataDEMO/') # Pre-initialised demo data
else:
    sys.exit(-1)
if not os.path.exists(home_path):
    log.error(f"Panic! Data path {home_path} is missing")
    sys.exit(-1)
man = libmanager.libmanager('Backend', log=log, home_path=home_path)

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get('/populate_patient_list/')
def populate_patient_list() -> dict:
    return {'code': 200, 'data': man.api.populate_patient_list(), 'msg': None}
