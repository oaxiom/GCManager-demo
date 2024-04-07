#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024
#
# Author(s):
# Andrew P. Hutchins,
#

import os, datetime

class analysis_progress:
    def __init__(self, log, home_path):
        self.log = log
        self.home_path = home_path
        self.patient_id = None

    def update(self, alignment, raw_call, merge, calibrate, annotate):
        '''
        **Purpose**
            Update the current statuses.
        '''
        oh = open(self.filename, 'wt')
        oh.write('{alignment:.0f}\n{raw_call:.0f}\n{merge:.0f}\n{calibrate:.0f}\n{annotate:.0f}\n')
        oh.close()

    def report(self):
        '''
        **Purpose**
            returns the current progress as a dict, as percentages.
        '''
        oh = open(self.filename, 'rt')

        return {
            'alignment': oh.readline(),
            'raw_call': oh.readline(),
            'merge': oh.readline(),
            'calibrate': oh.readline(),
            'annotate': oh.readline(),
            }

    def add_patient(self, patient_id:str, data_dir:str):
        self.patient_id = patient_id
        self.data_dir = data_dir

        self.filename = os.path.join(data_dir, "progress.txt")

        oh = open(self.filename, 'wt')
        oh.write('0\n0\n0\n0\n0\n')
        oh.close()
