#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024
#
# Author(s):
#

import pickle
import gzip
from . import tinyglbase

# TODO: Store the analysis date in the gcm file

class gcm_file:
    def __init__(self, filename, logger):
        with open(filename, 'rb') as oh:
            gcm = pickle.load(oh)

        self.logger = logger

        self.logs = gcm['full_logs']
        self.qc = gcm['qc']
        self.pharma = gcm['pharma']
        self.risk = gcm['risk']
        self.clinvar = gcm['clinvar']

        # Repack as tinyglbase objects on demand

    def get_logs(self):
        return gzip.decompress(self.logs).decode()

    def get_qc(self):
        return str(self.qc)

    def get_pharma(self):
        decoded = gzip.decompress(self.pharma).decode().split('\n')
        splited = [l.split('\t') for l in decoded if l if 'genotype' not in l]

        gl = tinyglbase.genelist(log=self.logger, format=True)
        gl.load_list([{'SNP': l[1], 'patient_genotype': l[2]} for l in splited])
        return gl

    def get_risk(self):
        # Risk table
        decoded = gzip.decompress(self.risk).decode().split('\n')
        splited = [l.split('\t') for l in decoded if l if 'genotype' not in l]

        gl = tinyglbase.genelist(log=self.logger, format=True)
        gl.load_list([{'SNPS': l[1], 'patient_genotype': l[2]} for l in splited]) # Don't need chrom
        return gl

    def get_clinvar(self):
        decoded = gzip.decompress(self.clinvar).decode().split('\n')
        splited = [l.split('\t') for l in decoded if l]

        # TODO: This is not accurate;

        gl = tinyglbase.genelist(log=self.logger, format=True)
        gl.load_list([{'chrom': l[0], 'rsid': l[1], 'genotype': l[2]} for l in splited])
        return gl

