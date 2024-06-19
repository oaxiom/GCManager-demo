#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024 中基科生物保留所有权利
#
# Author(s):
# Andrew P. Hutchins,
#

import os
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

stages = {
        1: 'Align reads to genome',
        2: 'BQSR correct',
        3: 'Merge BAMs',
        4: 'Haplotype',
        5: 'Genotype',
        6: 'Gather VCFs',
        7: 'Recalibrate',
        8: 'Annotate SNPs',
        9: 'Finished',
        }
