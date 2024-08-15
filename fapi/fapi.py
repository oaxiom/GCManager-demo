#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024 中基科生物保留所有权利
#
# Author(s):
# Andrew P. Hutchins
#

import sys, os, uuid, datetime
import time
import logging
import shutil
import aiofiles
import base64
from contextlib import asynccontextmanager
import asyncio
import binascii
import  _pickle
sys.path.append('../')

from libmanager import support, VERSION, libmanager
from contextlib import asynccontextmanager

logging.getLogger("multipart").setLevel(logging.ERROR)

if 'demo' in VERSION:
    home_path = os.path.join(os.path.expanduser('~'), 'gcm', 'GCMDataDEMO/') # Pre-initialised demo data
else:
    home_path = os.path.join(os.path.expanduser('~'), 'gcm', 'GCMData/')

gcman = libmanager.libmanager(home_path=home_path)
log = gcman.log

# Initialise system if DBs not found
if not os.path.exists(home_path):
    if 'demo' in VERSION:
        gcman.initialize('admin123', demo=True)
        log.warning('System DB not found. Initializing a blank DEMO DB')
    else: # Production
        gcman.initialize('admin123')
        log.warning('System DB not found. Initializing a blank production DB')

gcman.check_security()

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login.exceptions import InvalidCredentialsException
from fastapi.concurrency import run_in_threadpool
from typing_extensions import Annotated
from pydantic import UUID4, BaseModel, Field, ConfigDict
from fastapi_login import LoginManager
from fastapi.responses import HTMLResponse
from urllib.parse import unquote
from typing import Optional, List

#gcman.set_end_type('Doctorend')

async def check_backups(seconds):
    while True:
        gcman.check_if_its_time_to_backup_db()
        await asyncio.sleep(seconds)

async def check_security(seconds):
    while True:
        ret = gcman.check_security()
        if not ret:
            raise HTTPException(status_code=400, detail=gcman.get_error('fail_sec_check_mac'))
        await asyncio.sleep(seconds)

async def process_analysis_queue(seconds):
    while True:
        if gcman.end_type == 'Backend':
            gcman.process_analysis_queue()
        await asyncio.sleep(seconds)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run at startup
    asyncio.create_task(check_backups(60*60*2)) # Once every two hours, this does not force a DB backup, it only checks if one is required
    asyncio.create_task(check_security(60*60)) # Once an hour
    asyncio.create_task(process_analysis_queue(60*1)) # Every minute;
    yield

app = FastAPI(lifespan=lifespan)

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
        raise HTTPException(status_code=400, detail=gcman.get_error('user_exists'))

    gcman.users.add_user(uuid.uuid4(), user.username, user.password)
    return {'code': 200, 'data': (user.username, user.password), 'msg': gcman.get_error('user_success_registration')}

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
        expires=datetime.timedelta(hours=12)
        )

    return {'access_token': access_token, 'token_type': 'bearer'}

@app.post('/auth/change')
def change_password(username:str, newpassword:str, oldpassword:str = None, requesting_user=Depends(user_manager)) -> dict:

    if not gcman.users.user_exists(username):
        raise HTTPException(status_code=400, detail=gcman.get_error('user_not_exists', username=username))

    if not gcman.users.is_admin(requesting_user):
        # We are not an admin. Check the old password;
        if not oldpassword:
            raise HTTPException(status_code=400, detail=gcman.get_error('old_password_reqd'))
        if not gcman.users.check_password(username, oldpassword):
            raise HTTPException(status_code=400, detail=gcman.get_error('incorrect_old_pass'))
    else: # We are the admin
        if username == requesting_user:
            # We are trying to change our own password.
            # We will need the old password
            if not oldpassword:
                raise HTTPException(status_code=400, detail=gcman.get_error('old_password_reqd'))
            if not gcman.users.check_password(username, oldpassword):
                raise HTTPException(status_code=400, detail=gcman.get_error('incorrect_old_pass'))
        # We are not changing our own password, must be someone else's so no need oldpassword

    # If an admin, we don't need the oldpassword.
    ret = gcman.users.change_password(username, newpassword)

    if not ret: # probably old == new
        raise HTTPException(status_code=400, detail=gcman.get_error('oldpass_is_newpass'))

    # Logout needs to go on the server side if using JWTs.
    # See: https://github.com/MushroomMaula/fastapi_login/issues/82

    gcman.log.info(f'{requesting_user} changed password for {username}')
    return {'code': 200, 'data': True, 'msg': gcman.get_error('changed_pass', username=username)}

