#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024
#
# Author(s):
# Andrew P. Hutchins
#

'''

Questions:
TODO: Deprecate

'''

import os
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

    def populate_patient_list(self, user:str) -> list:
        table = self.manager.get_patients_table(user)
        return table

    def populate_report_generator(self, mode:str, lang:str) -> list:
        """

        Returns the list of diseases or conditions for three modes:

        疾病与用药指导
        临床表型相关变异
        疾病风险提示

        返回三种模式的疾病或状况列表：

        """
        # Backend: Report Generator
        # Doctorend: Report Generator

        assert mode in support.valid_genome_dbs, f'{mode} not found'

        if mode == 'Pharma': # 疾病与用药指导
            return self.manager.get_pharma_table(lang)

        elif mode == 'ClinVAR': # 临床表型相关变异
            return [] # An empty list is a valid return

        elif mode == 'Risk': # 疾病风险提示
            return self.manager.get_risk_table(lang)

    def export_vcf(self, patient_id: str) -> str:
        """
        Returns the PATH to the VCF file for this patient, of None
        if the VCF is not avaialable.

        The 保存所选VCF button.

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

        The 保存所选CRAM button.

        """
        ###### Used in:
        # Backend: Report Generator
        # Backend: Patient Data Manager

        return self.manager.get_cram_path(patient_id)

    def generate_report(self, user: str, mode: str, patient_id: str, selected_report:str) -> str:
        '''
        Generates the reports and returns the PATH to the HTML file, and the HTML data.

        Best to serve the HTML, right?

        mode can be one of :

        'Pharma': 疾病与用药指导

        'ClinVAR': 临床表型相关变异

        'Risk': 疾病风险提示

        '''
        ###### Used in:
        # Backend: Report Generator
        # Doctorend: Report Generator

        assert mode in support.valid_genome_dbs, f'{mode} was not in {support.valid_genome_dbs.keys()}'

        return self.manager.generate_report(user, mode, patient_id, selected_report)

    def add_new_patient(self,
        user:str,
        patient_id: str,
        sequence_data_id: str,
        name: str,
        sex: str,
        age: int,):
        """
        Add new patient data.
        Used on the screen to register a new patient
        添加新的患者数据。
        用于在屏幕上注册新患者:
        添加新患者数据

        """
        # Backend: Add New Patient

        # Sanitise input;
        age = int(age)

        ret, sequence_data_path  = self.manager.add_patient(
            user=user,
            patient_id=patient_id,
            seq_id=sequence_data_id,
            name=name,
            sex=sex,
            age=age)

        return ret, sequence_data_path

    def delete_patient(self, patient_id:str) -> bool:
        """
        Delete patient.
        删除患者

        NOTE: Does nothing in DEMO
        不删除演示版本中的患者

        """
        # Backend: Analysis State
        # Backend: Patient Data Manager

        return True

    def export_QC_statistics(self, patient_id: str) -> str:
        """
        Returns the analysis summary as a string.
        Used on the Analysis summary page.

        以字符串形式返回分析摘要。
        用于分析摘要页面。 "分析总结".

        """
        # Backend: Analysis summary

        return "QC data summary will go here.\nAs a long text.\nIt's relatively short."

    def get_logs(self, patient_id:str) -> str:
        """
        Return all the log data.
        Launched by the button 查看分析日志
        and found on the page: 查看日志

        返回所有日志数据。
        通过按钮启动查看分析日志
        在页面上找到：查看日志

        """
        # Backend: Patient Data Manager

        return self.manager.get_logs(patient_id)

    def populate_patient_data_list(self) -> str:
        """

        Return the patient data table which includes the space used,
        wether the data is already packed, CRAM is available? VCF available.
        Used on the page: 患者数据管理

        Data is in the form:
        [
        [患者 ID, Space Used, Data packed?, CRAM?, VCF?],
        ...]
        返回包括所用空间的患者数据表，
        数据是否已经打包，CRAM是否可用？VCF可用。
        在页面上使用：患者数据管理
        """

        # Backend: Patient Data Manager
        table = self.manager.get_patients_data_table()
        return table

    def clean_free_space(self) -> bool:
        """

        The button: 清除缓存 on the 患者数据管理 page.

        NOTE: Does nothing in DEMO
        不删除演示版本中的患者

        """
        # Backend: Patient Data Manager

        # TODO: Clean up miscellaneous non-patient data files
        return True

    def clean_up_analysis(self, patient_id: str) -> str:
        # Backend: Patient Data Manager

        # Does nothing in the DEMO version.
        # TODO: Clean up patient data files
        return 'Clean up is complete'

    def set_system_doctor_setting(self, key:str, value:str) -> bool:
        """
        Set a system setting on: 系统设置 page
        """

        # Doctorend: System Settings

        return self.manager.settings.set_doctor_setting(key, value)

    def get_system_doctor_setting(self, key:str) -> str:
        """
        Get a system setting on: 系统设置 page
        """
        # Doctorend: System Settings

        return self.manager.settings.get_doctor_setting(key)

    def set_system_backend_setting(self, key:str, value:str) -> bool:
        """
        Set a system setting on: 系统设置 page
        """

        # Doctorend: System Settings

        return self.manager.settings.set_backend_setting(key, value)

    def get_system_backend_setting(self, key:str) -> str:
        """
        Get a system setting on: 系统设置 page
        """
        # Doctorend: System Settings

        return self.manager.settings.get_backend_setting(key)
