#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024
#
# Author(s):
# Andrew P. Hutchins,
#

import os
import time

class analysis_progress:
    def __init__(self, log, home_path):
        self.log = log
        self.home_path = home_path
        self.patient_id = None

        self.last_timestamp = {}
        self.patients = {}
        self.current_stage = {}

    def report(self, patient_id:str) -> dict:
        '''
        **Purpose**
            returns the current progress as a dict, as percentages.
        '''
        # Do the setup;
        if patient_id not in self.patients:
            self.last_timestamp[patient_id] = time.time()
            self.current_stage[patient_id] = 1
            self.patients[patient_id] = {
                1: 0,
                2: 0,
                3: 0,
                4: 0,
                5: 0,
                6: 0,
                7: 0,
                8: 0,
                9: 0,
                }

        # simulate ongoing analysis;
        if self.current_stage[patient_id] == 10:
            return self.stage

        now_timestamp = time.time()

        delta = (now_timestamp - self.last_timestamp[patient_id]) // 0.6

        if delta >= 1:
            if self.patients[patient_id][self.current_stage[patient_id]] >= 100:
                self.patients[patient_id][self.current_stage[patient_id]] = 100
                self.current_stage[patient_id] += 1
            else:
                self.patients[patient_id][self.current_stage[patient_id]] += int(delta)

        if self.patients[patient_id][self.current_stage[patient_id]] >= 100:
            self.patients[patient_id][self.current_stage[patient_id]] = 100

        self.last_timestamp[patient_id] = time.time()

        return self.patients[patient_id]

    def _report():
        '''

        The real version can load a text file in the analysis directory.

        '''
        pass