@app.post("/auth/delete")
def delete(username_to_delete:str, requesting_user=Depends(user_manager)) -> dict:
    """
    Delete a User
    """
    # Check we are admin, and valid
    if not gcman.users.is_admin(requesting_user):
        raise HTTPException(status_code=400, detail=gcman.get_error('user_not_admin'))

    if not get_user(requesting_user): # I guess impossible to get here, but check anyway
        # If a non-admin user gets here, something strange going on.
        # Invalid Credentials will also force log off that user.
        raise InvalidCredentialsException

    # Check user_to_delete is valid and not and admin
    if not get_user(username_to_delete):
        raise HTTPException(status_code=400, detail=gcman.get_error('del_user_not_exist', username_to_delete=username_to_delete))
    if gcman.users.is_admin(username_to_delete):
        raise HTTPException(status_code=400, detail=gcman.get_error('cannot_del_admin'))

    ret = gcman.users.delete_user(username_to_delete)
    if not ret:
        # I guess impossible to get here, but check anyway
        raise HTTPException(status_code=400, detail=gcman.get_error('unk'))

    return {'code': 200, 'data': ret, 'msg': gcman.get_error('user_deleted', username_to_delete=username_to_delete)}

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
    return {"message": f"GCManager {VERSION} ; end_type={gcman.end_type}"}

@app.post('/set_end_type/')
def set_end_type(end_type: str) -> dict:
    """
    Jut here for internal testing
    """
    assert end_type in ('Doctorend', 'Backend'), f'{end_type} must be one of Doctorend or Backend'

    return {'code': 200, 'data': gcman.set_end_type(end_type), 'msg': gcman.get_error('none')}

@app.get('/populate_user_list/')
def populate_user_list(user=Depends(user_manager)) -> dict:
    """
    # Example return:
    [
    {'username': 'anormaluser', 'is_admin': 0, 'creation_time': '2024-06-07 17:28:01.903834'},
    {'username': 'admin', 'is_admin': 1, 'creation_time': '2024-06-07 17:28:02.237820'}
    ]
    """
    if not gcman.users.is_admin(user):
        raise HTTPException(status_code=400, detail=gcman.get_error('user_not_admin'))

    return {'code': 200, 'data': gcman.users.get_user_table(user), 'msg': gcman.get_error('none')}

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
    return {'code': 200, 'data': gcman.api.populate_patient_list(user), 'msg': gcman.get_error('none')}

@app.get('/populate_report_generator/{mode}')
def populate_report_generator(mode: str, lang: str, patient_id:str, user=Depends(user_manager)) -> dict:
    """
    ## Mode can be one of:

    Pharma = 疾病与用药指导
    ClinVAR = 临床表型相关变异
    Risk = 疾病风险提示

    lang (language) can be one of:
    'EN' English
    'CN' Chinese

    ## Example request:

    mode = Pharma
    lang = CN
    patient_id = '72210953309787'

    TODO: Deprecate lang;

    """
    return {'code': 200, 'data': gcman.api.populate_report_generator(mode, patient_id), 'msg': gcman.get_error('none')}

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
    if not gcman.patient_exists(patient_id):
        raise HTTPException(status_code=500, detail=gcman.get_error('pid_not_found', patient_id=patient_id))
    return {'code': 200, 'data': gcman.api.export_vcf(patient_id), 'msg': gcman.get_error('none')}

@app.get("/patient/export_cram/{patient_id}")
def export_cram(patient_id: str, user=Depends(user_manager)) -> dict:
    '''
    Example value:
    patient_id = '72210953309787'
    '''
    if not gcman.patient_exists(patient_id):
        raise HTTPException(status_code=500, detail=gcman.get_error('pid_not_found', patient_id=patient_id))
    return {'code': 200, 'data': gcman.api.export_cram(patient_id), 'msg': gcman.get_error('none')}

