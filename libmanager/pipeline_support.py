#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024 中基科生物保留所有权利
#
# Author(s):
#
# TODO: To port into the pipeline

import os
import gzip

def annotate_pharma_risk(vcffile):
    ##### Get the key snps
    key_snps_pharma = []
    with open(os.path.expanduser('../static_data/PharmaGKB/key_snps.txt'), 'rt') as oh:
        for line in oh:
            key_snps_pharma.append(line.strip())
    key_snps_pharma = set(key_snps_pharma)

    key_snps_risk = []
    with open(os.path.expanduser('../static_data/Risk/key_snps.txt'), 'rt') as oh:
        for line in oh:
            key_snps_risk.append(line.strip())
    key_snps_risk = set(key_snps_risk)

    print(f'Loaded {len(key_snps_pharma):,} Pharama-associated SNPs')
    print(f'Loaded {len(key_snps_risk):,} Risk-associated SNPs')

    results_pharma = []
    results_risk = []

    vcf = gzip.open(vcffile, 'rt')
    for lineno, line in enumerate(vcf):
        if (lineno + 1) % 1e6 == 0:
            print(f'{lineno+1:,}')

        if line[0] == '#':
            continue

        t = line.split('\t')

        rsid = t[2]
        if rsid in key_snps_pharma:
            results_pharma.append(t)
        if rsid in key_snps_risk:
            results_risk.append(t)

    vcf.close()

    print(f'Found {len(results_pharma):,} Pharma-associated matches')
    print(f'Found {len(results_risk):,} Risk-associated matches')

    output_pharma = 'chrom\trsid\tgenotype\n'
    for r in results_pharma:
        # Format the results into a PharmaGKB-style
        chrom = r[0]
        pos = r[1]
        rsid = r[2]
        ref_allele = r[3]
        alt_allele = r[4]
        alleles = r[9].split(':')[0]

        if alleles == '1/1':
            genotype = f'{alt_allele}{alt_allele}'
        elif alleles == '1|1': # !?!
            genotype = f'{alt_allele}{alt_allele}'
        elif alleles == '0/1':
            genotype = f'{ref_allele}{alt_allele}'
        elif alleles == '0|1': # Possible a 1|0?
            # The genotype is phased, and is matching. But, for our purposes,
            # We cna assume REF/ALT
            genotype = f'{ref_allele}{alt_allele}'
        else:
            print('phasing not found', alleles)
            print(r)

        output_pharma += f'{chrom}\t{rsid}\t{genotype}\n'

    output_risk = 'chrom\trsid\tgenotype\n'
    for r in results_risk:
        # Format the results into a PharmaGKB-style
        chrom = r[0]
        pos = r[1]
        rsid = r[2]
        ref_allele = r[3]
        alt_allele = r[4]
        alleles = r[9].split(':')[0]

        if alleles == '1/1':
            genotype = f'{alt_allele}{alt_allele}'
        elif alleles == '1|1': # !?!
            genotype = f'{alt_allele}{alt_allele}'
        elif alleles == '0/1':
            genotype = f'{ref_allele}{alt_allele}'
        elif alleles == '0|1': # Possible a 1|0?
            # The genotype is phased, and is matching. But, for our purposes,
            # We cna assume REF/ALT
            genotype = f'{ref_allele}{alt_allele}'
        else:
            print('phasing not found', alleles)
            print(r)

        output_risk += f'{chrom}\t{rsid}\t{genotype}\n'

    return output_pharma, output_risk
