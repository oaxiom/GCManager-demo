#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024
#
# Author(s):
#

import pickle
import gzip
from . import tinyglbase

class gcm_file:
    def __init__(self, filename, log):
        with open(filename, 'rb') as oh:
            gcm = pickle.load(oh)

        self.logs = gcm['full_logs']
        self.qc = gcm['qc']
        self.pharma = gzip.decompress(gcm['pharma']).decode()
        self.risk = gzip.decompress(gcm['risk']).decode()
        self.clinvar = gzip.decompress(gcm['clinvar']).decode()

        # Repack as tinyglbase objects on demand

    def get_logs(self):
        return self.logs

    def get_qc(self):
        return self.qc

    def get_pharma(self):
        gl = tinyglbase.genelist(log=log, format=True)
        gl.load_list()
        return self.pharma

    def get_risk(self):
        gl = tinyglbase.genelist(log=log, format=True)
        gl.load_list()
        return self.risk

    def get_clinvar(self):
        gl = tinyglbase.genelist(log=log, format=True)
        gl.load_list()
        return self.clinvar