@app.get("/patient/export_gcm/{patient_id}")
def export_gcm(patient_id: str, user=Depends(user_manager)) -> dict:
    '''
    Example value:
    patient_id = '72210953309787'
    '''
    if not gcman.patient_exists(patient_id):
        raise HTTPException(status_code=500, detail=gcman.get_error('pid_not_found', patient_id=patient_id))
    return {'code': 200, 'data': gcman.get_gcm_path(user, patient_id), 'msg': gcman.get_error('none')}

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
    if not gcman.patient_exists(patient_id):
        raise HTTPException(status_code=500, detail=gcman.get_error('pid_not_found', patient_id=patient_id))

    if not gcman.analysis_complete(patient_id):
        raise HTTPException(status_code=500, detail=gcman.get_error('analysis_not_complete', patient_id=patient_id))

    html_filename, html = gcman.api.generate_report(user, mode, patient_id, selected_report)

    return {'code': 200, 'data': {'html_filename': html_filename, 'html': html}, 'msg': gcman.get_error('none')}

@app.get("/patient/{patient_id}")
def is_patient_id_valid(patient_id: str, user=Depends(user_manager)) -> dict:
    '''

    Test if a patient_id is valid

    Examples =
    '72210953309787' (returns True)
    '88888888' (returns False)

    '''
    ret = gcman.patient_exists(patient_id)
    return {'code': 200, 'data': ret, 'msg': gcman.get_error('none')}

