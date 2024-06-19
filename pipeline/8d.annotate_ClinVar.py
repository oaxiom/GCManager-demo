
import sys, os, subprocess, gzip

if len(sys.argv) != 2:
    print('Incorrect number of arguments. should be PID file only')
    sys.exit(-1)

PID = sys.argv[1]
vcf = f'{PID}.recalibrated_snps_recalibrated_indels.vcf.gz'

# I do this through python, as I can't think of a way to fix the path correctly in BASH:
# output the toml file
clinvar_path=os.path.expanduser('~/static_data/ClinVar/clinvar_20240301.vcf.gz')

toml = f'''
[[annotation]]
file="{clinvar_path}"
fields=["AF_EXAC", "MC", "GENEINFO", "RS", "CLNSIG", "CLNDN"]
names=["ExAC_alleleFreq", "MC", "Gene", "RS", "significance", "diagnosis"]
ops=["self", "self", "self", "self", "self", "self",]
'''

oh = open('clinvar.toml', 'wt')
oh.write(toml)
oh.close()

subprocess.run(f'''vcfanno clinvar.toml {vcf} | bgzip > {PID}.gatk.dbsnp.clinvar.vcf.gz''', shell=True)
subprocess.run(f'''bcftools query -f '%CHROM\t%POS\t%REF\t%ALT\t%MC\t%Gene\t%RS\t%significance\t%ExAC_alleleFreq\t%diagnosis\n' {PID}.gatk.dbsnp.clinvar.vcf.gz | grep -v '\.\t\.' >{PID}.clinvar.tsv''', shell=True)
subprocess.run(f'''grep 'Pathogenic' {PID}.clinvar.tsv > {PID}.clinvar.pathogenic.tsv''', shell=True)

print('Stage 8: Finished annotating ClinVAR')

# Annotate with ClinVar
#vcfanno clinvar.toml ${vcf} | bgzip > genotype.gatk.clinvar.vcf.gz
#bcftools query -f '%CHROM\t%POS\t%REF\t%ALT\t%MC\t%Gene\t%RS\t%significance\t%ExAC_alleleFreq\t%diagnosis\n' genotype.gatk.annotated.vcf.gz | grep -v '\.\t\.'  >genotype.gatk.annotated.clinvar.tsv
#grep  'athogenic' genotype.gatk.annotated.clinvar.tsv  > genotype.gatk.annotated.clinvar.pathogenic.tsv

