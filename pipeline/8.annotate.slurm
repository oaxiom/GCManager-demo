#!/bin/sh
#SBATCH --cpus-per-task=2
#SBATCH -o annotate_snps.out

pwd=$(pwd)
PID=$(basename $pwd)
vcf=$PID.recalibrated_snps_recalibrated_indels.vcf.gz
DATA_PATH='/opt/seqanalysis/static_data'

echo Started Stage 8 with PID = $PID vcf = $vcf

# Only keeps annotated SNPs
# TODO: Potential problem here, if PharmaGKB or Risk/GWAS is updated, the python script needs to be rerun

echo 'Started dbSNP'
python3 8a.annotate_dbsnp.py $PID 
echo 'Started Pharma'
python3 8b.annotate_pharmaGKB.py $PID
echo 'Risk'
python3 8c.annotate_risk.py $PID
#echo 'ClinVAR'
#python 8d.annotate_ClinVar.py $PID

echo Stage 8: Completed annotation and selection of SNPs

python3 8f.getqc.py $PID

# Final cleanups
rm called.chr*.recal.g.vcf.gz
rm called.chr*.recal.g.vcf.gz.tbi
rm genotype.chr*.vcf.gz
rm genotype.chr*.vcf.gz.tbi
rm dbsnp.toml
rm *.sorted.dedupe.bam
rm *.sorted.dedupe.bam.bai
rm *.sorted.dedupe.recal.bam
rm *.sorted.dedupe.recal.bam.bai
rm recalibrate_*.recal
rm recalibrate_*.idx
rm recalibrate_*.tranches
rm PID.*.recalibrated_*.vcf.gz
rm PID.*.recalibrated_*.vcf.gz.tbi

# Final BAM to CRAM:
bash_ref_fasta=$(echo $DATA_PATH/hg38_v0_20231023/Homo_sapiens_assembly38.fasta)

/opt/seqanalysis/bin/samtools view -@ 2 -T $bash_ref_fasta -C -o $PID.cram $PID.sorted.final.bam

rm $PID.sorted.final.bam

# Has to go before the pack_gcm 
sh 8e.cleanup_logs.sh

python3 8g.pack_gcm.py $PID

