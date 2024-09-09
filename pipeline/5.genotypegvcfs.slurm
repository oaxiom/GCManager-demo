#!/bin/sh
#SBATCH --cpus-per-task=2
#SBATCH --partition=batch
#SBATCH -N 1

DATA_PATH='/opt/seqanalysis/static_data'

bash_ref_fasta=$DATA_PATH/hg38_v0_20231023/Homo_sapiens_assembly38.fasta.gz

/opt/seqanalysis/bin/gatk --java-options "-Xmx7G -XX:ParallelGCThreads=2" \
	GenotypeGVCFs \
	-R $bash_ref_fasta \
	-L $chrom \
	-V called.$chrom.recal.g.vcf.gz \
	-O genotype.$chrom.vcf.gz

echo Stage 5: Genotyped chrom $chrom

sleep 10 # Wait for any buffers
python3 runner.py