@app.post('/add_patient')
def add_new_patient(
    patient_id: Annotated[str, Form()],
    sequence_data_id: Annotated[str, Form()],
    name: Annotated[str, Form()],
    sex: Annotated[str, Form()],
    age: Annotated[int, Form()],
    institution_sending: Annotated[str, Form()], # 送检机构
    files: list[UploadFile],
    #request: Request,
    user=Depends(user_manager)) -> dict:
    '''

    # Add a new patient to the database.

    ## Example data:
    patient_id: ANEWPATIENT12345

    sequence_data_id: SEQID2345

    name: 王XX

    sex: 男

    age: 30

    institution_sending: 一家大医院

    # Files:

    ## If Backend:

    GCManager-demo/demo_data/fastqs/SRR10286930_tiny_1.fastq.gz

    GCManager-demo/demo_data/fastqs/SRR10286930_tiny_2.fastq.gz

    ## If Doctorend:

    GCManager-demo/demo_data/gcms/SRR10286930.data.gcm

    '''
    assert gcman.end_type in ('Doctorend', 'Backend'), f'end_type has not been set'
    # TODO: This function is 2x slow, as it copies the file first, then copies it again.
    # Supposedly it should be possible to remove one of the copies by using the underlying Starlette
    # Streamer.

    gcman.log.info(f'Supplied {len(files)} files')

    # Check it doesn't exist already
    if gcman.patient_exists(patient_id):
        raise HTTPException(status_code=512, detail=gcman.get_error('pid_exists', patient_id=patient_id))

    # Validate the files for the specific end;
    if gcman.end_type == 'Doctorend':
        # expects one file only, consisting of the intermediate file;
        if len(files) != 1:
            raise HTTPException(status_code=513, detail=gcman.get_error('doc_only_one_file'))
        # expects the file to have the extension .int.gz
        if not (files[0].filename.lower().endswith('.gcm') or files[0].filename.lower().endswith('.vcf.gz')):
            raise HTTPException(status_code=514, detail=gcman.get_error('doc_wrong_file_format'))

    else: # Backend
        # expected an even number of files.
        if len(files) % 2 != 0:
            raise HTTPException(status_code=515, detail=gcman.get_error('ana_even_files'))
        # Expects all files to have the form _1.fastq.gz
        for f in files:
            if not f.filename.lower().endswith('.fastq.gz'):
                raise HTTPException(status_code=516, detail=gcman.get_error('ana_wrong_file_format', f=f))

    # copy the data to a temporary location
    temp_data_path = os.path.join(gcman.home_path, 'tmp')
    try:
        os.mkdir(temp_data_path)
    except FileExistsError:
        # A failed previous upload?
        shutil.rmtree(temp_data_path)
        os.mkdir(temp_data_path)

    start_time = int(time.time())

    for file in files:
        # Need to rename the files:
        if gcman.end_type == 'Doctorend':
            if file.filename.endswith('.gcm'):
                destination_filename = f'PID.{patient_id}.data.gcm' # Easy case
            elif file.filename.endswith('.vcf.gz'):
                destination_filename = f'PID.{patient_id}.vcf.gz' # Easy case
        elif gcman.end_type == 'Backend':
            # TODO: Difficult case...
            destination_filename = file.filename
            # TODO: Check that all filenames are unique

        try:
            gcman.log.info(f'Uploading file {file.filename}')
            #f = await run_in_threadpool(open, os.path.join(temp_data_path, destination_filename), 'wb')
            #await run_in_threadpool(shutil.copyfileobj, file.file, f)
            destination_location = os.path.join(temp_data_path, destination_filename)
            with open(destination_location, 'wb') as f:
                shutil.copyfileobj(file.file, f, length=1024*1024)

        except Exception: # Can restrict this to more reasonable throws?
            return {'code': 517, 'data': None, 'msg': gcman.get_error('upload_error')}
        finally:
            #if 'f' in locals(): await run_in_threadpool(f.close)
            #await file.close()
            gcman.log.info(f'Finished uploading file {file.filename} to {patient_id}')

    end_time = int(time.time())
    gcman.log.info(f'Uploaded {len(files)} files in {end_time - start_time} to {patient_id} seconds')

    # You have to do this after the copy, otherwise you end up with a half-done patient if the
    # upload fails.
    ret_code, sequence_data_path, safe_patient_id = gcman.api.add_new_patient(
        user=user,
        patient_id=patient_id,
        sequence_data_id=sequence_data_id,
        name=name,
        sex=sex,
        age=age,
        institution_sending=institution_sending,
        )

    # move the data to the correct location
    allfiles = os.listdir(temp_data_path)
    for f in allfiles:
        src_path = os.path.join(temp_data_path, f)
        dst_path = os.path.join(sequence_data_path, f)
        shutil.move(src_path, dst_path)

    # And sanitise tmp
    shutil.rmtree(temp_data_path)

    if gcman.end_type == 'Doctorend':
        if file.filename.endswith('.gcm'): # We got a GCM
            # Need to rename the files as {safe_patient_id}.data.gcm
            try:
                gcman.get_qc(user, safe_patient_id) # See if we can load the gcm
            except _pickle.UnpicklingError:
                # delete the partially complete patient
                gcman.delete_patient(user=user, patient_id=patient_id)
                return {'code': 518, 'data': None, 'msg': gcman.get_error('gcm_corrupt')}
                
            # Set the analysis as complete;
            gcman.set_analysis_complete(safe_patient_id)
            gcman.log.info(f'Added GCM for {safe_patient_id}')
        elif file.filename.endswith('.vcf.gz'): # We got a VCF
            gcman.set_vcf_available(safe_patient_id)
            gcman.log.info(f'Converted VCF to GCM for {safe_patient_id}')
            try:
                gcman.dbsnp_vcf_to_gcm(os.path.join(sequence_data_path, destination_filename), os.path.join(sequence_data_path, destination_filename).replace('.vcf.gz', '.data.gcm'))
            except Exception:
                gcman.delete_patient(user=user, patient_id=patient_id)
                return {'code': 518, 'data': None, 'msg': gcman.get_error('vcf_corrupt')}
                
            gcman.get_qc(user, safe_patient_id)
            gcman.set_analysis_complete(safe_patient_id)

    else: # Backend/small platform
        # everything should be valid. I can add it to the queue.
        gcman.add_task(safe_patient_id)
        gcman.process_analysis_queue()

    gcman.update_patient_space_used(safe_patient_id)

    return {'code': 200, 'data': gcman.patient_exists(safe_patient_id), 'msg': gcman.get_error('none')}

