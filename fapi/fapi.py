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
    return {"message": f"GCManager {VERSION}"}

@app.get('/populate_patient_list/')
def populate_patient_list() -> dict:
    return {'code': 200, 'data': man.api.populate_patient_list(), 'msg': None}

@app.get('/populate_report_generator/{mode:str}/{lang:str}')
def populate_report_generator(mode: str, lang: str) -> dict:
    """
    Mode can be one of:

    Pharma = 疾病与用药指导
    ClinVAR = 临床表型相关变异
    Risk = 疾病风险提示

    lang (language) can be one of:
    'EN' English
    'CN' Chinese
    """
    return {'code': 200, 'data': man.api.populate_report_generator(mode, lang), 'msg': None}

@app.get("/export_vcf/{patient_id: str}")
def export_vcf(self, patient_id: str) -> str:
    return {'code': 200, 'data': man.api.export_vcf(), 'msg': None}

@app.get("/export_cram/{patient_id: str}")
def export_cram(self, patient_id: str) -> str:
    return {'code': 200, 'data': man.api.export_cram(), 'msg': None}

@app.get("/generate_report/{mode}/{patient_id: str}/{selected_report}")
def generate_report(self, mode: str, patient_id: str, selected_report:str) -> str:
    return {'code': 200, 'data': man.api.generate_report(), 'msg': None}

'''
@app.get("/")
def add_new_patient(self,
        patient_id: str,
        sequence_data_id: str,
        name: str,
        sex: str,
        age: int,
        sequence_data_files: str) -> bool:
'''

@app.get("/report_current_anaylsis_stage/{patient_id: str}")
def report_current_anaylsis_stage(self, patient_id:str):
    return {'code': 200, 'data': man.api.report_current_anaylsis_stage(), 'msg': None}

'''
@app.get("/")
def delete_patient(self, patient_id:str) -> bool:
'''

@app.get("/export_QC_statistics/{patient_id: str}")
def export_QC_statistics(self, patient_id: str) -> str:
    return {'code': 200, 'data': man.api.export_QC_statistics(), 'msg': None}

@app.get("/get_logs/{patient_id: str}")
def get_logs(self, patient_id:str) -> str:
    return {'code': 200, 'data': man.api.get_logs(), 'msg': None}

@app.get("/populate_patient_data_list/")
def populate_patient_data_list(self) -> str:
    return {'code': 200, 'data': man.api.populate_patient_data_list(), 'msg': None}

@app.get("/clean_free_space/")
def clean_free_space(self) -> bool:
    return {'code': 200, 'data': man.api.clean_free_space(), 'msg': None}

@app.get("/clean_up_analysis/{patient_id: str}")
def clean_up_analysis(self, patient_id: str) -> bool:
    return {'code': 200, 'data': man.api.clean_up_analysis(), 'msg': None}

@app.get("/convert_bam_to_cram/")
def convert_bam_to_cram(self) -> bool:
    return {'code': 200, 'data': man.api.convert_bam_to_cram(), 'msg': None}

'''
def set_system_doctor_setting(self, key:str, value:str) -> bool:
'''

@app.get("/get_system_doctor_setting/{key:str}")
def get_system_doctor_setting(self, key:str) -> str:
    return {'code': 200, 'data': man.api.get_system_doctor_setting(key), 'msg': None}

'''
def set_system_backend_setting(self, key:str, value:str) -> bool:
'''

@app.get("/get_system_backend_setting/{key: str}")
def get_system_backend_setting(self, key:str) -> str:
    return {'code': 200, 'data': man.api.get_system_backend_setting(key), 'msg': None}
