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

        assert mode in ('pharma', 'clinvar', 'risk'), f'{mode} not found'

        if mode == 'pharma':
            return self.manager.get_pharma_table()
        elif mode == 'clinvar':
            return [] # An empty list is a valid return
        elif mode == 'risk':
            return self.manager.get_risk_table()

    def export_vcf(self, patient_id: str) -> str:
        # Backend: Report Generator
        # Backend: Patient Data Manager
        # Doctorend: Report Generator

        return self.manager.get_vcf_path(patient_id)

    def export_cram(self, patient_id: str) -> str:
        # Backend: Report Generator
        # Backend: Patient Data Manager

        return self.manager.get_cram_path(patient_id)

    def export_report(self, patient_id: str, selected_report:str) -> str:
        # Backend: Report Generator
        # Doctorend: Report Generator

        return self.manager.generate_report(patient_id, selected_report)

    def print_report(self, patient_id: str, selected_report_id: str):
        # Backend: Report Generator
        # Doctorend: Report Generator

        """
        Not required? Just use the web browser HTML -> PDF function?

        """

        return None

    def add_new_patient(self, patient_id: str, sequence_data_id: str, sequence_data_files: str):
        # Backend: Add New Patient

        return None

    def report_current_anaylsis_stage(self, patient_id:str):
        # Backend: Analysis State

        return None

    def delete_patient(self, patient_id:str):
        # Backend: Analysis State
        # Backend: Patient Data Manager

        return None

    def export_QC_statistics(self, patient_id: str):
        # Backend: Analysis summary

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