# This version only takes the PATH of the file
@app.post('/add_patient_move')
def add_new_patient_move(
    patient_id: Annotated[str, Form()],
    sequence_data_id: Annotated[str, Form()],
    name: Annotated[str, Form()],
    sex: Annotated[str, Form()],
    age: Annotated[int, Form()],
    institution_sending: Annotated[str, Form()], # 送检机构
    #files: Annotated[list, Form()], # Send the path of the file.
    files: Annotated[list, Form()],
    #files: list[UploadFile], # If over the internet
    #request: Request,
    user=Depends(user_manager)) -> dict:
    '''

    # Add a new patient to the database.

    # This version accepts a file path, and MOVEs the data

    ## Example data:
    patient_id: ANEWPATIENT12345

    sequence_data_id: SEQID2345

    name: 王XX

    sex: 男

    age: 30

    institution_sending: 一家大医院

    ## Files:

    /Users/andrew/Tools/GCManager-demo/demo_data/fastqs/SRR10286930_tiny_1.fastq.gz

    /Users/andrew/Tools/GCManager-demo/demo_data/fastqs/SRR10286930_tiny_2.fastq.gz

    '''
    assert gcman.end_type in ('Backend',), f'end_type has not been set'

    files = files[0].strip('[]').strip("'").split(',')
    print(files)

    gcman.log.info(f'Supplied {len(files)} files')

    # Check it doesn't exist already
    if gcman.patient_exists(patient_id):
        raise HTTPException(status_code=512, detail=gcman.get_error('pid_exists', patient_id=patient_id))

    # Validate the files for the Backend;
    # expected an even number of files.
    if len(files) % 2 != 0:
        raise HTTPException(status_code=515, detail=gcman.get_error('ana_even_files'))
    # Expects all files to have the form _1.fastq.gz
    for f in files:
        if not f.lower().endswith('.fastq.gz'):
            raise HTTPException(status_code=516, detail=gcman.get_error('ana_wrong_file_format', f=f))

    # copy the data to a temporary location
    temp_data_path = os.path.join(gcman.home_path, 'tmp')
    try:
        os.mkdir(temp_data_path)
    except FileExistsError:
        # A failed previous upload?
        shutil.rmtree(temp_data_path)
        os.mkdir(temp_data_path)

    start_time = int(time.time())

    # list and shutil version
    for filename in files:
        # Need to rename the files:
        # TODO: Difficult case...
        destination_filename = os.path.split(filename)[1] # Don't rename the FASTQ
        # TODO: Check that all filenames are unique

        try:
            gcman.log.info(f'Moving file {filename}')
            #f = await run_in_threadpool(open, os.path.join(temp_data_path, destination_filename), 'wb')
            #await run_in_threadpool(shutil.copyfileobj, file.file, f)
            destination_location = os.path.join(temp_data_path, destination_filename)
            #with open(destination_location, 'wb') as f:
            shutil.move(filename, destination_location)

        except Exception:
            return {'code': 517, 'data': None, 'msg': gcman.get_error('upload_error')}
        finally:
            gcman.log.info(f'Finished uploading file {filename} to {patient_id}')

    end_time = int(time.time())
    gcman.log.info(f'Uploaded {len(files)} files in {end_time - start_time} to {patient_id} seconds')

    # You have to do this after the copy, otherwise you end up with a half-done patient if the
    # upload fails.
    ret_code, sequence_data_path, safe_patient_id = gcman.api.add_new_patient(
        user=user,
        patient_id=patient_id,
        sequence_data_id=sequence_data_id,
        name=name,
        sex=sex,
        age=age,
        institution_sending=institution_sending,
        )

    # move the data to the correct location
    allfiles = os.listdir(temp_data_path)
    for f in allfiles:
        src_path = os.path.join(temp_data_path, f)
        dst_path = os.path.join(sequence_data_path, f)
        shutil.move(src_path, dst_path)

    # And sanitise tmp, even though it's a move()
    shutil.rmtree(temp_data_path)

    # Backend/small platform
    gcman.add_task(patient_id)
    gcman.process_analysis_queue()

    gcman.update_patient_space_used(safe_patient_id)

    return {'code': 200, 'data': gcman.patient_exists(safe_patient_id), 'msg': gcman.get_error('none')}

@app.post('/del_patient')
def delete_patient(patient_id:str, user=Depends(user_manager)) -> dict:
    """

    Delete a patient from the system.

    Requires administrator privileges.

    """
    if not gcman.users.is_admin(user):
        # This is not a safe operation, non-admin users shouldn't even be able to get
        # here. In which case, issue Invalid Credentials and force logoff.
        raise InvalidCredentialsException

    if not gcman.patient_exists(patient_id):
        raise HTTPException(status_code=500, detail=gcman.get_error('pid_not_exist', patient_id=patient_id))

    gcman.delete_patient(user, patient_id)

    return {'code': 200, 'data': True, 'msg': gcman.get_error('none')}


