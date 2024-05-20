#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024
#
# Author(s):
# Andrew P. Hutchins,
#

import logging

valid_laguages = {
    'EN': 'English',
    'CN': '简体中文',
    }

valid_genome_dbs = {
    'Pharma': '疾病与用药指导', # 'Drug-genome associations',
    'ClinVAR': '临床表型相关变异',
    'Risk': '疾病风险提示',
    }

def prepare_logging():
    logging.basicConfig(level=logging.DEBUG,
        format='%(levelname)-8s: %(message)s',
        datefmt='%m-%d %H:%M')

    return logging.getLogger(f'GCmanager')
