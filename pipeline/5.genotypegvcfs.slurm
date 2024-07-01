#!/bin/sh
#SBATCH --cpus-per-task=2
#SBATCH --partition=batch
#SBATCH -N 1

HOME=$(echo ~)

bash_ref_fasta=$HOME/gcm/static_data/hg38_v0_20231023/Homo_sapiens_assembly38.fasta

gatk --java-options "-Xmx30G -XX:ParallelGCThreads=2" \
	GenotypeGVCFs \
	-R $bash_ref_fasta \
	-L $chrom \
	-V called.$chrom.recal.g.vcf.gz \
	-O genotype.$chrom.vcf.gz

echo Stage 5: Genotyped chrom $chr

sleep 10 # Wait for any buffers
python runner.py