@app.get("/patient/report_current_anaylsis_stage/")
def report_current_anaylsis_stage(user=Depends(user_manager)) -> dict:  # TODO: Fix typo
    '''
    Returns the current analysis stage for the indicated data,
    in the form:
    {1: 100, 2: 100, 3: 100, 4: 100, 5: 100, 6: 100, 7: 100, 8: 100, 9: 100}
    Used on the Analysis state page

    返回指示数据的当前分析阶段，
    形式为：
    {1: 100, 2: 100, 3: 100, 4: 100, 5: 100, 6: 100, 7: 100, 8: 100, 9: 100}
    任务分析状态
    '''
    percents, q_status, patient_id, q_size = gcman.report_current_analysis_stage()

    return {'code': 200,
        'data': {'percents': percents, 'q_message': q_status, 'current_analyis_patient_id': patient_id, 'items_on_q': q_size},
        'msg': q_status}

@app.get("/patient/export_QC_statistics/{patient_id}")
def export_QC_statistics(patient_id: str, user=Depends(user_manager)) -> dict:
    '''
    Returns the QC data as a string.

    以字符串形式返回分析摘要。
    用于分析摘要页面。 "分析总结".

    Example value:
    patient_id = '72210953309787'
    '''
    if not gcman.patient_exists(patient_id):
        raise HTTPException(status_code=500, detail=gcman.get_error('pid_not_found', patient_id=patient_id))

    return {'code': 200, 'data': gcman.get_qc(user, patient_id), 'msg': gcman.get_error('none')}

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
    if not gcman.patient_exists(patient_id):
        raise HTTPException(status_code=500, detail=gcman.get_error('pid_not_found', patient_id=patient_id))

    return {'code': 200, 'data': gcman.get_logs(user, patient_id), 'msg': gcman.get_error('none')}

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
    return {'code': 200, 'data': gcman.api.populate_patient_data_list(), 'msg': gcman.get_error('none')}

@app.get("/system/clean_free_space/")
def clean_free_space(user=Depends(user_manager)) -> dict:
    """

    The button: 清除缓存 on the 患者数据管理 page.

    """
    # This is a safe operation and non-admins can do.
    #if not gcman.users.is_admin(user):
    #    raise InvalidCredentialsException

    return {'code': 200, 'data': gcman.api.clean_free_space(user), 'msg': gcman.get_error('none')}

@app.get("/system/get_disk_space/")
def get_disk_space() -> dict:
    return {'code': 200, 'data': gcman.api.get_disk_space(), 'msg': gcman.get_error('none')}

@app.get("/patient/clean_up_analysis/{patient_id}")
def clean_up_analysis(patient_id: str, user=Depends(user_manager)) -> dict:
    '''
    Example value:
    patient_id = '72210953309787'
    '''
    # This is a safe operation and non-admins can do.
    #if not gcman.users.is_admin(user):
    #    raise InvalidCredentialsException

    if not gcman.patient_exists(patient_id):
        raise HTTPException(status_code=500, detail=gcman.get_error('pid_not_found', patient_id=patient_id))

    return {'code': 200, 'data': gcman.api.clean_up_analysis(user, patient_id), 'msg': gcman.get_error('cleanup_done')}

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
    return {'code': 200, 'data': gcman.api.get_system_doctor_setting(setting.key), 'msg': gcman.get_error('none')}

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
    return {'code': 200, 'data': gcman.api.get_system_backend_setting(setting.key), 'msg': gcman.get_error('none')}

@app.get("/settings/get_doctorend/{key}")
def get_system_doctor_setting(key:str) -> dict:
    '''
    Get a system setting on: 系统设置 page
    Example value:
    key = 'lang'
    '''
    return {'code': 200, 'data': gcman.api.get_system_doctor_setting(key), 'msg': gcman.get_error('none')}

@app.get("/settings/get_backend/{key}")
def get_system_backend_setting(key:str) -> dict:
    '''
    Get a system setting on: 系统设置 page
    Example value:
    key = 'lang'
    '''
    return {'code': 200, 'data': gcman.api.get_system_backend_setting(key), 'msg': gcman.get_error('none')}

