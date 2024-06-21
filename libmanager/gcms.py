#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024 中基科生物保留所有权利
#
# Author(s):
#

import sys
import os
import pickle
import gzip
from . import tinyglbase
from . import pipeline_support

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

    def report_available(self, report_code: str) -> bool:
        if not self.rest: # No restrictions
            return True

        if report_code in self.get_rest():
            return True

        return False

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

def dbsnp_vcf_to_gcm(vcfgz_filename, gcm_filename):
    """

    ** Convert a dbCNP annotated VCF to a GCM file.

    Returns a GCM


    """
    assert os.path.exists(vcfgz_filename), f'{vcfgz_filename} file not found'

    gcm_data = {
        'qc': None,
        'full_logs': None,
        'pharma': None,
        'risk': None,
        'clinvar': None, # Not currently used.
        'rest': None,
        }

    # reverse is gzip.decompress(bytes_obj).decode()

    # QC
    gcm_data['qc'] = f'''
        No QC data is available for this GCM, as
        the GCM was generated using a pre-processed VCF file.
        '''

    # Full logs
    gcm_data['full_logs'] = gzip.compress(f'''
        No log data is available for this GCM, as
        the GCM was generated using a pre-processed VCF file.

        The file {vcfgz_filename} was converted to this GCM
        '''.encode())

    pharma, risk = pipeline_support.annotate_pharma_risk(vcfgz_filename)
    # pharma table
    gcm_data['pharma'] = gzip.compress(pharma.encode())

    # risk
    gcm_data['risk'] = gzip.compress(risk.encode())

    # clinvar
    #with open(f'{PID}.clinvar.pathogenic.tsv', 'rt') as f:
    gcm_data['clinvar'] = None

    # save the gcm
    with open(gcm_filename, "wb") as oh:
        pickle.dump(gcm_data, oh, -1)

    gcm = gcm_file(gcm_filename, logger=None)

    return gcm
