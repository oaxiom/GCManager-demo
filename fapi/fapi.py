#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024
#
# Author(s):
# Andrew P. Hutchins
#

import sys, os, uuid, datetime
sys.path.append('../')

from libmanager import support, VERSION, libmanager

log = support.prepare_logging()

if 'demo' in VERSION:
    home_path = os.path.join(os.path.expanduser('~'), 'GCMDataDEMO/') # Pre-initialised demo data
else:
    home_path = os.path.join(os.path.expanduser('~'), 'GCMData/')

gcman = libmanager.libmanager('Backend', log=log, home_path=home_path)

# Initialise system if DBs not found
if not os.path.exists(home_path):
    if 'demo' in VERSION:
        gcman.initialize('admin123456', demo=True)
        log.warning('System DB not found. Initializing a blank production DB')
    else: # Production
        gcman.initialize('admin123456')
        log.warning('System DB not found. Initializing a blank DEMO DB')

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login.exceptions import InvalidCredentialsException
from pydantic import UUID4, BaseModel, Field, ConfigDict
from fastapi_login import LoginManager

app = FastAPI()


###### User management

with open(os.path.join(home_path, 'dbs', ".env"), "r") as f:
    gcs = f.read()

class UserCreate(BaseModel):
    username: str
    password: str
    model_config = ConfigDict(from_attributes=True)

class User(UserCreate):
    id: UUID4

user_manager = LoginManager(gcs, token_url='/auth/token')

@user_manager.user_loader()
def get_user(username: str):  # could also be an asynchronous function
    return gcman.users.get(username)

@app.post("/auth/register")
def register(user: UserCreate) -> dict:
    """
    Register a new user.

    """
    if gcman.users.user_exists(user.username):
        raise HTTPException(status_code=400, detail="A user with this username already exists")

    gcman.users.add_user(uuid.uuid4(), user.username, user.password)
    return {'code': 200, 'data': True, 'msg': "Successful registration"}

@app.post('/auth/token')
def login(data: OAuth2PasswordRequestForm = Depends()) -> dict:
    username = data.username
    password = data.password

    if not get_user(username):
        raise InvalidCredentialsException
    if not gcman.users.check_password(username, password):
        raise InvalidCredentialsException

    access_token = user_manager.create_access_token(
        data=dict(sub=username),
        expires=datetime.timedelta(hours=1)
        )

    return {'access_token': access_token, 'token_type': 'bearer'}

@app.post('/auth/change')
def change_password(username:str, newpassword:str, user=Depends(user_manager)) -> dict:

    # old password must be valid because of the logintoken. Ask again anyway?

    if not get_user(username):
        raise InvalidCredentialsException

    ret = gcman.users.change_password(username, newpassword)

    if not ret: # probably old == new
        raise InvalidCredentialsException

    # TODO: invalidate the old token
    # Logout needs to go on the server side if using JWTs.
    # See: https://github.com/MushroomMaula/fastapi_login/issues/82

    return {'code': 200, 'data': True, 'msg': f'Succesfully changed password for user {username}'}

#TODO: Recover password
#Not clear how this is done at the moment; Need internet connection?
#def recover_password()

@app.post("/auth/delete")
def delete(username_to_delete:str, requesting_user=Depends(user_manager)) -> dict:
    """
    Delete a User
    """
    # Check we are admin, and valid
    if not get_user(requesting_user): # I guess impossible to get here, but check anyway
        raise InvalidCredentialsException
    if not gcman.users.is_admin(requesting_user):
        raise HTTPException(status_code=400, detail="The current user is not an admin")

    # Check user_to_delete is valid and not and andin
    if not get_user(username_to_delete):
        raise HTTPException(status_code=400, detail=f"A user with this username {username_to_delete} does not exist")
    if gcman.users.is_admin(username_to_delete):
        raise HTTPException(status_code=400, detail="An admin user cannot be deleted")

    ret = gcman.users.delete_user(username_to_delete)
    if not ret:
        # I guess impossible to get here, but check anyway
        raise HTTPException(status_code=400, detail="Unknown Error")

    return {'code': 200, 'data': ret, 'msg': f"{username_to_delete} succesfully deleted"}

'''
# Logout needs to go on the server side if using JWTs.
# See: https://github.com/MushroomMaula/fastapi_login/issues/82

@app.post('/auth/logout')
def logout(user=Depends(user_manager)):
    username = user
    if not get_user(username): # Should be valid anyway,
        raise InvalidCredentialsException

    return {'code': 200, 'data': True, 'msg': f'User {user} succesfully logged out'}
'''

###### App FAPI

@app.get("/")
async def root():
    return {"message": f"GCManager {VERSION}"}

@app.get('/populate_patient_list/')
def populate_patient_list(user=Depends(user_manager)) -> dict:
    """
    返回患者表，格式为：
    [
    {患者 ID: 'ID',
    姓名: 'NAME',
    年龄: 30,
    性别: 'NAN',
    是否已完成分析?, true}
    ,
    {}, {}, ...
    ]
    搜索患者
    """
    return {'code': 200, 'data': gcman.api.populate_patient_list(), 'msg': None}

