#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024
#
# Author(s):
# Andrew P. Hutchins,
#

# TODO:
# 1. Fix up the exceptions

import os, sys, sqlite3, datetime, glob, uuid

from . import analysis_progress
from . import api
from . import stagedata
from . import logger
from . import reporter_pharma
from . import reporter_risk
from . import settings
from . import support
from . import user
from . import initialise

class libmanager:
    def __init__(self, end_type, log, home_path):
        assert end_type in ('Doctorend', 'Backend'), f'{end_type} must be one of Doctorend or Backend'

        self.log = logger.logger()
        self.end_type = end_type
        self.home_path = home_path
        self.script_path = os.path.join(os.path.split(os.path.realpath(__file__))[0], '..')
        self.db_path = os.path.join(self.home_path, 'dbs')
        self.data_path = os.path.join(self.home_path, 'data')

        self.api = api.api(self, log, home_path)

        self.patient_id = None
        self.seq_id = None

        self.analysis_progress = analysis_progress.analysis_progress(log=log, home_path=home_path)

        self.db_PID_path = os.path.join(self.home_path, 'dbs', "PID.db")
        self.db_disease_codes_path = os.path.join(self.home_path, 'dbs', "disease_codes.db")

        self.db_PID = None
        self.db_disease_codes = None

        self.users = user.users(self.home_path, self.log)

        # TODO: Move these open/close to a function to clean up the code

        # Open PID database
        #self.db_PID = sqlite3.connect(self.db_PID_path)
        #self.db_PID_cursor = self.db_PID.cursor()
        # ...
        #self.db_PID.close()

        # disease code databse:
        #self.db_disease_codes.close() = sqlite3.connect(self.db_disease_codes_path)
        #self.db_disease_codes_cursor = self.db_disease_codes.cursor()
        # ...
        #self.db_disease_codes.close()

        self.settings = settings.settings(self.home_path)

        self.log.info(f"Started libmanager: {end_type}")

    def _security_check(self):
        '''
        **Purpose**
            Perform sanity and purity check on the system.

            Must be fast, and callable from most functions.

            TODO: Maybe have a FAST and SLOW security check? or an async one?

        '''
        # TODO: Make sure the username is 'gcm'

        # TODO: Confirm GC, and the dbs structure.

        # TODO: Add md5sum check on self.db_disease_codes

        return True

    def initialize(self, adminpass:str, demo:bool = False):
        '''
        **Purpose**
            Internal method to setup the empty databases


        '''
        initialise.initialize_system(self, self.end_type, self.log, self.script_path, self.home_path, demo=demo)
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
            return '不'

        return 'No'

    def get_patients_table(self) -> list:
        '''
        **Purpose**
            Return a list of lists in the form:

            PatientID | analysis_complete

        '''
        # TODO: Enable fuzzy searching
        self.db_PID = sqlite3.connect(self.db_PID_path)
        self.db_PID_cursor = self.db_PID.cursor()
        self.db_PID_cursor.execute('SELECT PID, name, age, sex, analysis_done FROM patients')
        results = self.db_PID_cursor.fetchall()
        self.db_PID.close()

        clean_results = []
        for row in results:
            row = {
                'patient_id': row[0],
                'name': row[1],
                'age': row[2],
                'sex': row[3],
                'analysis_done': self._sql_yesno(row[4])
                }

            clean_results.append(row)

        return clean_results

    def get_patients_data_table(self) -> list:
        '''
        **Purpose**
            Return all of the pateinet_data table;
        '''
        self.db_PID = sqlite3.connect(self.db_PID_path)
        self.db_PID_cursor = self.db_PID.cursor()
        self.db_PID_cursor.execute('SELECT * FROM patient_data')
        results = self.db_PID_cursor.fetchall()
        self.db_PID.close()
        clean_results = []

        # Convert the 1/0 to Yes, No
        for row in results:
            row = {
                'patient_id': row[0],
                'space_used': row[1],
                'data_packed': self._sql_yesno(row[2]),
                'cram_available': self._sql_yesno(row[3]),
                'vcf_available': self._sql_yesno(row[4]),
                }

            clean_results.append(row)

        return clean_results

    def get_pharma_table(self, lang='CN') -> list:
        '''
        **Purpose**
            Return the Pharma DB table;
        '''
        self.db_disease_codes = sqlite3.connect(self.db_disease_codes_path)
        self.db_disease_codes_cursor = self.db_disease_codes.cursor()

        if lang == 'CN':
            self.db_disease_codes_cursor.execute('SELECT desc_cn FROM diseasecodes_pharma')
        else:
            self.db_disease_codes_cursor.execute('SELECT desc_en FROM diseasecodes_pharma')

        results = self.db_disease_codes_cursor.fetchall()
        self.db_disease_codes.close()

        if results:
            results = [i[0] for i in results]

        return results

    def get_risk_table(self, lang='CN') -> list:
        '''
        **Purpose**
            Return all of the Risk DB table;
        '''
        self.db_disease_codes = sqlite3.connect(self.db_disease_codes_path)
        self.db_disease_codes_cursor = self.db_disease_codes.cursor()

        if lang == 'CN':
            self.db_disease_codes_cursor.execute('SELECT desc_cn FROM diseasecodes_risk')
        else:
            self.db_disease_codes_cursor.execute('SELECT desc_en FROM diseasecodes_risk')

        results = self.db_disease_codes_cursor.fetchall()
        self.db_disease_codes.close()

        if results:
            results = [i[0] for i in results]

        return results

    def _check_analysis_is_complete(self, patient_id: str) -> bool:
        """
        **Purpose**
            check that the analysis is complete
        """
        self.db_PID = sqlite3.connect(self.db_PID_path)
        self.db_PID_cursor = self.db_PID.cursor()
        self.db_PID_cursor.execute('SELECT analysis_done FROM patients WHERE PID= :patient_id', {'patient_id': patient_id})
        analysis_done = self.db_PID_cursor.fetchone()
        self.db_PID.close()

        if analysis_done[0]: return True

        return False

    def _check_cram_vcf_status(self, patient_id:str, to_check:str) -> bool:
        """
        **Purpose**
            Check if a VCF or CRAM exisits.

        """
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

    def get_logs(self, patient_id: str) -> str:
        '''
        **Purpose**
            collect and send all the log data

        '''
        self.patient_exists(patient_id)

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

        return '\n'.join(results)

    def get_vcf_path(self, patient_id: str) -> str:
        '''
        **Purpose**
            Return the VCF filename;
        '''
        self.patient_exists(patient_id)

        if not self._check_analysis_is_complete(patient_id):
            self.log.error(f'Asked for {patient_id} VCF file, but VCF file is not available, analysis is incomplete')
            raise LookupError(f'Asked for {patient_id} VCF file, but VCF file is not available, analysis is incomplete')

        if not self._check_cram_vcf_status(patient_id, 'vcf'):
            self.log.warning(f'Asked for {patient_id} VCF file, but VCF file is not avaialble')
            raise LookupError(f'Asked for {patient_id} VCF file, but VCF file is not available, analysis is incomplete')

        vcf_path = os.path.join(self.data_path, f'PID.{patient_id}', f'{patient_id}.gatk.dbsnp.vcf.gz')

        if not os.path.exists(vcf_path):
            self.log.error(f'Asked for {patient_id} VCF file, but VCF file does not exist (although it was reported to exist)')
            raise LookupError(f'Asked for {patient_id} VCF file, but VCF file does not exist (although it was reported to exist)')

        return vcf_path

    def get_cram_path(self, patient_id: str) -> str:
        '''
        **Purpose**
            Return the VCF filename;
        '''
        self.patient_exists(patient_id)

        if not self._check_analysis_is_complete(patient_id):
            self.log.error(f'Asked for {patient_id} CRAM file, but CRAM file is not available, analysis is incomplete')
            raise LookupError(f'Asked for {patient_id} CRAM file, but CRAM file is not available, analysis is incomplete')

        if not self._check_cram_vcf_status(patient_id, 'cram'):
            self.log.warning(f'Asked for {patient_id} CRAM file, but CRAM file is not available')
            return False

        cram_path = os.path.join(self.data_path, f'PID.{patient_id}', f'{patient_id}.sorted.dedupe.recal.cram')

        if not os.path.exists(cram_path):
            self.log.error(f'Asked for {patient_id} CRAM file, but CRAM file does not exist (although it was reported to exist)')
            raise LookupError(f'Asked for {patient_id} CRAM file, but CRAM file does not exist (although it was reported to exist)')

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
        if not r: return False
        if len(r) != 1: raise Exception('Patient database returned more than one entry!')

        return True

    def add_patient(self,
        patient_id: str,
        seq_id: str,
        name: str,
        sex: str,
        age: int,
        ):
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
            'name': name,
            'age': age,
            'sex': sex,
            'analysis_done': 0,
            'date_added': datetime.datetime.now().isoformat(' '),
            'date_analysis': 'null',
            'data_dir': data_dir,
            }

        new_patient = '''INSERT INTO patients VALUES (:patient_id, :seq_id, :name, :age, :sex, :analysis_done, :date_added, :date_analysis, :data_dir)'''

        self.db_PID = sqlite3.connect(self.db_PID_path)
        self.db_PID_cursor = self.db_PID.cursor()
        self.db_PID_cursor.execute(new_patient, newpid_row)
        self.db_PID_cursor.execute('INSERT INTO summary_statistics VALUES (:patient_id, :seq_id, 0)', newpid_row)
        self.db_PID_cursor.execute('INSERT INTO patient_data VALUES (:patient_id, "0Gb", 0, 0, 0)', newpid_row)
        self.db_PID.commit()
        self.db_PID.close()

        if os.path.exists(data_dir):
            raise Exception(f'Trying to add {patient_id} but the data directory {data_dir} already exists')
        os.mkdir(data_dir)

        self.log.info(f'Added patient {patient_id}')

        return True

    def summary_statistics(self, patient_id:str, ):
        '''
        **Purpose**
            Return the summary statistics for the patient_id
        '''
        self.db_PID = sqlite3.connect(self.db_PID_path)
        self.db_PID_cursor = self.db_PID.cursor()
        r = self.db_PID_cursor.execute('SELECT * FROM summary_statistics WHERE pid=?', (patient_id, ))
        r = r.fetchall()
        self.db_PID.close()

        if not r: return False
        if len(r) != 1: raise Exception('Patient database returned more than one entry!')

        return r[0]

    def generate_report(self, mode:str, patient_id:str, search_term:str, lang='CN'):
        '''
        **Purpose**
            Generate a HTML report for patient_id and search_term

            Save the file into the ~/analysis/patient_id/patient_id.disease_code.pdf

        **Returns**
            Location of the saved HTML file
        '''
        assert mode in support.valid_genome_dbs, f'{mode} was not in {support.valid_genome_dbs.keys()}'

        # TODO: Pull language out of system settings DB

        # Get patient data;
        self.db_PID = sqlite3.connect(self.db_PID_path)
        self.db_PID_cursor = self.db_PID.cursor()
        self.db_PID_cursor.execute('SELECT name, age, sex FROM patients WHERE pid=?', (patient_id, ))
        patient_data = self.db_PID_cursor.fetchone()
        self.db_PID.close()

        # TODO: Check return
        patient_data = {'name': patient_data[0], 'age': patient_data[1], 'sex': patient_data[2]}

        self.db_disease_codes = sqlite3.connect(self.db_disease_codes_path)
        self.db_disease_codes_cursor = self.db_disease_codes.cursor()

        # Select the proper report generator:
        if mode == 'Pharma':
            # TODO: Fuzzy search
            self.db_disease_codes_cursor.execute('SELECT dis_code, desc_en, desc_cn FROM diseasecodes_pharma WHERE desc_en=? OR desc_cn=?', (search_term, search_term))
            res = self.db_disease_codes_cursor.fetchone()
            if not res:
                raise AssertionError(f'{search_term} was not found in diseasecodes_pharma database')

            disease_code = res[0]
            descEN = res[1]
            descCN = res[2]

            self.log.info(f'Search found: {disease_code}, {descEN}, {descCN}')

            rep = reporter_pharma.reporter_pharma(self.data_path, self.script_path, patient_id, patient_data, disease_code, descEN, descCN, self.log, lang)
            #html_file = rep.generate_html_file()
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

            rep = reporter_risk.reporter_risk(self.data_path, self.script_path, patient_id, patient_data, disease_code, descEN, descCN, self.log, lang)
            #html_file = rep.generate_html_file()
            html_file, html = rep.generate()

            html = ''

        self.db_disease_codes.close()

        return html_file, html
