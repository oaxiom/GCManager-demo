#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024
#
# Author(s):
# Andrew P. Hutchins,
#

stages = {
        1: 'Align reads to genome',
        2: 'BQSR correct',
        3: 'Merge BAMs',
        4: 'Haplotype',
        5: 'Genotype',
        6: 'Gather VCFs',
        7: 'Recalibrate',
        8: 'Finished',
        }
