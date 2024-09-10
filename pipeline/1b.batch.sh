# This is for paired-end FASTQs:

NPROCall=$(nproc)
NPROCm=$(($NPROCall-1))

for p1 in *_1.fastq.gz
do
	# This script would be better to sbatch each one
	base=$(basename $p1 _1.fastq.gz)
	p2=${p1%_1.fastq.gz}_2.fastq.gz

	echo Starting ... base \= $base \; p1 \= $p1 \; p2 \= $p2

	sbatch -J $base -o $base.align.out -c $NPROCall --export=ALL,base=$base,p1=$p1,p2=$p2,NPROCm=$NPROC 1b.align.slurm

done
