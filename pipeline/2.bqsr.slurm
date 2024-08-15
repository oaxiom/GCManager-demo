#!/usr/bin/env bash
#SBATCH --partition=batch
#SBATCH -N 1

HOME=$(echo ~)

bash_ref_fasta=$HOME/gcm/static_data/hg38_v0_20231023/Homo_sapiens_assembly38.fasta
interval_list=$HOME/gcm/static_data/hg38_v0_20231023/wgs_coverage_regions.hg38.interval_list
knwon_dbsnp=$HOME/gcm/static_data/hg38_v0_20231023/Homo_sapiens_assembly38.dbsnp138.vcf
known_indel=$HOME/gcm/static_data/hg38_v0_20231023/Homo_sapiens_assembly38.known_indels.vcf.gz
known_1000g=$HOME/gcm/static_data/hg38_v0_20231023/Mills_and_1000G_gold_standard.indels.hg38.vcf.gz

bqfile=${bamfile%.bam}.recal_data.table
recalfile=${bamfile%.bam}.recal.bam

echo Stage 2: Starting BQSR for $bamfile

# Base Calibrator and ApplyBQSR are fast
# Online docs suggerst this may be a problem if the data is large enough.
gatk --java-options "-Xmx20G -XX:+UseParallelGC -XX:ParallelGCThreads=4" \
                BaseRecalibrator \
                -L $interval_list \
                -R $bash_ref_fasta \
                -I $bamfile \
                --known-sites $knwon_dbsnp \
		        --known-sites $known_indel \
		        --known-sites $known_1000g \
                -O $bqfile

gatk --java-options "-Xmx8G -XX:+UseParallelGC -XX:ParallelGCThreads=4" \
                ApplyBQSR -R $bash_ref_fasta \
                -I $bamfile \
                -L $interval_list \
                -bqsr $bqfile \
                --static-quantized-quals 10 --static-quantized-quals 20 --static-quantized-quals 30 \
	       	    -O $recalfile

#rm $bamfile

echo Stage 2: Done BQSR for $bamfile

sleep 10 # Wait for any buffers
python3 runner.py

