#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024
#
# Author(s):
# Andrew P. Hutchins
#

'''

Questions:
1. Is this running continuously, or invoked only when needed?

'''

import os, sqlite3, datetime, logging
from . import analysis_progress
from . import support

class api:
    """
    **Purpose**
        Exposed API for web front end

    """
    def __init__(self, manager, log, home_path):
        self.log = log
        self.home_path = home_path
        self.log.info("Started API")
        self.manager = manager

    def populate_patient_list(self) -> list:
        # Backend: Front Page
        # Doctorend: Front Page

        #TODO: Enable fuzzy searching

        table = self.manager.get_patients_table()

        # Returns a list of tuples,
        return table

    def populate_report_generator(self, mode) -> list:
        # Backend: Report Generator
        # Doctorend: Report Generator

        assert mode in support.valid_genome_dbs, f'{mode} not found'

        if mode == 'Pharma': # 疾病与用药指导
            return self.manager.get_pharma_table()

        elif mode == 'ClinVAR': # 临床表型相关变异
            return [] # An empty list is a valid return

        elif mode == 'Risk': # 疾病风险提示
            return self.manager.get_risk_table()


    def export_vcf(self, patient_id: str) -> str:
        """
        Returns the PATH to the CRAM file for this patient, of None
        if the CRAM is not avaialable.

        """
        ###### Used in:
        # Backend: Report Generator
        # Backend: Patient Data Manager
        # Doctorend: Report Generator

        return self.manager.get_vcf_path(patient_id)

    def export_cram(self, patient_id: str) -> str:
        """
        Returns the PATH to the CRAM file for this patient, of None
        if the CRAM is not avaialable.

        """
        ###### Used in:
        # Backend: Report Generator
        # Backend: Patient Data Manager

        return self.manager.get_cram_path(patient_id)

    def generate_report(self, mode: str, patient_id: str, selected_report:str) -> str:
        '''
        Generates the reports and returns the PATH to the HTML file.

        mode can be one of :
        if mode == 'Pharma': # 疾病与用药指导
        elif mode == 'ClinVAR': # 临床表型相关变异
        elif mode == 'Risk': # 疾病风险提示

        '''
        ###### Used in:
        # Backend: Report Generator
        # Doctorend: Report Generator

        assert mode in support.valid_genome_dbs, f'{mode} was not in {support.valid_genome_dbs.keys()}'

        return self.manager.generate_report(mode, patient_id, selected_report)

    def print_report(self, patient_id: str, selected_report_id: str):
        # Backend: Report Generator
        # Doctorend: Report Generator

        """
        Not required? Just use the web browser HTML -> PDF function?

        """
        return None

    def add_new_patient(self, patient_id: str,
        sequence_data_id: str,
        name: str,
        age: int,
        sex: str,
        sequence_data_files: str):
        # Backend: Add New Patient

        # Sanitise input;
        age = int(age)

        return None

    def report_current_anaylsis_stage(self, patient_id:str):
        # Backend: Analysis State

        return None

    def delete_patient(self, patient_id:str):
        # Backend: Analysis State
        # Backend: Patient Data Manager

        # NOTE: Does nothing in DEMO
        return None

    def export_QC_statistics(self, patient_id: str):
        # Backend: Analysis summary

        # NOTE: Does nothing in DEMO
        return None

    def get_logs(self, patient_id:str) -> str:
        # Backend: Patient Data Manager

        return self.manager.get_logs(patient_id)

    def populate_patient_data_list(self) -> str:
        # Backend: Patient Data Manager
        table = self.manager.get_patients_data_table()
        return table

    def clean_free_space(self) -> bool:
        # Backend: Patient Data Manager

        # Does nothing in the DEMO version.
        # TODO: Clean up miscellaneous non-patient data files
        return True

    def clean_up_analysis(self, patient_id: str) -> bool:
        # Backend: Patient Data Manager

        # Does nothing in the DEMO version.
        # TODO: Clean up patient data files
        return None

    def convert_bam_to_cram(self):
        # Backend: Patient Data Manager

        # Does nothing in DEMO
        # TODO:
        return None

    def set_system_doctor_setting(self, key, value):
        # Doctorend: System Settings

        return self.manager.settings.set_doctor_setting(key, value)

    def get_system_doctor_setting(self, key) -> str:
        # Doctorend: System Settings

        return self.manager.settings.get_doctor_setting(key)
