#!/bin/sh
#SBATCH --partition=batch
#SBATCH -N 1
#SBATCH --output merge_bams.out 

pwd=$(pwd)
PID=$(basename $pwd)

echo Stage 3: Merging BAMs to $PID.sorted.final.bam

/opt/seqanalysis/bin/samtools merge -@ 2 -o $PID.sorted.final.bam *.sorted.dedupe.recal.bam
/opt/seqanalysis/bin/samtools index $PID.sorted.final.bam

echo Stage 3: Done Merging

sleep 10 # Wait for any buffers
python3 runner.py
