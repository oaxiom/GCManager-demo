#!/usr/bin/env bash
#SBATCH --cpus-per-task=2
#SBATCH --partition=batch
#SBATCH -N 1

PWD=$(pwd)
PID=$(basename $PWD)
DATA_PATH='/opt/seqanalysis/static_data'

bash_ref_fasta=$DATA_PATH/hg38_v0_20231023/Homo_sapiens_assembly38.fasta.gz

gvcffile=called.$chrom.recal.g.vcf.gz

bamfile=$PID.sorted.final.bam

# This approach is invalid for X and Y chromsomes.
# Need to use -ploidy and build separate models for male and female
/opt/seqanalysis/bin/gatk --java-options "-Xmx7G -XX:+UseParallelGC -XX:ParallelGCThreads=2" \
                HaplotypeCaller \
                -R $bash_ref_fasta \
                -I $bamfile \
                -L $chrom \
                -O $gvcffile \
                -G StandardAnnotation -G StandardHCAnnotation \
                -GQB 10 -GQB 20 -GQB 30 -GQB 40 -GQB 50 -GQB 60 -GQB 70 -GQB 80 -GQB 90 \
                --native-pair-hmm-threads 2 \
                -ERC GVCF
                #-stand-call-conf 10 # default is 30.0, as used by wdl pipeline;

echo Stage 4: Completed chrom $chrom

sleep 10 # Wait for any buffers
python3 runner.py