@app.get("/security/get_public_key")
def get_public_key() -> dict:
    '''
    Returns the public crypto key
    '''
    return {'code': 200, 'data': gcman.get_public_key(), 'msg': gcman.get_error('none')}

@app.post('/security/register_frontend/')
def register_frontend(encrypted: str) -> dict:
    """
    ## Register the front end for the first time

    Note that  encrypted should be a base64 encoded UTF-8 string of bytes:
    base64.b64encode(encrypted).decode("utf-8")

    ## For example, if the ID == 'ABCDEFGHIJKLMMO'

    then encrypted is:

    Om7nQI7LG/RG8LvyC5fjzCEM981LAjyhiSrqQUkQ0f4P7PnYsgEbX6uYriO3Hox0AFfsSPM/FoWO4PMSMZUWCxE2EDSMHMCfBlIHuLC08p0bxZKghZUehXKsJMi3kAqSv49Gk/KiG5fE2rAkHhRo797TRfLHiFDyzbxtnTKEZFLMFMOd35+1q7WJ92vZ5jlXNB/SAGJvgVPgRfaT4AaWOYPllol82NGxFaZsRaSmVsjyaHb26ZdCxqMhS1Uo6u1mPdYYL2vXIYpB0l/X4S30CGSpVcbifjTLfeWI1FlAF5WQQsnFenXWmDl6xCGjzlTVOdZ0bF35q3GK0mt66EgQaA==

    """
    if gcman._already_registered():
        return {'code': 500, 'data': False, 'msg': gcman.get_error('system_registered')}
    try:
        ret = gcman.register_frontend(encrypted)
    except binascii.Error:
        raise HTTPException(status_code=500, detail=gcman.get_error('validation_enc_fail'))

    return {'code': 200, 'data': ret, 'msg': gcman.get_error('none')}

@app.post('/security/clear_activation/')
def clear_activation() -> dict:
    """

    ## Clear the activation

    """
    if not gcman._already_registered():
        return {'code': 500, 'data': False, 'msg': gcman.get_error('sys_not_registered')}

    return {'code': 200, 'data': gcman.clear_activation(), 'msg': gcman.get_error('none')}

@app.post('/security/validate/')
def validate(encrypted: str) -> dict:
    '''
    ## Validate the encrypted string

    Note that  encrypted should be a base64 encoded UTF-8 string of bytes:
    base64.b64encode(encrypted).decode("utf-8")

    ## For example, if the ID == 'ABCDEFGHIJKLMMO'

    then encrypted is:

    Om7nQI7LG/RG8LvyC5fjzCEM981LAjyhiSrqQUkQ0f4P7PnYsgEbX6uYriO3Hox0AFfsSPM/FoWO4PMSMZUWCxE2EDSMHMCfBlIHuLC08p0bxZKghZUehXKsJMi3kAqSv49Gk/KiG5fE2rAkHhRo797TRfLHiFDyzbxtnTKEZFLMFMOd35+1q7WJ92vZ5jlXNB/SAGJvgVPgRfaT4AaWOYPllol82NGxFaZsRaSmVsjyaHb26ZdCxqMhS1Uo6u1mPdYYL2vXIYpB0l/X4S30CGSpVcbifjTLfeWI1FlAF5WQQsnFenXWmDl6xCGjzlTVOdZ0bF35q3GK0mt66EgQaA==

    '''
    try:
        ret = gcman.check_frontend_registration(encrypted)
    except ValueError:
        raise HTTPException(status_code=500, detail=gcman.get_error('validation_enc_fail'))

    return {'code': 200, 'data': ret, 'msg': gcman.get_error('none')}

@app.get('/settings/get_help_text')
def get_help_text() -> dict:
    return {'code': 200, 'data': gcman.get_help(), 'msg': gcman.get_error('none')}

@app.get('/settings/get_version')
def get_version() -> dict:
    return {'code': 200, 'data': gcman.get_version(), 'msg': gcman.get_error('none')}

@app.get('/settings/get_manual')
def get_manual() -> dict:
    return {'code': 200, 'data': gcman.get_manual(), 'msg': gcman.get_error('none')}
