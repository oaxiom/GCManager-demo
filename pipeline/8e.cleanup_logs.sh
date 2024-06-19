#!/bin/sh
#
# Clean up all the logs, put them in order and preserve them.

echo '#########' > full_logs.out
echo '# Stage 1' >> full_logs.out
echo '#########' >> full_logs.out

cat *.align.out >> full_logs.out

echo '#########' >> full_logs.out
echo '# Stage 2' >> full_logs.out
echo '#########' >> full_logs.out

cat *.bqsr.out >>full_logs.out

echo '#########' >> full_logs.out
echo '# Stage 3' >> full_logs.out
echo '#########' >> full_logs.out

cat merge_bams.out >>full_logs.out

echo '#########' >> full_logs.out
echo '# Stage 4' >> full_logs.out
echo '#########' >> full_logs.out

cat called.chr*.out >>full_logs.out

echo '#########' >> full_logs.out
echo '# Stage 5' >> full_logs.out
echo '#########' >> full_logs.out

cat genotypegvcfs.*.out >>full_logs.out

echo '#########' >> full_logs.out
echo '# Stage 6' >> full_logs.out
echo '#########' >> full_logs.out

cat gathervcfs.out >>full_logs.out

echo '#########' >> full_logs.out
echo '# Stage 7' >> full_logs.out
echo '#########' >> full_logs.out

cat variant_racalibrate.out >>full_logs.out

echo '#########' >> full_logs.out
echo '# Stage 8' >> full_logs.out
echo '#########' >> full_logs.out

cat annotate_snps.out >>full_logs.out

echo "Stage 8: Completed annotation and selection of SNPs" >>full_logs.out
echo 'All stages completed' >> full_logs.out

gzip -f full_logs.out

