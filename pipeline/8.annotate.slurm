#!/bin/sh
#SBATCH --cpus-per-task=2
#SBATCH -o annotate_snps.out

pwd=$(pwd)
PID=$(basename $pwd)
vcf=$PID.recalibrated_snps_recalibrated_indels.vcf.gz

echo Started Stage 8 with PID = $PID vcf = $vcf

# Only keeps annotated SNPs
# TODO: Potential problem here, if PharmaGKB or Risk/GWAS is updated, the python script needs to be rerun

echo 'Started dbSNP'
python 8a.annotate_dbsnp.py $PID 
echo 'Started Pharma'
python 8b.annotate_pharmaGKB.py $PID
echo 'Risk'
python 8c.annotate_risk.py $PID
echo 'ClinVAR'
python 8d.annotate_ClinVar.py $PID

echo Stage 8: Completed annotation and selection of SNPs

sh 8e.cleanup_logs.sh

python 8f.getqc.py $PID

python 8g.pack_gcm.py $PID

sleep 10 # Wait for any buffers
python runner.py