@app.get('/populate_report_generator/{mode}')
def populate_report_generator(mode: str, lang: str, user=Depends(user_manager)) -> dict:
    """
    Mode can be one of:

    Pharma = 疾病与用药指导
    ClinVAR = 临床表型相关变异
    Risk = 疾病风险提示

    lang (language) can be one of:
    'EN' English
    'CN' Chinese

    Example request:

    mode = Pharma
    lang = CN

    """
    return {'code': 200, 'data': gcman.api.populate_report_generator(mode, lang), 'msg': None}

@app.get("/patient/export_vcf/{patient_id:str}")
def export_vcf(patient_id: str, user=Depends(user_manager)) -> dict:
    '''
    Returns the PATH to the CRAM file for this patient, of None
    if the CRAM is not avaialable.

    The 保存所选VCF button
    The 保存所选CRAM button

    Example value:
    patient_id = '72210953309787'
    '''
    if not gcman.patient_exists(patient_id): raise HTTPException(status_code=500, detail=f'{patient_id} not found!')
    return {'code': 200, 'data': gcman.api.export_vcf(patient_id), 'msg': None}

@app.get("/patient/export_cram/{patient_id}")
def export_cram(patient_id: str, user=Depends(user_manager)) -> dict:
    '''
    Example value:
    patient_id = '72210953309787'
    '''
    if not gcman.patient_exists(patient_id): raise HTTPException(status_code=500, detail=f'{patient_id} not found!')
    return {'code': 200, 'data': gcman.api.export_cram(patient_id), 'msg': None}

@app.get("/patient/generate_report/{mode}/{patient_id}")
def generate_report(mode: str, patient_id: str, selected_report:str, user=Depends(user_manager)) -> dict:
    '''
    Mode can be one of:

    Pharma = 疾病与用药指导
    ClinVAR = 临床表型相关变异
    Risk = 疾病风险提示

    Example values:
    mode = 'Pharma'
    patient_id = '72210953309787'
    selected_report = '中风'

    '''
    if not gcman.patient_exists(patient_id): raise HTTPException(status_code=500, detail=f'{patient_id} not found!')

    html_filename, html = gcman.api.generate_report(mode, patient_id, selected_report)

    return {'code': 200, 'data': {'html_filename': html_filename, 'html': html}, 'msg': None}

@app.get("/patient/{patient_id}")
def is_patient_id_valid(patient_id: str, user=Depends(user_manager)) -> dict:
    '''

    Test if a patient_id is valid

    Examples =
    '72210953309787' (returns True)
    '88888888' (returns False)

    '''
    ret = gcman.patient_exists(patient_id)
    return {'code': 200, 'data': ret, 'msg': None}

class PatientData(BaseModel):
    patient_id: str = Field(examples=["ANEWPATIENT12345"])
    sequence_data_id: str = Field(examples=["SEQID2345"])
    name: str = Field(examples=["王XX"])
    sex: str = Field(examples=["男"])
    age: int = Field(examples=[30,])
    sequence_data_files: str = Field(examples=["/path/to/data/fastq"])

@app.post('/add_patient')
def add_new_patient(patient_data: PatientData, user=Depends(user_manager)) -> dict:
    '''

    Add a new patient to the database.

    Example data:
    {
      "patient_id": "ANEWPATIENT12345",
      "sequence_data_id": "SEQID2345",
      "name": "王XX",
      "sex": "男",
      "age": 30,
      "sequence_data_files": "/path/to/data/fastq"
    }

    '''
    # Check it doesn't exist already
    ret = gcman.patient_exists(patient_data.patient_id)

    if ret:
        raise HTTPException(status_code=500, detail=f'{patient_data.patient_id} already exists!')

    ret_code = gcman.api.add_new_patient(
        patient_id=patient_data.patient_id,
        sequence_data_id=patient_data.sequence_data_id,
        name=patient_data.name,
        sex=patient_data.sex,
        age=patient_data.age,
        sequence_data_files=patient_data.sequence_data_files
        )

    if not ret_code:
        raise HTTPException(status_code=404, detail=f'Failed to add {patient_data.patient_id}')

    # Check it's valid
    ret = gcman.patient_exists(patient_data.patient_id)

    return {'code': 200, 'data': ret, 'msg': None}

@app.get("/patient/report_current_anaylsis_stage/{patient_id}")
def report_current_anaylsis_stage(patient_id:str, user=Depends(user_manager)) -> dict:
    '''
    Returns the current analysis stage for the indicated data,
    in the form:
    (100, 100, 100, 100, 25, 0, 0, 0)
    Used on the Analysis state page

    返回指示数据的当前分析阶段，
    形式为：
    (100, 100, 100, 100, 25, 0, 0, 0)
    任务分析状态

    Example value:
    patient_id = '72210953309787'
    '''
    if not gcman.patient_exists(patient_id): raise HTTPException(status_code=500, detail=f'{patient_id} not found!')
    return {'code': 200, 'data': gcman.api.report_current_anaylsis_stage(patient_id), 'msg': None}

'''
def delete_patient(self, patient_id:str) -> bool:
'''

