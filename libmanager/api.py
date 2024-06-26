#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024 中基科生物保留所有权利
#
# Author(s):
# Andrew P. Hutchins
#

import os
import glob
import shutil
from . import support

class api:
    """
    **Purpose**
        These days its more of an adjunct to libmanager

        TODO: Deprecate the simple generic functions

    """
    def __init__(self, manager, log, home_path):
        self.log = log
        self.home_path = home_path
        self.manager = manager

    def populate_patient_list(self, user:str) -> list:
        table = self.manager.get_patients_table(user)
        return table

    def populate_report_generator(self, mode:str, patient_id:str) -> list:
        """

        Returns the list of diseases or conditions for three modes:

        疾病与用药指导
        临床表型相关变异
        疾病风险提示

        返回三种模式的疾病或状况列表：

        """
        assert mode in support.valid_genome_dbs, f'{mode} not found'

        if mode == 'Pharma': # 疾病与用药指导
            return self.manager.get_pharma_table(patient_id)

        elif mode == 'ClinVAR': # 临床表型相关变异
            return [] # An empty list is a valid return

        elif mode == 'Risk': # 疾病风险提示
            return self.manager.get_risk_table(patient_id)

    def export_vcf(self, patient_id: str) -> str:
        """
        Returns the PATH to the VCF file for this patient, of None
        if the VCF is not avaialable.

        The 保存所选VCF button.

        """
        return self.manager.get_vcf_path(patient_id)

    def export_cram(self, patient_id: str) -> str:
        """
        Returns the PATH to the CRAM file for this patient, of None
        if the CRAM is not avaialable.

        The 保存所选CRAM button.

        """
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
        assert mode in support.valid_genome_dbs, f'{mode} was not in {support.valid_genome_dbs.keys()}'

        return self.manager.generate_report(user, mode, patient_id, selected_report)

    def add_new_patient(self,
        user:str,
        patient_id: str,
        sequence_data_id: str,
        name: str,
        sex: str,
        age: int,
        institution_sending: str):
        """
        Add new patient data.
        Used on the screen to register a new patient
        添加新的患者数据。
        用于在屏幕上注册新患者:
        添加新患者数据

        """
        # Sanitise input;
        age = int(age)

        ret, sequence_data_path, safe_patient_id  = self.manager.add_patient(
            user=user,
            patient_id=patient_id,
            seq_id=sequence_data_id,
            name=name,
            sex=sex,
            age=age,
            institution_sending=institution_sending)

        # Sends the sequence_data path back to the FAPI,
        # so it knows where to copy the data.

        return ret, sequence_data_path, safe_patient_id

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

        table = self.manager.get_patients_data_table()
        return table

    def clean_free_space(self, user:str) -> bool:
        """

        The button: 清除缓存 on the 患者数据管理 page.

        """
        # Clean cached reports
        for f in glob.glob(os.path.join(self.manager.data_path, '*/*.html')):
            os.remove(f)
            self.log.info(f'{user} deleted file {f}')

        # Remove backups > 10
        for idx, f in enumerate(reversed(sorted(list(glob.glob(os.path.join(self.manager.backup_path, f'db_backup-{self.manager.end_type}-*.tar.gz')))))):
            if idx > 10:
                os.remove(f)
                self.log.info(f'{user} deleted old backup {f}')

        self.log.info(f'{user} cleaned up all free space using clean cache')

        return True

    def clean_up_analysis(self, user:str, patient_id: str) -> str:
        # This is more for the backend;

        if not self.manager.analysis_complete(patient_id):
            # Don't clean an incomplete patient.
            return True

        for f in glob.glob(os.path.join(self.manager.data_path, f'PID.{patient_id}', '*.out')):
            os.remove(f)
            self.log.info(f'{user} deleted file {f}')

        # Clean up unneeded BAMS; VCFs; etc.
        return True

    def get_disk_space(self) -> int:
        disk_space = shutil.disk_usage(self.manager.data_path)
        percent = int((disk_space.used / disk_space.total) * 100)
        return percent # percentage

    def set_system_doctor_setting(self, key:str, value:str) -> bool:
        """
        Set a system setting on: 系统设置 page
        """
        return self.manager.settings.set_doctor_setting(key, value)

    def get_system_doctor_setting(self, key:str) -> str:
        """
        Get a system setting on: 系统设置 page
        """
        return self.manager.settings.get_doctor_setting(key)

    def set_system_backend_setting(self, key:str, value:str) -> bool:
        """
        Set a system setting on: 系统设置 page
        """
        return self.manager.settings.set_backend_setting(key, value)

    def get_system_backend_setting(self, key:str) -> str:
        """
        Get a system setting on: 系统设置 page
        """
        return self.manager.settings.get_backend_setting(key)
