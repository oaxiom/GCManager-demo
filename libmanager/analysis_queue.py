#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024 中基科生物保留所有权利
#
# Author(s):
# Andrew P. Hutchins,
#

import sys
import os
import shutil
import datetime
import time

class analysis_queue:
    def __init__(self, script_path, db_path, data_path, log):
        """
        **Purpose**
            Maintain the analysis queue, and run the analysis as required.

        """
        self.script_path = script_path
        self.db_path = db_path
        self.data_path = data_path
        self.log = log

        self.q = []

        self.currently_processing = None

    def _load_progress_txt_file(self, patient_id:str):
        with open(os.path.join(self.db_path, f'PID.{patient_id}', 'progress.txt')) as f:
            prog = f.read()

        res = {}
        for line in prog.split('\n'):
            if 'Stage' in line:
                line = line.split(' ')
            res[int(line[1].strip(':'))] = int(line[2].strip('%'))

        return res

    def analysis_progress(self, patient_id:str) -> dict:
        '''
        Get the analysis progress for this patient ID, I assume you checked it exists.
        '''
        # Do the simple case;
        if self._analysis_complete(patient_id):
            return {1: 100, 2: 100, 3: 100, 4: 100, 5: 100, 6: 100, 7: 100, 8: 100, 9: 100}

        # See if we can get it from the progress file left by runner.py
        if os.path.exists(os.path.join(self.db_path, f'PID.{patient_id}', 'progress.txt')):
            return self._load_progress_txt_file(patient_id)

        return # What to do?!?!

    def _analysis_complete(self, task: dict) -> bool:
        '''
        **Purpose**
            Check if the analysis is complete;

        '''
        # Probably best to check for the existence of the .data.gcm file
        if os.path.exists(task['gcm_path']):
            return True
        return False

    def add_task(self, patient_id:str):
        """

        Add a patient_id to the queue.

        """
        # copy runner to the correct location.
        shutil.copy(os.path.join(self.script_path, 'bin', 'runner.py'),
            os.path.join(self.db_path, f'PID.{patient_id}'))

        task = {
            'PID': patient_id,
            'added_to_q_time': time,
            'started_analysis': None,
            'analysis_path': os.path.join(self.db_path, f'PID.{patient_id}'),
            'gcm_path': os.path.join(self.db_path, f'PID.{patient_id}', f'PID.{patient_id}.data.gcm'),
            'runner_path': os.path.join(self.db_path, f'PID.{patient_id}', 'runner.py')
            }

        self.q.append(task)
        self.log.info(f'Added {patient_id} to the analysis queue')


    def run(self):
        """
        **Purpose**
            Run the queue

        """
        if not self.currently_processing:
            # Nothing running,
            if self.q:
                self.currently_processing = self.q.pop(0)

        if self.currently_processing:
            # Should run without waiting.
            subprocess.Popen(f'python {self.currently_processing["runner_path"]}', shell=True)
            self.currently_processing['started_analysis'] = time.time()

            if self.analysis_complete(self.currently_processing):
                self.currently_processing = None
                # there is ~5 mins between when run() will get called again.
                # I think it's reasonable to wait till we go around again.
                # This makes certain all buffers are flushed, etc.
                # Gives a chance for some background tasks to complete

        if self.currently_processing:
            self.log.info('Processed the analysis queue. There are {len(self.q)} items queuing, and {self.currently_processing["patient_id"]} is procesing')
        else:
            self.log.info('Processed the analysis queue. There are {len(self.q)} items queuing.')
