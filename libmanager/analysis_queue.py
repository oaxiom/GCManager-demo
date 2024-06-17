#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024 中基科生物保留所有权利
#
# Author(s):
# Andrew P. Hutchins,
#

import sys
import os

class analysis_queue:
    def __init__(self, db_path, data_path, log):
        """
        **Purpose**
            Maintain the analysis queue, and run the analysis as required.

        """
        self.db_path = db_path
        self.data_path = data_path
        self.log = log

    def run(self):
        """
        **Purpose**
            Run the queue

        """
        pass
