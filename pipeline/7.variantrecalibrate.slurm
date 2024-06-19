#!/usr/bin/env bash
#SBATCH --cpus-per-task=4
#SBATCH --partition=batch
#SBATCH -o variant_racalibrate.out
#SBATCH -N 1

HOME=$(echo ~)

hg38_ref_fasta=$(echo '$HOME/gcmtools/static_data/hg38_v0_20231023/Homo_sapiens_assembly38.fasta')
known_dbsnp=$(echo '$HOME/gcmtools/static_data/hg38_v0_20231023/Homo_sapiens_assembly38.dbsnp138.vcf')
known_indel=$(echo '$HOME/gcmtools/static_data/hg38_v0_20231023/Homo_sapiens_assembly38.known_indels.vcf.gz')
known_1000g=$(echo '$HOME/gcmtools/static_data/hg38_v0_20231023/Mills_and_1000G_gold_standard.indels.hg38.vcf.gz')
known_hapmap=$(echo '$HOME/gcmtools/static_data/hg38_v0_20231023/hapmap_3.3.hg38.vcf.gz')
known_omni=$(echo '$HOME/gcmtools/static_data/hg38_v0_20231023/1000G_omni2.5.hg38.vcf.gz')
known_1000g_snps=$(echo '$HOME/gcmtools/static_data/hg38_v0_20231023/1000G_phase1.snps.high_confidence.hg38.vcf.gz')

pwd=$(pwd)
PID=$(basename $pwd)

gatk --java-options "-Xmx8G -XX:+UseParallelGC -XX:ParallelGCThreads=4" \
	VariantRecalibrator \
	-R $hg38_ref_fasta \
	-V genotype.raw.vcf.gz \
	-O recalibrate_SNP.recal \
	--max-gaussians 6 \
	--tranches-file recalibrate_SNP.tranches \
	--rscript-file vqsr_snp_plots.R \
	-tranche 100.0 -tranche 99.9 -tranche 99.0 -tranche 90.0 \
	-resource:hapmap,known=false,training=true,truth=true,prior=15.0 $known_hapmap \
	-resource:omni,known=false,training=true,truth=true,prior=12.0 $known_omni \
	-resource:1000G,known=false,training=true,truth=false,prior=10.0 $known_1000g_snps \
	-resource:dbsnp,known=true,training=false,truth=false,prior=7.0 $known_dbsnp \
	-tranche 100.0 -tranche 99.95 -tranche 99.9 -tranche 99.8 -tranche 99.6 -tranche 99.5 -tranche 99.4 -tranche 99.3 -tranche 99.0 -tranche 98.0 -tranche 97.0 -tranche 90.0 \
    -an QD -an MQRankSum -an ReadPosRankSum -an FS -an MQ -an SOR -an DP \
	-mode SNP

# Above is from https://gatk.broadinstitute.org/hc/en-us/articles/360035531112--How-to-Filter-variants-either-with-VQSR-or-by-hard-filtering

echo Stage 7: VariantRecalibrator SNPs

gatk --java-options '-Xmx8g -XX:+UseParallelGC -XX:ParallelGCThreads=4' VariantRecalibrator \
	-R $hg38_ref_fasta \
   	-V genotype.raw.vcf.gz \
   	-O recalibrate_INDEL.recal \
	--max-gaussians 4 \
	--tranches-file recalibrate_INDEL.tranches \
	--rscript-file vqsr_indel_plots.R \
	-resource:mills,known=false,training=true,truth=true,prior=12.0 $known_indel  \
   	-resource:dbsnp,known=true,training=false,truth=false,prior=2.0 $known_dbsnp \
   	-an QD -an DP -an FS -an SOR -an ReadPosRankSum -an MQRankSum \
  	-mode INDEL 

echo Stage 7: VariantRecalibrator INDELs

#Rscript vqsr_snp_plots.R
#Rscript vqsr_indel_plots.R

gatk --java-options "-Xmx8G -XX:+UseParallelGC -XX:ParallelGCThreads=4" ApplyVQSR \
	-R $hg38_ref_fasta \
	-V genotype.raw.vcf.gz \
        -O $PID.recalibrated_snps_raw_indels.vcf.gz \
	--truth-sensitivity-filter-level 99.7 \
	--tranches-file recalibrate_SNP.tranches \
	--recal-file recalibrate_SNP.recal \
	--create-output-variant-index true \
        -mode SNP

echo Stage 7: ApplyVQSR SNPs

gatk --java-options "-Xmx8G -XX:+UseParallelGC -XX:ParallelGCThreads=4" ApplyVQSR \
	-R $hg38_ref_fasta \
	-V $PID.recalibrated_snps_raw_indels.vcf.gz \
	-O $PID.recalibrated_snps_recalibrated_indels.vcf.gz \
	--truth-sensitivity-filter-level 99.7 \
	--tranches-file recalibrate_INDEL.tranches \
	--recal-file recalibrate_INDEL.recal \
	-mode INDEL

echo Stage 7: Finished recalibrating

sleep 10 # Wait for any buffers
python runner.py
