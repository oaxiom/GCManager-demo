#!/bin/sh
#SBATCH --partition=batch
#SBATCH -N 1

# This is for interleaved paired-end FASTQs:

DATA_PATH='/opt/seqanalysis/static_data'
bash_ref_fasta=$(echo '$DATA_PATH/hg38_v0_20231023/Homo_sapiens_assembly38.fasta.gz')

pwd=$(pwd)
PID=$(basename $pwd)

echo Stage 1: Starting ... base \= $base\; PID \= $PID\;p1 \= $p1\; p2 \= $p2
num_reads=$(zcat $p1 | wc -l)
echo Stage 1: Number of reads = $num_reads

rg='@RG\\tID:'$base'\\tSM:'$PID'\\tPL:ILLUMINA'
echo RG = $rg

bwa_cmd="/opt/seqanalysis/bin/bwa mem -R $rg -K 100000000 -v 3 -t $NPROC -Y $bash_ref_fasta $p1 $p2"
echo $bwa_cmd
eval $bwa_cmd | /opt/seqanalysis/bin/samtools view -b - | /opt/seqanalysis/bin/samtools fixmate -m -@ 1 - - | /opt/seqanalysis/bin/samtools sort -@ 2 -m 2G - | /opt/seqanalysis/bin/samtools markdup -s -@ 2 -O bam - $base.sorted.dedupe.bam
/opt/seqanalysis/bin/samtools index -@ 1 $base.sorted.dedupe.bam

/opt/seqanalysis/bin/samtools flagstat -@ 2 $base.sorted.dedupe.bam >$base.sorted.dedupe.flagstat

echo Stage 1: Aligned Read for sample $p1 $p2 # repalce with timer later

sleep 10 # Wait for any buffers
python3 runner.py

