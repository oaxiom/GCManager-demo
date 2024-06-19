
import sys, os, subprocess, gzip
#TODO: tinyglbase
#from glbase3 import genelist, glload

if len(sys.argv) != 2:
    print('Incorrect number of arguments. should be PID file only')
    sys.exit(-1)

PID = sys.argv[1]

##### Get the key snps
key_snps = []
oh = open(os.path.expanduser('~/static_data/PharmaGKB/key_snps.txt'), 'rt')
for line in oh:
    key_snps.append(line.strip())
oh.close()
key_snps = set(key_snps)

print(f'Loaded {len(key_snps):,} SNPs')

results = []

vcf = gzip.open(f'{PID}.gatk.dbsnp.vcf.gz', 'rt')
for lineno, line in enumerate(vcf):
    if (lineno + 1) % 1e6 == 0:
        print(f'{lineno+1:,}')

    if line[0] == '#':
        continue

    t = line.split('\t')

    rsid = t[2]
    if rsid not in key_snps:
        continue

    results.append(t)

print(f'Found {len(results):,} matches')

output = open(f'{PID}.pharmagkb.txt', 'wt')
output.write(f'chrom\trsid\tgenotype\n')
for r in results:
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

    output.write(f'{chrom}\t{rsid}\t{genotype}\n')

output.close()



print('Stage 8: Finished PharmaGKB')
