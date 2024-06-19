#!/bin/sh
#SBATCH --cpus-per-task=16
#SBATCH --partition=batch
#SBATCH -N 1

# This is for interleaved paired-end FASTQs:

bash_ref_fasta='/export/home/andrew/genome/hg38_v0_20231023/Homo_sapiens_assembly38.fasta'

pwd=$(pwd)
PID=$(basename $pwd)

echo Stage 1: Starting ... base \= $base\; PID \= $PID\;p1 \= $p1\; p2 \= $p2
num_reads=$(zcat $p1 | wc -l)
echo Stage 1: Number of reads = $num_reads

rg='@RG\\tID:'$base'\\tSM:'$PID'\\tPL:ILLUMINA'
echo RG = $rg

bwa_cmd="bwa mem -R $rg -K 100000000 -v 3 -t 8 -Y $bash_ref_fasta $p1 $p2"
echo $bwa_cmd
eval $bwa_cmd | samtools view -b - | samtools fixmate -m -@ 2 - - | samtools sort -@ 4 -m 4G - | samtools markdup -s -@ 2 -O bam - $base.sorted.dedupe.bam
#bwa mem -R \'"$rg"\' -K 100000000 -v 3 -t 8 -Y $bash_ref_fasta $p1 $p2 | samtools view -b - | samtools fixmate -m -@ 2 - - | samtools sort -@ 4 -m 4G - | samtools markdup -s -@ 2 -O bam - $base.sorted.dedupe.bam 
samtools index -@ 4 $base.sorted.dedupe.bam

samtools flagstat -@ 4 $base.sorted.dedupe.bam >$base.sorted.dedupe.flagstat

echo Stage 1: Aligned Read for sample $p1 $p2 # repalce with timer later

sleep 10 # Wait for any buffers
python runner.py

