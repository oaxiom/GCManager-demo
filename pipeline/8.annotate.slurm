#!/bin/sh
#SBATCH --cpus-per-task=1
#SBATCH -o annotate_snps.out

pwd=$(pwd)
PID=$(basename $pwd)
vcf=$PID.recalibrated_snps_recalibrated_indels.vcf.gz
HOME=$(echo ~)

echo Started Stage 8 with PID = $PID vcf = $vcf

# Only keeps annotated SNPs
# TODO: Potential problem here, if PharmaGKB or Risk/GWAS is updated, the python script needs to be rerun

echo 'Started dbSNP'
python 8a.annotate_dbsnp.py $PID 
echo 'Started Pharma'
python 8b.annotate_pharmaGKB.py $PID
echo 'Risk'
python 8c.annotate_risk.py $PID
#echo 'ClinVAR'
#python 8d.annotate_ClinVar.py $PID

echo Stage 8: Completed annotation and selection of SNPs

sh 8e.cleanup_logs.sh

python 8f.getqc.py $PID

python 8g.pack_gcm.py $PID

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
HOME=$(echo ~)
bash_ref_fasta=$(echo '$HOME/gcmtools/static_data/hg38_v0_20231023/Homo_sapiens_assembly38.fasta')

samtools view -@ 2 -T $bash_ref_fasta -C -o $PID.cram $PID.sorted.final.bam

rm $PID.sorted.final.bam

sleep 10 # Wait for any buffers
python runner.py

