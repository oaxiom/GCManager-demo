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
import subprocess

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

    def _load_progress_txt_file(self, patient_id:str) -> dict:
        res = {}

        oh = open(os.path.join(self.data_path, f'PID.{patient_id}', 'progress.txt'))
        for line in oh:
            if line.startswith('Stage '):
                line = line.strip().split(' ')
                res[int(line[1].strip(':'))] = int(line[2].strip('%'))
        oh.close()

        return res

    def analysis_progress(self, patient_id:str) -> dict:
        '''
        Get the analysis progress for this patient ID, I assume you checked it exists.
        '''
        # See if we can get it from the progress file left by runner.py
        if os.path.exists(os.path.join(self.data_path, f'PID.{patient_id}', 'progress.txt')):
            return self._load_progress_txt_file(patient_id)

        # If no progress.txt, it's probably not started.
        return {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0}

    def _analysis_complete(self, task: dict) -> bool:
        '''
        **Purpose**
            Check if the analysis is complete;

        '''
        # Probably best to check for the existence of the .data.gcm file
        if os.path.exists(task['gcm_path']):
            # TODO: Check file size is not zero
            return True

        if os.path.exists(os.path.join(task['analysis_path'], 'FATALERROR.out')): # This is a tag left by runner to say we failed.
            return True

        return False

    def patient_is_on_the_task_list(self, patient_id:str) -> bool:
        """
        Return if the patient is on the analysis queue.

        """
        for t in self.q:
            if t['PID'] == patient_id:
                return True

        return False

    def patient_is_currently_processing(self, patient_id:str) -> bool:
        if not self.currently_processing: # No one on the queue
            return False

        if patient_id == self.currently_processing["PID"]:
            return True
        return False

    def add_task(self, patient_id:str):
        """

        Add a patient_id to the queue.

        """
        # Check that the patient_id is not already on the queue:
        for task in self.q:
            if task['PID'] == patient_id:
                # We are already on the queue, don't add twice!
                self.log.info(f"Tried to add {patient_id} but it's already on the queue")
                return True

        # copy runner to the correct location.
        shutil.copy(os.path.join(self.script_path, 'bin', 'runner.py'),
            os.path.join(self.data_path, f'PID.{patient_id}'))

        self._copy_all_pipeline_scripts(os.path.join(self.data_path, f'PID.{patient_id}'))

        task = {
            'PID': patient_id,
            'time_on_q': time.time(),
            'time_started_analysis': None,
            'analysis_path': os.path.join(self.data_path, f'PID.{patient_id}'),
            'gcm_path': os.path.join(self.data_path, f'PID.{patient_id}', f'PID.{patient_id}.data.gcm'),
            'runner_path': os.path.join(self.data_path, f'PID.{patient_id}', 'runner.py')
            }

        self.q.append(task)
        self.log.info(f'Added {patient_id} to the analysis queue')

        return True

    def _copy_all_pipeline_scripts(self, path):
        all_files = os.listdir(os.path.join(self.script_path, 'pipeline/'))
        for f in all_files:
            src_path = os.path.join(self.script_path, 'pipeline', f)
            if os.path.isfile(src_path):
                dst_path = os.path.join(path, f)
                shutil.copy(src_path, dst_path)

    def __sweeper(self):
        """
        If the q is idle, go through all PIDs, and attempt to re-add to the queue
        python runner.py if full_logs.

        """
        # Paranoia!
        if self.currently_processing:
            return

        if self.q:
            return

        self.log.info('Started sweeper')

        for pid_path in glob.glob(os.path.join(self.data_path, 'PID.*'):
            if os.path.exists(os.path.join(pid_path, 'full_logs.out.gz')):
                # Irrecoverable, also likely a fatal error
                continue
            if os.path.exists(os.path.join(pid_path, 'FATALERROR.out')):
                # Irrecoverable
                continue

            # More tests?
            patient_id = os.path.split(pid_path)[1][4:] # Can't use split or lstrip, or anything.

            self.log.info(f'Sweeper is attempting to rescue {patient_id}')
            self.add_task(patient_id) # re-add it to the queue.

        return

    def run(self):
        """
        **Purpose**
            Run the queue

        """
        if not self.currently_processing:
            # Nothing running
            if self.q:
                self.currently_processing = self.q.pop(0)
                self.currently_processing['time_started_analysis'] = time.time()
                self.log.info(f'Started analysing {self.currently_processing["PID"]}')
            else:
                self.__sweeper()

        if self.currently_processing:
            # Should run without waiting.
            subprocess.Popen(f'python3 {self.currently_processing["runner_path"]}',
                cwd=self.currently_processing["analysis_path"],
                shell=True)

            if self._analysis_complete(self.currently_processing):
                # there is ~5 mins between when run() will get called again.
                # I think it's reasonable to wait till we go around again.
                # This makes certain all buffers are flushed, etc.
                # Gives a chance for some background tasks to complete
                finished_PID = self.currently_processing['PID']
                time_taken = int(time.time() - self.currently_processing['time_started_analysis'])
                time_on_q = int(self.currently_processing['time_started_analysis'] - self.currently_processing['time_on_q'])
                self.log.info(f'{finished_PID}, analysis is complete, took {time_taken//60:,} minutes and spent {time_on_q//60:,} minutes on the queue.')
                self.currently_processing = None # blank so a new task can be grabbed
                return finished_PID # message back that PID is done;
            else:
                # This would be the place to check and see if the analysis has stalled.
                pass

        if self.currently_processing:
            self.log.info(f'Processed the analysis queue. There are {len(self.q)} items queuing, and {self.currently_processing["PID"]} is procesing')
        else:
            self.log.info(f'Processed the analysis queue. There are {len(self.q)} items queuing.')

        return True