@app.get("/patient/export_QC_statistics/{patient_id}")
def export_QC_statistics(patient_id: str, user=Depends(user_manager)) -> dict:
    '''
    Returns the analysis summary as a string.
    Used on the Analysis summary page.

    以字符串形式返回分析摘要。
    用于分析摘要页面。 "分析总结".

    Example value:
    patient_id = '72210953309787'
    '''
    if not gcman.patient_exists(patient_id): raise HTTPException(status_code=500, detail=f'{patient_id} not found!')
    return {'code': 200, 'data': gcman.api.export_QC_statistics(patient_id), 'msg': None}

@app.get("/patient/get_logs/{patient_id}")
def get_logs(patient_id:str, user=Depends(user_manager)) -> dict:
    '''
    Return all the log data.
    Launched by the button 查看分析日志
    and found on the page: 查看日志

    返回所有日志数据。
    通过按钮启动查看分析日志
    在页面上找到：查看日志

    Example value:
    patient_id = '72210953309787'
    '''
    if not gcman.patient_exists(patient_id): raise HTTPException(status_code=500, detail=f'{patient_id} not found!')
    return {'code': 200, 'data': gcman.api.get_logs(patient_id), 'msg': None}

@app.get("/populate_patient_data_list/")
def populate_patient_data_list(user=Depends(user_manager)) -> dict:
    '''

    Return the patient data table which includes the space used,
    wether the data is already packed, CRAM is available? VCF available.
    Used on the page: 患者数据管理

    Data is in the form:

    [
    {
      "patient_id": "72210953309787",
      "space_used": "7.1Gb",
      "data_packed": "不",
      "cram_available": "是",
      "vcf_available": "是"
    },
    {
      "patient_id": "NA12878",
      "space_used": "12.0Gb",
      "data_packed": "不",
      "cram_available": "不",
      "vcf_available": "是"
    },
    ]


    '''
    return {'code': 200, 'data': gcman.api.populate_patient_data_list(), 'msg': None}

@app.get("/system/clean_free_space/")
def clean_free_space(user=Depends(user_manager)) -> dict:
    """

    The button: 清除缓存 on the 患者数据管理 page.

    NOTE: Does nothing in DEMO
    不删除演示版本中的患者

    """
    if not gcman.users.is_admin(user):
        raise InvalidCredentialsException

    return {'code': 200, 'data': gcman.api.clean_free_space(), 'msg': None}

@app.get("/patient/clean_up_analysis/{patient_id}")
def clean_up_analysis(patient_id: str, user=Depends(user_manager)) -> dict:
    '''
    Example value:
    patient_id = '72210953309787'
    '''
    if not gcman.users.is_admin(user):
        raise InvalidCredentialsException

    if not gcman.patient_exists(patient_id): raise HTTPException(status_code=500, detail=f'{patient_id} not found!')
    return {'code': 200, 'data': gcman.api.clean_up_analysis(patient_id), 'msg': None}

@app.get("/patient/convert_bam_to_cram/{patient_id}")
def convert_bam_to_cram(patient_id: str, user=Depends(user_manager)) -> dict:
    '''
    Convert a BAM file to CRAM
    转换所选BAM 成 CRAM

    NOTE: Does nothing in DEMO
    不删除演示版本中的患者

    Example value:
    patient_id = '72210953309787'
    '''
    if not gcman.patient_exists(patient_id): raise HTTPException(status_code=500, detail=f'{patient_id} not found!')
    return {'code': 200, 'data': gcman.api.convert_bam_to_cram(patient_id), 'msg': None}

class Setting(BaseModel):
    key: str = Field(examples=["lang"])
    setting: str = Field(examples=["EN", "CN"])

@app.post('/settings/doctorend/')
def set_system_doctor_setting(setting: Setting, user=Depends(user_manager)) -> dict:
    '''

    Example value:
    {
    "key": "lang",
    "setting": "EN"
    }

    '''
    gcman.api.set_system_doctor_setting(setting.key, setting.setting)
    return {'code': 200, 'data': gcman.api.get_system_doctor_setting(setting.key), 'msg': None}

@app.post('/settings/backend/')
def set_system_backend_setting(setting: Setting, user=Depends(user_manager)) -> dict:
    '''

    Example value:
    {
    "key": "lang",
    "setting": "EN"
    }

    '''
    gcman.api.set_system_backend_setting(setting.key, setting.setting)
    return {'code': 200, 'data': gcman.api.get_system_backend_setting(setting.key), 'msg': None}

@app.get("/settings/get_doctorend/{key}")
def get_system_doctor_setting(key:str, user=Depends(user_manager)) -> dict:
    '''
    Get a system setting on: 系统设置 page
    Example value:
    key = 'lang'
    '''
    return {'code': 200, 'data': gcman.api.get_system_doctor_setting(key), 'msg': None}

@app.get("/settings/get_backend/{key}")
def get_system_backend_setting(key:str, user=Depends(user_manager)) -> dict:
    '''
    Get a system setting on: 系统设置 page
    Example value:
    key = 'lang'
    '''
    return {'code': 200, 'data': gcman.api.get_system_backend_setting(key), 'msg': None}
