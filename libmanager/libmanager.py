#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024 中基科生物保留所有权利
#
# Author(s):
# Andrew P. Hutchins,
#

# TODO:
# 1. Fix up the exceptions
# 2. Use decorators for the db open closing

import os
import sys
import sqlite3
import datetime
import glob
import uuid
import pathlib
import shutil
import time
import asyncio
import tarfile
import gzip
import base64
import unicodedata
import re
from threading import Thread

from . import analysis_progress
from . import analysis_queue
from . import api
from . import stagedata
from . import logger
from . import reporter_pharma
from . import reporter_risk
from . import settings
from . import support
from . import user
from . import initialise
from . import utils
from . import help_text
from . import gcms
from . import security
from . import errormsgs
from . import VERSION, DBVERSION, RELEASEVERSION

class libmanager:
    def __init__(self, home_path):
        # One problem here: If it is a totally blank run, GCMData*/logs wont exist till
        # initialise is called...
        if not os.path.exists(os.path.join(home_path, 'logs')):
            self.log = logger.basic_logger()
            
        else: # Logs fine call the ful logger;
            self.log = logger.logger(os.path.join(home_path, 'logs'))

        self.end_type = None
        self.home_path = home_path
        #self.script_path = os.path.join(os.path.split(os.path.realpath(__file__))[0], '..')
        self.script_path = os.path.realpath(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
        self.db_path = os.path.join(self.home_path, 'dbs')
        self.data_path = os.path.join(self.home_path, 'data')
        self.backup_path = os.path.join(os.path.expanduser('~'), 'gcm', 'gcmbackup/')

        self.env = None
        self.fren = None

        self.api = api.api(self, self.log, home_path)

        self.patient_id = None
        self.seq_id = None

        self.analysis_progress = analysis_progress.analysis_progress(log=self.log, home_path=home_path)

        self.db_PID_path = os.path.join(self.home_path, 'dbs', "PID.db")
        self.db_disease_codes_path = os.path.join(self.home_path, 'dbs', "disease_codes.db")

        self.db_PID = None
        self.db_disease_codes = None

        self.users = user.users(self.home_path, self.log)

        self.settings = settings.settings(self.home_path)

        self.analysis_queue = analysis_queue.analysis_queue(self.script_path, self.db_path, self.data_path, self.log)

        try:
            self.check_security()
        except FileNotFoundError:
            # security wil fail if we are initialising a full DB
            pass

        self.log.info(f"Started libmanager")

    def check_security(self):
        '''
        **Purpose**
            Perform sanity and purity check on the system.

        '''
        # TODO: Make sure the username is 'gcm' (only if Backend)

        # TODO: Confirm GC, and the dbs structure.

        # dbenv checking
        with open(os.path.join(self.home_path, 'dbs', ".env"), "r") as f:
            cenv = f.read()

        if not self.env:
            self.env = cenv
        else:
            if self.env != cenv:
                self.log.info('Failed Machine security check (env is wrong)')
                return False

        with open(os.path.join(self.home_path, 'dbs', ".fren"), "r") as f:
            cfren = f.read()

        if not self.fren:
            self.fren = cfren
        else:
            if self.fren != cfren:
                self.log.info('Failed Machine security check (fren is wrong)')
                return False

        # TODO: Add md5sum check on self.db_disease_codes

        # Copy protection method 1: Check this machine is correct
        with open(os.path.join(self.db_path, ".mchne"), "r") as f:
            mchne = f.read()

        if not security.verify_password(utils.guid(), mchne):
            self.log.info('Failed Machine security check (machine ID has changed)')
            return False

        self.log.info('Security check passed')

        return True

    def check_if_its_time_to_backup_db(self, force:bool=False):
        '''
        **Purpose**
            see if enough time delta has elapsed to make it worth
            doing a backup;

        '''
        if not self.end_type:
            return None

        if self.end_type == 'Doctorend':
            last_backup_time = int(self.settings.get_doctor_setting('last_backup'))
        elif self.end_type == 'Backend':
            last_backup_time = int(self.settings.get_backend_setting('last_backup'))
        else:
            return None

        if time.time() - last_backup_time > 86400:  # 24 hours = 86400; time.time() reports seconds;
            def backup_db(self, path_to_copy):
                shutil.make_archive(os.path.join(self.backup_path, f'db_backup-{self.end_type}-{int(time.time())}'),
                    'gztar',
                    self.home_path, # root dir;
                    path_to_copy)
                return True

            if self.end_type == 'Doctorend':
                # Doctor end can be a full backup as space is reasonable
                Thread(target=backup_db, args=(self, self.home_path)).start()

            elif self.end_type == 'Backend':
                # Back end the space is massive. We can only backup the DBs.
                # TODO: Add selected data from data/
                #ret = Thread(target=backup_db, args=(self, self.db_path)).start()
                pass

            # Backup the database
            self.log.info(f'Backing up database on {datetime.datetime.today():%Y-%m-%d}')

            # Delete the oldest backup if > 20: #? Is this a good idea... Maybe skip this for now
            # and see if it become a problem in production.

            # Store
            if self.end_type == 'Doctorend':
                self.settings.set_doctor_setting('last_backup', int(time.time()))
            elif self.end_type == 'Backend':
                self.settings.set_backend_setting('last_backup', int(time.time()))

        else:
            self.log.info("Checked if it's time to do a DB backup, not needed")

        return None

    def set_end_type(self, end_type):
        """

        Set the end_type of the system
        (Required)

        """
        assert end_type in ('Doctorend', 'Backend'), f'{end_type} must be one of Doctorend or Backend'

        self.log.info(f"Set the end type as {end_type}")

        self.end_type = end_type
        return True

    def initialize(self, adminpass:str, demo:bool = False):
        '''
        **Purpose**
            Internal method to setup the empty databases


        '''
        self.log = initialise.initialize_system(self, self.end_type, self.log, self.script_path, self.home_path, self.backup_path, demo=demo)
        self.users.add_user(uuid.uuid4(), 'admin', adminpass, is_admin=True)
        return True

    def _sql_booler(self, v):
        if v == 1: return True
        return False

    def _sql_yesno(self, v, lang='CN'):
        if lang == 'EN':
            if v == '1': return 'Yes'
            return 'No'

        elif lang == 'CN':
            if v == '1': return '是'
            return '否'

        return '否'

    def _get_patient_data(self, user, patient_id) -> dict:
        '''
        **Purpose**
            get patient data for one row.

        '''
        self.db_PID = sqlite3.connect(self.db_PID_path)
        self.db_PID_cursor = self.db_PID.cursor()
        self.db_PID_cursor.execute('SELECT PID, name, age, sex, analysis_done, institution_sending FROM patients WHERE PID=?', (patient_id,))
        row = self.db_PID_cursor.fetchone()
        self.db_PID.close()

        row = {
            'patient_id': row[0],
            'name': row[1],
            'age': row[2],
            'sex': row[3],
            'analysis_done': bool(row[4]),
            'insititution_sending': row[5], # TODO: Fix typo
            }

        self.log.info(f'{user} asked for the patients_data for {patient_id}')
        return row

    def get_patients_table(self, user) -> list:
        '''
        **Purpose**
            Return a list of lists in the form:

            PatientID | analysis_complete

        '''
        self.lang = self.settings.get_lang(self.end_type)

        self.db_PID = sqlite3.connect(self.db_PID_path)
        self.db_PID_cursor = self.db_PID.cursor()
        self.db_PID_cursor.execute('SELECT PID, name, age, sex, analysis_done, institution_sending FROM patients')
        results = self.db_PID_cursor.fetchall()
        self.db_PID.close()

        clean_results = []
        for row in results:
            row = {
                'patient_id': row[0],
                'name': security.str_decrypt(row[1], self.fren),
                'age': security.str_decrypt(row[2], self.fren),
                'sex': security.str_decrypt(row[3], self.fren),
                'analysis_done': self._sql_yesno(row[4], self.lang),
                'insititution_sending': row[5],  # TODO: Fix typo
                }

            clean_results.append(row)

        self.log.info(f'{user} asked for the patients_data_table')
        return clean_results

    def get_patients_data_table(self) -> list:
        '''
        **Purpose**
            Return all of the patient_data table;
        '''
        self.lang = self.settings.get_lang(self.end_type)

        self.db_PID = sqlite3.connect(self.db_PID_path)
        self.db_PID_cursor = self.db_PID.cursor()
        self.db_PID_cursor.execute('SELECT * FROM patient_data')
        results = self.db_PID_cursor.fetchall()
        clean_results = []

        # Convert the 1/0 to Yes, No
        for row in results:
            # Update the space used whilst here; this should be fast enough, even
            # For hundreds of patients?
            patient_path = os.path.join(self.data_path, f'PID.{row[0]}')

            row = {
                'patient_id': row[0],
                'space_used': row[1],
                'data_packed': self._sql_yesno(row[2], self.lang),
                'cram_available': self._sql_yesno(row[3], self.lang),
                'vcf_available': self._sql_yesno(row[4], self.lang),
                }

            clean_results.append(row)

        self.db_PID.close()

        return clean_results

    def update_patient_space_used(self, patient_id:str) -> bool:
        db_PID = sqlite3.connect(self.db_PID_path)
        db_PID_cursor = db_PID.cursor()
        patient_path = os.path.join(self.data_path, f'PID.{patient_id}')
        k, m, g = utils.measure_disk_space(patient_path)
        # update the db;
        if self.end_type == 'Doctorend':
            db_PID_cursor.execute('UPDATE patient_data SET space_used = ? WHERE PID = ?', (m, patient_id))
        else:
            db_PID_cursor.execute('UPDATE patient_data SET space_used = ? WHERE PID = ?', (g, patient_id))
        db_PID.commit()
        db_PID.close()
        return True

    def __restrict_reports(self, gcm, results):
        restricted_reports = gcm.get_rest()
        if restricted_reports:
            res = []
            for r in results:
                if r[0] in restricted_reports:
                    res.append(r)
            return res
        return results

    def get_pharma_table(self, patient_id: str) -> list:
        '''
        **Purpose**
            Return the Pharma DB table;
        '''

        self.lang = self.settings.get_lang(self.end_type)

        self.db_disease_codes = sqlite3.connect(self.db_disease_codes_path)
        self.db_disease_codes_cursor = self.db_disease_codes.cursor()

        if self.lang == 'CN':
            self.db_disease_codes_cursor.execute('SELECT dis_code, desc_cn FROM diseasecodes_pharma')
        else:
            self.db_disease_codes_cursor.execute('SELECT dis_code, desc_en FROM diseasecodes_pharma')

        results = self.db_disease_codes_cursor.fetchall()
        self.db_disease_codes.close()

        # Now see if there are restrictions for this patient_id.
        if patient_id:
            gcm = gcms.gcm_file(os.path.join(self.data_path, f'PID.{patient_id}', f'PID.{patient_id}.data.gcm'), logger=self.log)
            results = self.__restrict_reports(gcm, results)

        if results:
            results = [i[1] for i in results]

        return results

    def get_risk_table(self, patient_id: str) -> list:
        '''
        **Purpose**
            Return all of the Risk DB table;
        '''
        self.lang = self.settings.get_lang(self.end_type)

        self.db_disease_codes = sqlite3.connect(self.db_disease_codes_path)
        self.db_disease_codes_cursor = self.db_disease_codes.cursor()

        if self.lang == 'CN':
            self.db_disease_codes_cursor.execute('SELECT dis_code, desc_cn FROM diseasecodes_risk')
        else:
            self.db_disease_codes_cursor.execute('SELECT dis_code, desc_en FROM diseasecodes_risk')

        results = self.db_disease_codes_cursor.fetchall()
        self.db_disease_codes.close()

        # Now see if there are restrictions for this patient_id.
        if patient_id:
            gcm = gcms.gcm_file(os.path.join(self.data_path, f'PID.{patient_id}', f'PID.{patient_id}.data.gcm'), logger=self.log)
            results = self.__restrict_reports(gcm, results)

        if results:
            results = [i[1] for i in results]

        return results

    def _check_analysis_is_complete(self, patient_id: str) -> bool:
        """
        **Purpose**
            check that the analysis is complete

            TODO: Deprecate. Use the more robust analysis_complete()
        """
        assert self.patient_exists(patient_id), f'{patient_id} not found'

        self.db_PID = sqlite3.connect(self.db_PID_path)
        self.db_PID_cursor = self.db_PID.cursor()
        self.db_PID_cursor.execute('SELECT analysis_done FROM patients WHERE PID= :patient_id', {'patient_id': patient_id})
        analysis_done = self.db_PID_cursor.fetchone()
        self.db_PID.close()

        if int(analysis_done[0]): return True

        return False

    def _check_cram_vcf_status(self, patient_id:str, to_check:str) -> bool:
        """
        **Purpose**
            Check if a VCF or CRAM exisits.

        """
        assert self.patient_exists(patient_id), f'{patient_id} not found'

        assert to_check in ('vcf', 'cram'), f'{to_check} is not valid'

        self.db_PID = sqlite3.connect(self.db_PID_path)
        self.db_PID_cursor = self.db_PID.cursor()

        if to_check == 'vcf':
            self.db_PID_cursor.execute('SELECT vcf_available FROM patient_data WHERE PID= :patient_id', {'patient_id': patient_id})
        elif to_check == 'cram':
            self.db_PID_cursor.execute('SELECT cram_available FROM patient_data WHERE PID= :patient_id', {'patient_id': patient_id})

        analysis_done = self.db_PID_cursor.fetchone()
        self.db_PID.close()
        if int(analysis_done[0]):
            return True
        return False

    def _get_log_fileA(self, stage:int, out_glob_filenames) -> list:
        '''
        **Purpose**
            Abstraction for *.outs
        '''
        results = []

        results.append('#############')
        results.append(f'#### Stage {stage}: {stagedata.stages[stage]}')
        results.append('#############')
        stage1_outs = glob.glob(out_glob_filenames)
        if not stage1_outs:
            results.append(f'Stage {stage} is incomplete')
            return True, results

        for f in sorted(list(stage1_outs)):
            with open(f, 'rt') as oh:
                results += oh.read().split('\n')

        return False, results

    def _get_log_fileB(self, stage:int, out_filename:str) -> list:
        '''
        **Purpose**
            Abstraction for *.outs
        '''
        results = []

        results.append('#############')
        results.append(f'#### Stage {stage}: {stagedata.stages[stage]}')
        results.append('#############')
        if not os.path.exists(out_filename):
            results.append(f'Stage {stage} is incomplete')
            return True, results

        with open(out_filename, 'rt') as oh:
            results += oh.read().split('\n')

        return False, results

    def get_logs(self, user: str, patient_id: str) -> str:
        '''
        **Purpose**
            collect and send all the log data

        '''
        assert self.patient_exists(patient_id), f'{patient_id} not found'

        self.log.info(f'{user} asked for analysis logs for {patient_id}')

        if os.path.exists(os.path.join(self.data_path, f'PID.{patient_id}', f'PID.{patient_id}.data.gcm')):
            self.log.info(f'GCM is available for {patient_id}')
            gcm = gcms.gcm_file(os.path.join(self.data_path, f'PID.{patient_id}', f'PID.{patient_id}.data.gcm'), logger=self.log)
            return gcm.get_logs()

        # Note that this still returns even if the analysis is incomplete;
        log_path = os.path.join(self.data_path, f'PID.{patient_id}')

        results = []

        # Collect by stage order;
        # Stage 1:
        is_completed, result = self._get_log_fileA(1, os.path.join(log_path, '*.align.out'))
        results += result
        if is_completed: return '\n'.join(results)

        # Stage 2:
        is_completed, result = self._get_log_fileA(2, os.path.join(log_path, '*.bqsr.out'))
        results += result
        if is_completed: return '\n'.join(results)

        # Stage 3:
        is_completed, result = self._get_log_fileB(3, os.path.join(log_path, 'merge_bams.out'))
        results += result
        if is_completed: return '\n'.join(results)

        # TODO: Collect the rest of the stages.

        return '\n'.join(results)

    def get_qc(self, user: str, patient_id: str) -> str:
        '''
        **Purpose**
            collect and send all the log data

        '''
        assert self.patient_exists(patient_id), f'{patient_id} not found'

        self.log.info(f'{user} asked for QC data for {patient_id}')

        if os.path.exists(os.path.join(self.data_path, f'PID.{patient_id}', f'PID.{patient_id}.data.gcm')):
            self.log.info(f'GCM is available for {patient_id}')
            gcm = gcms.gcm_file(os.path.join(self.data_path, f'PID.{patient_id}', f'PID.{patient_id}.data.gcm'), logger=self.log)
            return gcm.get_qc()

        elif os.path.exists(os.path.join(self.data_path, f'PID.{patient_id}', 'FATALERROR.out')):
            with open(os.path.join(self.data_path, f'PID.{patient_id}', 'FATALERROR.out'), 'rt') as f:
                return f.read()
        else:
            self.log.warning(f'QC data is not available for {patient_id}')
            if self.settings.get_lang(self.end_type) == 'EN':
                return 'QC data not available'
            else:
                return '质量控制数据不详'

        return ''

    def get_gcm_path(self, user:str, patient_id:str) -> str:
        '''
        **Purpose**
            Return the VCF filename;
        '''
        assert self.patient_exists(patient_id), f'{patient_id} not found'

        if not self._check_analysis_is_complete(patient_id):
            self.log.info(f'{user} asked for {patient_id} GCM file, but GCM file is not available, analysis is incomplete')
            return False

        gcm_path = os.path.join(self.data_path, f'PID.{patient_id}', f'PID.{patient_id}.data.gcm')

        if not os.path.exists(gcm_path):
            self.log.error(f'{user} asked for {patient_id} GCM file, but GCM file does not exist (although it was reported to exist)')
            return False

        self.log.info(f'{user} asked to export GCM data file for {patient_id}')

        return gcm_path

    def get_vcf_path(self, user:str, patient_id:str) -> str:
        '''
        **Purpose**
            Return the VCF filename;
        '''
        assert self.patient_exists(patient_id), f'{patient_id} not found'

        if not self._check_analysis_is_complete(patient_id):
            self.log.warning(f'{user} asked for {patient_id} VCF file, but VCF file is not available, analysis is incomplete')
            return False

        if not self._check_cram_vcf_status(patient_id, 'vcf'):
            self.log.warning(f'{user} asked for {patient_id} VCF file, but VCF file is not available')
            return False

        vcf_path = os.path.join(self.data_path, f'PID.{patient_id}', f'PID.{patient_id}.vcf.gz')

        if not os.path.exists(vcf_path):
            self.log.error(f'{user} asked for {patient_id} VCF file, but VCF file does not exist (although it was reported to exist)')
            return False

        return vcf_path

    def get_cram_path(self, user:str, patient_id:str) -> str:
        '''
        **Purpose**
            Return the CRAM filename;
        '''
        assert self.patient_exists(patient_id), f'{patient_id} not found'

        if not self._check_analysis_is_complete(patient_id):
            self.log.warning(f'{user} asked for {patient_id} CRAM file, but CRAM file is not available, analysis is incomplete')
            return False

        if not self._check_cram_vcf_status(patient_id, 'cram'):
            self.log.warning(f'{user} asked for {patient_id} CRAM file, but CRAM file is not available')
            return False

        cram_path = os.path.join(self.data_path, f'PID.{patient_id}', f'PID.{patient_id}.cram')

        if not os.path.exists(cram_path):
            self.log.error(f'{user} asked for {patient_id} CRAM file, but CRAM file does not exist (although it was reported to exist)')
            return False

        return cram_path

    def patient_exists(self, patient_id:str):
        '''
        **Purpose**
            Check if a patient exists in the system
            This will consult a SQL database (or equivalent) to check if the
            patient id exists

        **Returns**
            False or the patient data as a dict

        '''
        self.db_PID = sqlite3.connect(self.db_PID_path)
        self.db_PID_cursor = self.db_PID.cursor()
        r = self.db_PID_cursor.execute('SELECT * from patients WHERE pid=?', (patient_id, ))
        r = r.fetchall()
        self.db_PID.close()
        if len(r) == 0: return False
        if not r: return False
        if len(r) > 1: raise Exception('Patient database returned more than one entry!')

        return True

    def analysis_complete(self, patient_id:str) -> bool:
        '''
        **Purpose**
            See if the analysis is complete

        '''
        self.db_PID = sqlite3.connect(self.db_PID_path)
        self.db_PID_cursor = self.db_PID.cursor()
        r = self.db_PID_cursor.execute('SELECT analysis_done from patients WHERE pid=?', (patient_id, ))
        r = r.fetchall()
        self.db_PID.close()

        if len(r) > 1: raise Exception('Patient database returned more than one entry!')
        if len(r) == 0: return False
        r = int(r[0][0])
        if not r: return False

        return True

    def set_analysis_complete(self, patient_id:str) -> bool:
        '''
        **Purpose**
            if we have a GCM, then set the analysis to complete
        '''
        self.db_PID = sqlite3.connect(self.db_PID_path)
        self.db_PID_cursor = self.db_PID.cursor()
        self.db_PID_cursor.execute('UPDATE patients SET analysis_done=?, date_analysis=? WHERE PID=?', (1, datetime.datetime.now().isoformat(' '), patient_id, ))
        self.db_PID.commit()
        self.db_PID.close()
        self.update_patient_space_used(patient_id)
        return True

    def set_vcf_available(self, patient_id:str) -> bool:
        '''
        **Purpose**
            if we have a VCF,  set it to present
        '''
        self.db_PID = sqlite3.connect(self.db_PID_path)
        self.db_PID_cursor = self.db_PID.cursor()
        self.db_PID_cursor.execute('UPDATE patient_data SET vcf_available=?, data_packed=? WHERE PID=?', (1, datetime.datetime.now().isoformat(' '), patient_id, ))
        self.db_PID.commit()
        self.db_PID.close()
        self.update_patient_space_used(patient_id)
        return True

    def set_cram_available(self, patient_id:str) -> bool:
        '''
        **Purpose**
            if we have a CRAM,  set it to present
        '''
        self.db_PID = sqlite3.connect(self.db_PID_path)
        self.db_PID_cursor = self.db_PID.cursor()
        self.db_PID_cursor.execute('UPDATE patient_data SET cram_available=?, data_packed=? WHERE PID=?', (1, datetime.datetime.now().isoformat(' '), patient_id, ))
        self.db_PID.commit()
        self.db_PID.close()
        self.update_patient_space_used(patient_id)
        return True

    def dbsnp_vcf_to_gcm(self, vcf_filename, gcm_filename) -> bool:
        '''
        **Purpose**
            Convert to GCM
        '''
        gcms.dbsnp_vcf_to_gcm(self.script_path, vcf_filename, gcm_filename)

        return True

    def add_patient(self,
        user: str,
        patient_id: str,
        seq_id: str,
        name: str,
        sex: str,
        age: int,
        institution_sending: str,
        ):
        '''
        **Purpose**
            Setup new patient id, with a seq id, and validate all initial QC.

        '''
        def safe_filename(s):
            # Normalize string to remove accents and special characters
            s = unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode()
            # Replace unsafe characters with underscores
            return re.sub(r'[^a-zA-Z0-9_.-]', '_', s)

        patient_id = safe_filename(patient_id)

        # Should be impossible, but just in case
        if self.patient_exists(patient_id):
            raise Exception(f'{user} is trying to add {patient_id} but it already exists')

        # TODO: Check the size of the imported FASTQ files.
        # I guess if < 1Gb each, reject the data;

        # Add new patient ID:
        data_dir = os.path.join(self.home_path, 'data', f'PID.{patient_id}')
        newpid_row = {
            'patient_id': patient_id,
            'seq_id': seq_id,
            'name': security.str_encrypt(name, self.fren),
            'age': security.str_encrypt(str(age), self.fren),
            'sex': security.str_encrypt(sex, self.fren),
            'analysis_done': 0,
            'date_added': datetime.datetime.now().isoformat(' '),
            'date_analysis': 'null',
            'data_dir': data_dir,
            'institution_sending': institution_sending,
            }

        new_patient = '''INSERT INTO patients VALUES (:patient_id, :seq_id, :name, :age, :sex, :analysis_done, :date_added, :date_analysis, :data_dir, :institution_sending)'''

        self.db_PID = sqlite3.connect(self.db_PID_path)
        self.db_PID_cursor = self.db_PID.cursor()
        self.db_PID_cursor.execute(new_patient, newpid_row)
        self.db_PID_cursor.execute('INSERT INTO summary_statistics VALUES (:patient_id, :seq_id, 0)', newpid_row)
        self.db_PID_cursor.execute('INSERT INTO patient_data VALUES (:patient_id, "0Gb", 0, 0, 0)', newpid_row)
        self.db_PID.commit()
        self.db_PID.close()

        if os.path.exists(data_dir):
            raise Exception(f'{user} is trying to add {patient_id} but the data directory {data_dir} already exists')

        os.mkdir(data_dir)

        self.log.info(f'{user} added patient {patient_id}')

        sequence_data_path = data_dir # Copy the seq data here;

        # ret, sequence_data_path, safe_patient_id
        return True, sequence_data_path, patient_id

    def delete_patient(self, user:str, patient_id:str) -> bool:
        """

        Delete a patient and clean up the data.

        """
        assert self.patient_exists(patient_id), f'{patient_id} does not exist'

        if self.end_type == 'Backend':
            # Race condition.
            # Don't delete the patient if the analysis is incomplete.
            # But this leaves the possibility of an incomplete analysis...
            # Just delete it if it's not on the queue?

            if self.analysis_queue.patient_is_on_the_task_list(patient_id):
                self.log.info(f'{user} asked to delete {patient_id}, but {patient_id} is on the analysis queue and cannot be deleted')
                return False

            elif self.analysis_queue.patient_is_currently_processing(patient_id):
                # Yes, I want to delete this patient.
                # This would allow a user to delete a frozen analysis.
                self.analysis_queue.currently_processing = None

        # Check the data folder is valid;
        patient_db_path = os.path.join(self.home_path, 'data', f'PID.{patient_id}')
        assert os.path.exists(patient_db_path), f'{patient_db_path} file path is missing'
        shutil.rmtree(patient_db_path, ignore_errors=False)
        self.log.info(f'{user} deleted patient data {patient_db_path}')

        # Purge from the DB
        self.db_PID = sqlite3.connect(self.db_PID_path)
        self.db_PID_cursor = self.db_PID.cursor()
        self.db_PID_cursor.execute('DELETE FROM patients WHERE PID=?', (patient_id,))
        self.db_PID_cursor.execute('DELETE FROM patient_data WHERE PID=?', (patient_id,))
        self.db_PID.commit()
        self.db_PID.close()
        self.log.info(f'{user} deleted patient: {patient_id}')

        return True

    def summary_statistics(self, patient_id:str):
        '''
        **Purpose**
            Return the summary statistics for the patient_id

            TODO: Deprecate. Pretty sure this is not used. use gc.get_qc()
        '''
        self.db_PID = sqlite3.connect(self.db_PID_path)
        self.db_PID_cursor = self.db_PID.cursor()
        r = self.db_PID_cursor.execute('SELECT * FROM summary_statistics WHERE pid=?', (patient_id, ))
        r = r.fetchall()
        self.db_PID.close()

        if not r: return False
        if len(r) != 1: raise Exception('Patient database returned more than one entry!')

        return r[0]

    def report_current_analysis_stage(self):
        """
        Return the update;
        """
        self.lang = self.settings.get_lang(self.end_type) # Pull language out of system settings DB
        q_size = len(self.analysis_queue.q)

        if self.analysis_queue.currently_processing:
            current_patient_analysis_pid = self.analysis_queue.currently_processing['PID']
            if self.lang == 'EN': q_status = f'Currently processing {current_patient_analysis_pid}, there are {q_size} items on the queue.'
            else: q_status = f'目前正在处理{current_patient_analysis_pid}，队列中有{q_size}个项目。'
            return self.analysis_queue.analysis_progress(current_patient_analysis_pid), q_status, current_patient_analysis_pid, q_size

        # Nothing being processed:
        if self.lang == 'EN': patient_id = 'None'
        else: patient_id = '无'

        if self.lang == 'EN': q_status = 'Idle'
        else: q_status = '无'

        return {1: 100, 2: 100, 3: 100, 4: 100, 5: 100, 6: 100, 7: 100, 8: 100, 9: 100}, q_status, patient_id, q_size

    def generate_report(self, user:str, mode:str, patient_id:str, search_term:str):
        '''
        **Purpose**
            Generate a HTML report for patient_id and search_term

            Save the file into the ~/analysis/patient_id/patient_id.disease_code.pdf

        **Returns**
            Location of the saved HTML file
        '''
        assert mode in support.valid_genome_dbs, f'{mode} was not in {support.valid_genome_dbs.keys()}'
        assert self.analysis_complete(patient_id), f'{patient_id} analysis is not complete, but asking for a report'

        self.lang = self.settings.get_lang(self.end_type) # Pull language out of system settings DB
        gcm = gcms.gcm_file(os.path.join(self.data_path, f'PID.{patient_id}', f'PID.{patient_id}.data.gcm'), logger=self.log)

        self.log.info(f'User "{user}" asked for a {mode} report for patient_id {patient_id} for the condition {search_term}')

        # Get patient data;
        self.db_PID = sqlite3.connect(self.db_PID_path)
        self.db_PID_cursor = self.db_PID.cursor()
        self.db_PID_cursor.execute('SELECT name, age, sex FROM patients WHERE pid=?', (patient_id, ))
        patient_data = self.db_PID_cursor.fetchone()
        self.db_PID.close()

        # TODO: Check return
        patient_data = {'name': security.str_decrypt(patient_data[0], self.fren),
            'age': security.str_decrypt(patient_data[1], self.fren),
            'sex': security.str_decrypt(patient_data[2], self.fren)}

        self.db_disease_codes = sqlite3.connect(self.db_disease_codes_path)
        self.db_disease_codes_cursor = self.db_disease_codes.cursor()

        html = ''
        html_file = ''

        # Select the proper report generator:
        if mode == 'Pharma':
            self.db_disease_codes_cursor.execute('SELECT dis_code, desc_en, desc_cn FROM diseasecodes_pharma WHERE desc_en=? OR desc_cn=?', (search_term, search_term))
            res = self.db_disease_codes_cursor.fetchone()
            if not res:
                raise AssertionError(f'{search_term} was not found in diseasecodes_pharma database')

            disease_code = res[0]
            descEN = res[1]
            descCN = res[2]

            self.log.info(f'Search found: {disease_code}, {descEN}, {descCN}')

            if not gcm.report_available(disease_code):
                self.log.info(f'User {user} asked for a {mode} report for {patient_id} but a report for {search_term} is not avaialble')
                return None, None

            rep = reporter_pharma.reporter_pharma(self.data_path, self.script_path, patient_id, patient_data, gcm, disease_code, descEN, descCN, self.log, self.lang)
            html_file, html = rep.generate()

        elif mode == 'ClinVAR':
            html = ''
            html_file = ''

        elif mode == 'Risk':
            self.db_disease_codes_cursor.execute('SELECT dis_code, desc_en, desc_cn FROM diseasecodes_risk WHERE desc_en=? OR desc_cn=?', (search_term, search_term))
            res = self.db_disease_codes_cursor.fetchone()
            if not res:
                raise AssertionError(f'{search_term} was not found in diseasecodes_risk database')

            disease_code = res[0]
            descEN = res[1]
            descCN = res[2]

            self.log.info(f'Search found: {disease_code}, {descEN}, {descCN}')

            if not gcm.report_available(disease_code):
                self.log.info(f'User {user} asked for a {mode} report for {patient_id} but a report for {search_term} is not avaialble')
                return None, None

            rep = reporter_risk.reporter_risk(self.data_path, self.script_path, patient_id, patient_data, gcm, disease_code, descEN, descCN, self.log, self.lang)
            html_file, html = rep.generate()

        self.db_disease_codes.close()

        return html_file, html

    def get_public_key(self) -> str:
        '''
        **Purpose**
            Return the public key

        '''
        self.log.info('Asked for public crypto key')
        if 'demo' in VERSION:
            return security.get_public_key_stream(os.path.join(self.script_path, 'keys', 'demo.public_key.pem'))
        # Production
        return security.get_public_key_stream(os.path.join(self.script_path, 'keys', 'production.public_key.pem'))

    def _already_registered(self) -> bool:
        if os.path.exists(os.path.join(self.data_path, '.mac')):
            return True
        return False

    def register_frontend(self, encrypted:str) -> bool:
        """

        register front end for the first time

        """
        if self._already_registered():
            return False # Tried to register twice.

        encrypted = base64.b64decode(encrypted) # reverse of base64.b64encode(encrypted).decode("utf-8")

        if 'demo' in VERSION:
            private_key = security.load_private_key(os.path.join(self.script_path, 'keys', 'demo.private_key.pem'))
        else: # Production
            private_key = security.load_private_key(os.path.join(self.script_path, 'keys', 'production.private_key.pem'))

        m = security.decrypt(encrypted, private_key)

        with open(os.path.join(self.data_path, '.mac'), "w") as f:
            f.write(security.hash_password(m))

        self.log.info('Registered front end for the first time')

        return True

    def clear_activation(self) -> bool:
        """
        # Clear the activation key;
        """
        m = os.path.join(self.data_path, '.mac')
        if not os.path.exists(m):
            return False

        os.remove(m)

        return True

    def check_frontend_registration(self, encrypted:str) -> bool:
        """
        **Purpose**
            Check the front end is registered

        """
        if not self._already_registered():
            return False # Tried to register twice.

        encrypted = base64.b64decode(encrypted) # reverse of base64.b64encode(encrypted).decode("utf-8")

        if 'demo' in VERSION:
            private_key = security.load_private_key(os.path.join(self.script_path, 'keys', 'demo.private_key.pem'))
        else: # Production
            private_key = security.load_private_key(os.path.join(self.script_path, 'keys', 'production.private_key.pem'))

        m = security.decrypt(encrypted, private_key)
        with open(os.path.join(self.data_path, '.mac'), "r") as f:
            p = f.read()

        self.log.info('Checked the front end registration')

        return security.verify_password(m, p)

    def get_help(self) -> str:
        """
        **Purpose**
            Return the help text.
        """
        self.lang = self.settings.get_lang(self.end_type)
        return help_text.get_help(self.end_type, self.lang)

    def get_manual(self) -> str:
        return os.path.join(self.script_path, 'manual', 'manual.cn.pdf')

    def get_version(self) -> str:
        self.lang = self.settings.get_lang(self.end_type) # Pull language out of system settings DB
        SVER = VERSION.replace(' demo', '')
        if self.lang == 'EN':
            return f'Release Version: {RELEASEVERSION}. Full version: {SVER}'
        return f'发布版本：{RELEASEVERSION} 完整版本：{SVER}'

    def get_error(self, typ, **kargs):
        self.lang = self.settings.get_lang(self.end_type)

        if typ not in errormsgs.errormsgs[self.lang]:
            if self.lang == 'EN': return 'None'
            else: return '无'

        if kargs:
            return errormsgs.errormsgs[self.lang][typ].format(**kargs)
        return errormsgs.errormsgs[self.lang][typ]

    def add_task(self, patient_id:str) -> bool:
        """
        Process the current analysis queue

        """
        if self.end_type != 'Backend':
            return

        return self.analysis_queue.add_task(patient_id)

    def process_analysis_queue(self) -> bool:
        """
        Process the current analysis queue

        """
        if self.end_type != 'Backend':
            return

        completed_patient_id = self.analysis_queue.run()

        if completed_patient_id:
            self.set_analysis_complete(completed_patient_id)

            if os.path.exists(os.path.join(self.data_path, f'PID.{completed_patient_id}', 'PID.{completed_patient_id}.vcf.gz')):
                self.set_vcf_available(completed_patient_id)

            if os.path.exists(os.path.join(self.data_path, f'PID.{completed_patient_id}', 'PID.{completed_patient_id}.cram')):
                self.set_cram_available(completed_patient_id)

            self.update_patient_space_used(completed_patient_id)

        return True
