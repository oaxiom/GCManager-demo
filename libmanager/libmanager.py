#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024
#
# Author(s):
# Andrew P. Hutchins,
#

import os, sqlite3, datetime

from . import analysis_progress

class libmanager:
    def __init__(self, log, home_path):
        self.log = log
        self.home_path = home_path

        self.log.info("Started libmanager")

        self.patient_id = None
        self.seq_id = None

        self.analysis_progress = analysis_progress.analysis_progress(log=log, home_path=home_path)

        # Open PID database
        self.sql = sqlite3.connect(os.path.join(self.home_path, 'dbs/', "PID.db"))
        self.db = self.sql.cursor()

    def _security_check(self):
        '''
        **Purpose**
            Perform sanity and purity check on the system.

        '''
        # TODO: Make sure the username is 'gcmanager'

        # TODO: Confirm GC, and the dbs structure.

        # TODO: Add md5sum check on diseaseDB

        return True

    def _initialize(self):
        '''
        **Purpose**
            Internal method to setup the empty databases


        '''
        # Setup the PID database;
        # TODO: Setup the date properly.
        self.db.execute('CREATE TABLE patients (PID TEXT, SID TEXT, analysis_done TEXT, date_added TEXT, date_analysis TEXT, data_dir TEXT)')
        self.sql.commit()

        # summary statistics DB:
        self.db.execute('CREATE TABLE summary_statistics (PID TEXT, SID TEXT, aligned_reads INT)')
        self.sql.commit()

        # TODO: Setup the disease code database, by packing the raw data
        disease_db = sqlite3.connect(os.path.join(self.home_path, "dbs/", "disease_codes.db"))
        c = disease_db.cursor()
        c.execute('CREATE TABLE diseasecodes (dis_code TEXT, desc_en TEXT, desc_cn TEXT)')
        # TODO: Load from spreadsheet;
        disease_db.commit()
        disease_db.close()

        return True

    def patient_exists(self, patient_id:str):
        '''
        **Purpose**
            Check if a patient exists in the system
            This will consult a SQL database (or equivalent) to check if the
            patient id exists

        **Returns**
            False or the patient data as a dict

        '''
        r = self.db.execute('SELECT * from patients WHERE pid=?', (patient_id, ))
        r = r.fetchall()

        if not r: return False
        if len(r) != 1: raise Exception('Patient database returned more than one entry!')

        return r[0]

    def setup(self, patient_id: str, seq_id: str):
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
        self.db.execute('INSERT INTO patients VALUES (:patient_id, :seq_id, :analysis_done, :date_added, :date_analysis, :data_dir)', newpid_row)
        self.db.execute('INSERT INTO summary_statistics VALUES (:patient_id, :seq_id, 0)', newpid_row)
        self.sql.commit()

        if os.path.exists(data_dir):
            raise Exception(f'Trying to add {patient_id} but the data directory {data_dir} already exists')
        os.mkdir(data_dir)

        self.analysis_progress.add_patient(patient_id, data_dir)

        return True

    def summary_statistics(self, patient_id:str, ):
        '''
        **Purpose**
            Return the summary statistics for the patient_id
        '''
        r = self.db.execute('SELECT * from summary_statistics WHERE pid=?', (patient_id, ))
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
            Location of the save PDF file
        '''
        return f'~/data/{patient_id}.{disease_code}.pdf'
