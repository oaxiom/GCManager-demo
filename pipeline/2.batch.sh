for bamfile in *.sorted.dedupe.bam
do
	echo Submitting $bamfile
	o=${bamfile%.sorted.dedupe.bam}
	sbatch -J bqsr.$bamfile -o $o.bqsr.out --export=ALL,bamfile=$bamfile 2.bqsr.slurm
done

