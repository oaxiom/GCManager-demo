gunzip -c full/SRR10286930_1.fastq.gz | head -n 22000000 | gzip >SRR10286930_minimal_1.fastq.gz
gunzip -c full/SRR10286930_2.fastq.gz | head -n 22000000 | gzip >SRR10286930_minimal_2.fastq.gz


