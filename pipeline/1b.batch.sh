# This is for paired-end FASTQs:

for p1 in *_1.fastq.gz
do
	# This script would be better to sbatch each one
	base=$(basename $p1 _1.fastq.gz)
	p2=${p1%_1.fastq.gz}_2.fastq.gz

	echo Starting ... base \= $base \; p1 \= $p1 \; p2 \= $p2

	sbatch -J $base -o $base.align.out --export=ALL,base=$base,p1=$p1,p2=$p2 1b.align.slurm

done
