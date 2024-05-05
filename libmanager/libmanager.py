#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024
#
# Author(s):
# Andrew P. Hutchins,
#

# TODO:
# 1. Fix up the exceptions

import os, sys, sqlite3, datetime

from . import analysis_progress
from . import initialise_dbs
from . import api

class libmanager:
    def __init__(self, log, home_path):
        self.log = log
        self.home_path = home_path
        self.db_path = os.path.join(self.home_path, 'dbs/')
        self.data_path = os.path.join(self.home_path, 'data/')

        self.api = api.api(self, log, home_path)

        self.log.info("Started libmanager")

        self.patient_id = None
        self.seq_id = None

        self.analysis_progress = analysis_progress.analysis_progress(log=log, home_path=home_path)

        # Open PID database
        self.db_PID = sqlite3.connect(os.path.join(self.home_path, 'dbs/', "PID.db"))
        self.db_PID_cursor = self.db_PID.cursor()

        # disease code databse:
        self.db_disease_codes = sqlite3.connect(os.path.join(self.home_path, 'dbs/', "disease_codes.db"))
        self.db_disease_codes_cursor = self.db_disease_codes.cursor()

    def _security_check(self):
        '''
        **Purpose**
            Perform sanity and purity check on the system.

        '''
        # TODO: Make sure the username is 'gcmanager'

        # TODO: Confirm GC, and the dbs structure.

        # TODO: Add md5sum check on diseaseDB

        return True

    def _initialize(self, demo:bool = False):
        '''
        **Purpose**
            Internal method to setup the empty databases


        '''
        initialise_dbs.init_dbs(self.home_path, os.path.join(os.path.split(sys.argv[0])[0], '../'), self.log)

        if demo:
            initialise_dbs.build_demo_data(self, self.home_path, self.log)

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
            return '不'

    def get_patients_table(self) -> list:
        '''
        **Purpose**
            Return a list of lists in the form:

            PatientID | analysis_complete

        '''
        # TODO: Enable fuzzy searching

        self.db_PID_cursor.execute('SELECT PID, analysis_done FROM patients')
        results = self.db_PID_cursor.fetchall()

        return results

    def get_patients_data_table(self) -> list:
        '''
        **Purpose**
            Return all of the pateinet_data table;
        '''
        self.db_PID_cursor.execute('SELECT * FROM patient_data')
        results = self.db_PID_cursor.fetchall()

        print(results)

        clean_results = []

        # Convert the 1/0 to Yes, No
        for row in results:
            row = list(row)
            print(row)
            row[2] = self._sql_yesno(row[2])
            row[3] = self._sql_yesno(row[3])
            row[4] = self._sql_yesno(row[4])
            clean_results.append(row)

        return clean_results

    def get_disbd_table(self, lang='CN') -> list:
        '''
        **Purpose**
            Return all of the pateinet_data table;
        '''
        if lang == 'CN':
            self.db_disease_codes_cursor.execute('SELECT * FROM diseasecodes')
        else:
            self.db_disease_codes_cursor.execute('SELECT * FROM diseasecodes')
        results = self.db_disease_codes_cursor.fetchall()

        return results

    def get_vcf_path(self, patient_id: str) -> str:
        '''
        **Purpose**
            Return the VCF filename;
        '''
        self.db_PID_cursor.execute('SELECT analysis_done FROM patients WHERE PID= :patient_id', {'patient_id': patient_id})
        analysis_done = self.db_PID_cursor.fetchone()

        print(analysis_done[0])

        if not analysis_done[0]:
            self.log.error(f'Asked for {patient_id} VCF file, but VCF file is not avaialble')
            raise LookupError(f'Asked for {patient_id} VCF file, but VCF file is not avaialble')

        vcf_path = os.path.join(self.data_path, f'PID.{patient_id}', f'{patient_id}.recalibrated_snps_recalibrated_indels.vcf.gz')

        print(vcf_path)

        if not os.path.exists(vcf_path):
            self.log.error(f'Asked for {patient_id} VCF file, but VCF file does not exist (although it was reported to exist)')
            raise LookupError(f'Asked for {patient_id} VCF file, but VCF file does not exist (although it was reported to exist)')

        return vcf_path

    def patient_exists(self, patient_id:str):
        '''
        **Purpose**
            Check if a patient exists in the system
            This will consult a SQL database (or equivalent) to check if the
            patient id exists

        **Returns**
            False or the patient data as a dict

        '''
        r = self.db_PID_cursor.execute('SELECT * from patients WHERE pid=?', (patient_id, ))
        r = r.fetchall()

        if not r: return False
        if len(r) != 1: raise Exception('Patient database returned more than one entry!')

        return r[0]

    def add_patient(self, patient_id: str, seq_id: str):
        '''
        **Purpose**
            Setup new patient id, with a seq id, and validate all initial QC.

        '''
        # Should be impossible, but just in case
        if self.patient_exists(patient_id):
            raise Exception(f'Trying to add {patient_id} but it already exists')

        # TODO: Check the size of the imported FASTQ files.
        # I guess if < 1Gb each, reject the data;


        # Add new patient ID:
        data_dir = os.path.join(self.home_path, 'data', f'PID.{patient_id}')
        newpid_row = {
            'patient_id': patient_id,
            'seq_id': seq_id,
            'analysis_done': 0,
            'date_added': datetime.datetime.now().isoformat(' '),
            'date_analysis': 'null',
            'data_dir': data_dir,
            }
        self.db_PID_cursor.execute('INSERT INTO patients VALUES (:patient_id, :seq_id, :analysis_done, :date_added, :date_analysis, :data_dir)', newpid_row)
        self.db_PID_cursor.execute('INSERT INTO summary_statistics VALUES (:patient_id, :seq_id, 0)', newpid_row)
        self.db_PID_cursor.execute('INSERT INTO patient_data VALUES (:patient_id, "0Gb", 0, 0, 0)', newpid_row)
        self.db_PID.commit()

        if os.path.exists(data_dir):
            raise Exception(f'Trying to add {patient_id} but the data directory {data_dir} already exists')
        os.mkdir(data_dir)

        return True

    def summary_statistics(self, patient_id:str, ):
        '''
        **Purpose**
            Return the summary statistics for the patient_id
        '''
        r = self.db_PID_cursor.execute('SELECT * from summary_statistics WHERE pid=?', (patient_id, ))
        r = r.fetchall()

        if not r: return False
        if len(r) != 1: raise Exception('Patient database returned more than one entry!')

        return r[0]

    def generate_report(self, patient_id:str, disease_code:str):
        '''
        **Purpose**
            Generate a PDF report for patient_id and disease_code

            Save the file into the ~/analysis/patient_id/patient_id.disease_code.pdf

        **Returns**
            Location of the saved PDF file
        '''
        return f'~/data/{patient_id}.{disease_code}.pdf'
