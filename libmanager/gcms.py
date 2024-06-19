#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024 中基科生物保留所有权利
#
# Author(s):
#

import pickle
import gzip
from . import tinyglbase

# TODO: Store the analysis date in the gcm file

safe_builtins = {} # i.e. None.

class RestrictedUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        # Only allow safe classes from builtins.
        if module == "builtins" and name in safe_builtins:
            return getattr(builtins, name)
        # Forbid everything else.
        raise pickle.UnpicklingError("global '%s.%s' is forbidden" % (module, name))

class gcm_file:
    def __init__(self, filename, logger):
        with open(filename, 'rb') as oh:
            gcm = RestrictedUnpickler(oh).load()

        self.logger = logger

        self.logs = gcm['full_logs']
        self.qc = gcm['qc']
        self.pharma = gcm['pharma']
        self.risk = gcm['risk']
        self.clinvar = gcm['clinvar']
        if 'rest' in gcm: # TODO: deprecate as more gcms are upgraded.
            self.rest = gcm['rest']
        else:
            self.rest = None

        # Repack as tinyglbase objects on demand

    def get_rest(self):
        if self.rest:
            return set(self.rest)
        return None

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

    def save(self, filename):
        # Pack the gcm back out to a normal gcm file;

        gcm_data = {
            'qc': self.qc,
            'full_logs': self.logs,
            'pharma': self.pharma,
            'risk': self.risk,
            'clinvar': self.clinvar, # Not currently used.
            'rest': self.rest,
            }

        with open(filename, "wb") as oh:
            pickle.dump(gcm_data, oh, -1)
