#!/usr/bin/env bash
#SBATCH --cpus-per-task=1
#SBATCH --partition=batch
#SBATCH -N 1

PWD=$(pwd)
PID=$(basename $PWD)
HOME=$(echo ~)

bash_ref_fasta=$(echo '$HOME/gcmtools/static_data/hg38_v0_20231023/Homo_sapiens_assembly38.fasta')
interval_list=$(echo '$HOME/gcmtools/static_data/hg38_v0_20231023/wgs_coverage_regions.hg38.interval_list')
knwon_dbsnp=$(echo '$HOME/gcmtools/static_data/hg38_v0_20231023/Homo_sapiens_assembly38.dbsnp138.vcf')
known_indel=$(echo '$HOME/gcmtools/static_data/hg38_v0_20231023/Homo_sapiens_assembly38.known_indels.vcf.gz')
known_1000g=$(echo '$HOME/gcmtools/static_data/hg38_v0_20231023/Mills_and_1000G_gold_standard.indels.hg38.vcf.gz')

gvcffile=called.$chrom.recal.g.vcf.gz

bamfile=$PID.sorted.final.bam

# This approach is invalid for X and Y chromsomes.
# Need to use -ploidy and build separate models for male and female
gatk --java-options "-Xmx40G -XX:+UseParallelGC -XX:ParallelGCThreads=1" \
                HaplotypeCaller \
                -R $bash_ref_fasta \
                -I $bamfile \
                -L $chrom \
                -O $gvcffile \
                -G StandardAnnotation -G StandardHCAnnotation \
                -GQB 10 -GQB 20 -GQB 30 -GQB 40 -GQB 50 -GQB 60 -GQB 70 -GQB 80 -GQB 90 \
                --native-pair-hmm-threads 1 \
                -ERC GVCF
                #-stand-call-conf 10 # default is 30.0, as used by wdl pipeline;

echo Stage 4: Completed chrom $chrom

sleep 10 # Wait for any buffers
python runner.py

