
import sys, gzip, glob

if len(sys.argv) != 2:
    print('Incorrect number of arguments. should be PID file only')
    sys.exit(-1)

print('Collecting QC')

PID = sys.argv[1]

def wc(filename, gziped):
    if gziped:
        oh = gzip.open(filename, 'rt')
    else:
        oh = open(filename, 'rt')
    for i, _ in enumerate(oh):
        pass
    oh.close()

    return i

outputs = {}

with open('read_count.txt', 'rt') as f:
    outputs['read_count'] = int(f.read().strip())

outputs['mapped_reads'] = 0
outputs['duplicates'] = 0
outputs['properly_paired'] = 0

for bams in glob.glob('*.sorted.dedupe.flagstat'):
    with open(bams, 'rt') as oh:
        # These numbers are *2, i.e. a single read is two pairs.
        _ = oh.readline() # total reads
        _ = oh.readline() # primary
        _ = oh.readline() # secondary
        _ = oh.readline() # supplementary
        outputs['duplicates'] += int(oh.readline().split(' ')[0]) //2 # duplicates
        _ = oh.readline() # primary duplicates
        outputs['mapped_reads'] += int(oh.readline().split(' ')[0]) //2 # mapped
        _ = oh.readline() # paired
        _ = oh.readline() # read1
        _ = oh.readline() # read2
        outputs['properly_paired'] += int(oh.readline().split(' ')[0]) //2 # properly paired
        _ = oh.readline()
        _ = oh.readline()
        _ = oh.readline()
        _ = oh.readline()
        _ = oh.readline()
        _ = oh.readline()


outputs['total_snps'] = wc(f'{PID}.recalibrated_snps_recalibrated_indels.vcf.gz', gziped=True)

outputs['total_annotated_snps'] = wc(f'{PID}.dbsnp.vcf.gz', gziped=True)

with open(f'{PID}.qc', 'wt') as oh:
    oh.write(f"Total number of input reads = {outputs['read_count']}\n")
    oh.write(f"Mapped reads = {outputs['mapped_reads']} ({(outputs['mapped_reads']/outputs['read_count']*100):.1f}%)\n")
    oh.write(f"Properly paired = {outputs['properly_paired']}\n")
    oh.write(f"Read duplicates = {outputs['duplicates']}\n")
    oh.write(f"Total number of SNPs = {outputs['total_snps']}\n")
    oh.write(f"Total annotated SNPs = {outputs['total_annotated_snps']}\n")

print('Finished collecting QC')
