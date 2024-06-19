
import sys, os, subprocess, gzip

if len(sys.argv) != 2:
    print('Incorrect number of arguments. should be PID file only')
    sys.exit(-1)

PID = sys.argv[1]
vcf = f'{PID}.recalibrated_snps_recalibrated_indels.vcf.gz'

# I do this through python, as I can't think of a way to fix the path correctly in BASH:
# output the toml file
dbsnp_path=os.path.expanduser('~/static_data/dbsnp138/dbsnp.vcf.gz')
toml = f'''
[[annotation]]
file="{dbsnp_path}"
fields=["ID"]
names=["rs_ids"]
ops=["self"]

[[postannotation]]
name="ID"
fields=["rs_ids"]
op="setid"
type="String"
'''

oh = open('dbsnp.toml', 'wt')
oh.write(toml)
oh.close()

result = subprocess.run(f'''vcfanno -lua "" dbsnp.toml {vcf} | awk -F "\t" '$3!="."' | bgzip > {PID}.gatk.dbsnp.vcf.gz''', shell=True)

print('Stage 8: Finished annotating dbSNP')

