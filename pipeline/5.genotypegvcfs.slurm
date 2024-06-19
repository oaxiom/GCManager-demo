#!/bin/sh
#SBATCH --cpus-per-task=4
#SBATCH --partition=batch
#SBATCH -N 1

bash_ref_fasta='/export/home/andrew/genome/hg38_v0_20231023/Homo_sapiens_assembly38.fasta'
interval_list='/export/home/andrew/genome/hg38_v0_20231023/wgs_coverage_regions.hg38.interval_list'
knwon_dbsnp='/export/home/andrew/genome/hg38_v0_20231023/Homo_sapiens_assembly38.dbsnp138.vcf'
known_indel='/export/home/andrew/genome/hg38_v0_20231023/Homo_sapiens_assembly38.known_indels.vcf.gz'
known_1000g='/export/home/andrew/genome/hg38_v0_20231023/Mills_and_1000G_gold_standard.indels.hg38.vcf.gz'

gatk --java-options "-Xmx30G -XX:ParallelGCThreads=4" \
	GenotypeGVCFs \
	-R $bash_ref_fasta \
	-L $chrom \
	-V called.$chrom.recal.g.vcf.gz \
	-O genotype.$chrom.vcf.gz

echo Stage 5: Genotyped chrom $chr

sleep 10 # Wait for any buffers
python runner.py

