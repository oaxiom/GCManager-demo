#!/bin/sh
#SPATCH --cpus-per-task=1
#SBATCH -J gathervcfs
#SBATCH -o gathervcfs.out

java -jar /export/unstable/picard-3.1.0/picard.jar \
	GatherVcfs \
	-O genotype.raw.vcf.gz \
	-I genotype.chr1.vcf.gz -I genotype.chr2.vcf.gz -I genotype.chr3.vcf.gz \
	-I genotype.chr4.vcf.gz -I genotype.chr5.vcf.gz -I genotype.chr6.vcf.gz \
	-I genotype.chr7.vcf.gz -I genotype.chr8.vcf.gz -I genotype.chr9.vcf.gz \
	-I genotype.chr10.vcf.gz -I genotype.chr11.vcf.gz -I genotype.chr12.vcf.gz \
	-I genotype.chr13.vcf.gz -I genotype.chr14.vcf.gz -I genotype.chr15.vcf.gz \
	-I genotype.chr16.vcf.gz -I genotype.chr17.vcf.gz -I genotype.chr18.vcf.gz \
	-I genotype.chr19.vcf.gz -I genotype.chr20.vcf.gz -I genotype.chr21.vcf.gz \
	-I genotype.chr22.vcf.gz 

# 	-I genotype.chrX.vcf -I genotype.chrY.vcf.gz -I genotype.chrM.vcf.gz O=merged.vcf.gzi

tabix genotype.raw.vcf.gz

echo Stage 6: Collected VCFs

sleep 10 # Wait for any buffers
python runner.py

