for chrom in chr1 chr2 chr3 chr4 chr5 chr6 chr7 chr8 chr9 chr10 chr11 chr12 chr13 chr14 chr15 chr16 chr17 chr18 chr19 chr20 chr21 chr22
do
	echo Submitting $chrom
	sbatch -J genotypegvcfs.$chrom -o genotypegvcfs.$chrom.out --export=ALL,chrom=$chrom 5.genotypegvcfs.slurm
done
