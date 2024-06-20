# runner
#
# This script essentially can be run in the folder, and
# it will work out the stage of the run, report the current completion state
# and then run subsequent scripts if needed.
#
# Known bugs:


import sys, os, glob, subprocess, logging, statistics, pathlib

# Dummy logger
def prepare_logging():
    logging.basicConfig(level=logging.DEBUG,
        format='%(levelname)-8s: %(message)s',
        datefmt='%m-%d %H:%M')

    return logging.getLogger(f'GCmanager')

stages = {
        1: 'Align reads to genome',
        2: 'BQSR correct',
        3: 'Merge BAMs',
        4: 'Haplotype',
        5: 'Genotype',
        6: 'Gather VCFs',
        7: 'Recalibrate',
        8: 'Annotate SNPs',
        9: 'Finished',
        }

class runner:
    def __init__(self, patient_id: str, log=None):
        # This sample variables
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.PID = patient_id
        self.log = log

        self.stage1 = 0
        self.stage2 = 0
        self.stage3 = 0
        self.stage4 = 0
        self.stage5 = 0
        self.stage6 = 0
        self.stage7 = 0
        self.stage8 = 0

    def run(self):
        # Statistics
        self.unmapped_reads_count = None # NEeded to estimate bwa completion
        self.mapped_read_count = None # I think I don't need this?

        if os.path.exists('full_logs.out.gz'):
            # Stage 8 has been completed
            return

        # Step 1: Determine minimum requirements
        assert len(glob.glob('*_1.fastq.gz')) >= 1, 'No FASTQ files found'

        # Step 2: Are we completely empty?
        # libmanager deals with this now
        #if not os.path.exists('1b.batch.sh'): self.setup_scripts()

        # Do we have the count_reads completed?
        if not os.path.exists('read_count.txt'):
            self.count_reads()
            # This might seem weird, why not just go straight through?
            # But it could cause a race condition, where you spend >5 mins counting reads (very possible)
            # and in the meantime another runner gets started.
            # This would make a huge mess.
            # At least this way read_count.txt is made (by count_reads(), and we don't get into a loop counting reads
            # constantly. Another possible problem is if count_reads is empty
            # the next time the runner is started, but we get around that by
            # filling in an artificially huge number until the real number becomes avaialble.
            return None

        self.get_total_read_count()
        if self.unmapped_reads_count < 4e6:
            # It is very unliukely the data will produce anything useful.
            # Kill the analysis.
            [self.touch_all_outs(i) for i in [1,2,3,4,5,6,7,8]]
            with open('FATALERROR.out', 'w') as f:
                f.write('####################################################')
                f.write(f'Fatal Error, too few reads {self.unmapped_reads_count:,}')
                f.write('####################################################')
                subprocess.run('sh 8e.cleanup_logs.sh', shell=True)
            log.info(f'Fatal Error for PID {patient_id}, too few reads {self.unmapped_reads_count:,}')
            return None

        # TODO: Abstract away trhe functions below.
        # It's basically two types

        # Is Stage 1 (alignment) copmplete?
        align_outs = list(glob.glob('*.align.out'))
        if len(align_outs) == 0:
            # Too early, we haven't started yet
            # start stage 1
            log.info('Submitting Stage 1: Align')
            self.touch_all_outs(1)
            subprocess.run('./1b.batch.sh', shell=True)
            self.final_results(1)
            return None
        elif len(align_outs) >= 1:
            # Started
            self.stage1, genuine_finish = self.estimate_bwa_completion(align_outs)
            if not genuine_finish:
                self.final_results(1)
                return None

        # Is Stage 2 complete
        bqsr_outs = list(glob.glob('*.bqsr.out'))
        if len(bqsr_outs) == 0: # We havne't started yet
            log.info('Submitting Stage 2: BQSR')
            self.touch_all_outs(2)
            subprocess.run('./2.batch.sh', shell=True)
            self.final_results(2)
            return None
        elif len(align_outs) >= 1:
            self.stage2, genuine_finish = self.estimate_bqsr_completion(bqsr_outs)
            if not genuine_finish:
                self.final_results(2)
                return None

        # Stage 3: Merge the BAMs
        # This one is fairly fast, so don't bother with progress meter
        if not os.path.exists('merge_bams.out'):
            # Not started
            self.touch_all_outs(3)
            subprocess.run('sbatch 3.merge_bams.slurm', shell=True)
            self.final_results(3)
            return None
        else:
            # Started, are we finished?
            oh = open('merge_bams.out', 'rt')
            for line in oh:
                if 'Stage 3: Done Merging' in line:
                    self.stage3 = 100
                    break
            else: # Not finished
                self.final_results(3)
                return None

        # Stage 4: Haplotype the BAM
        call_outs = list(glob.glob('called.*.out'))
        if len(call_outs) == 0:
            self.touch_all_outs(4)
            subprocess.run('./4.batch.sh', shell=True)
            self.final_results(4)
            return None
        else:
            self.stage4, genuine_finish = self.estimate_haplotype_completion(call_outs)
            if not genuine_finish:
                self.final_results(4)
                return None

        # Stage 5: Genotype the GVCFs
        outs = list(glob.glob('genotypegvcfs.*.out'))
        if len(outs) == 0:
            self.touch_all_outs(5)
            subprocess.run('./5.batch.sh', shell=True)
            self.final_results(5)
            return None
        elif len(outs) == 22:
            self.stage5, genuine_finish = self.estimate_genotype_completion(outs)
            if not genuine_finish:
                self.final_results(5)
                return None

        # Stage 6: 6.merge_vcfs.slurm Should be very fast
        if not os.path.exists('gathervcfs.out'):
            # Not started yet
            self.touch_all_outs(6)
            subprocess.run('sbatch 6.merge_vcfs.slurm', shell=True)
            self.final_results(6)
            return None
        else:
            oh = open('gathervcfs.out', 'rt')
            for line in oh:
                if 'Stage 6: Collected VCFs' in line:
                    self.stage6 = 100
                    break
            else:
                self.final_results(6)
                return None

        # Stage 7: Recalibrate
        if not os.path.exists('variant_racalibrate.out'):
            # Not started yet
            self.touch_all_outs(7)
            subprocess.run('sbatch 7.variantrecalibrate.slurm', shell=True)
            self.final_results(7)
            return None
        else:
            oh = open('variant_racalibrate.out', 'rt')
            for line in oh:
                if 'Stage 7: VariantRecalibrator SNPs' in line:
                    self.stage7 = 25
                elif 'Stage 7: VariantRecalibrator INDELs' in line:
                    self.stage7 = 50
                elif 'Stage 7: ApplyVQSR SNPs' in line:
                    self.stage7 = 75

                if 'Stage 7: Finished recalibrating' in line:
                    self.stage7 = 100
                    break
            else:
                self.final_results(7)
                return None

        if not os.path.exists('annotate_snps.out'):
            # Stage 8 not started
            self.touch_all_outs(8)
            subprocess.run('sbatch 8.annotate.slurm', shell=True)
            self.final_results(8)
            return None
        else:
            oh = open('annotate_snps.out', 'rt')
            for line in oh:
                # TODO: add pharma, clinvar and risk percent completions
                if 'Stage 8: Completed' in line:
                    self.stage8 = 100
            else:
                self.final_results(8)
                return None

        self.final_results(9)
        log.info('All stages are complete')
        return True

    def final_results(self, stage):
        log.info(f'Current Stage: {stage}, {stages[stage]}')
        log.info(f'Stage 1: {self.stage1}%')
        log.info(f'Stage 2: {self.stage2}%')
        log.info(f'Stage 3: {self.stage3}%')
        log.info(f'Stage 4: {self.stage4}%')
        log.info(f'Stage 5: {self.stage5}%')
        log.info(f'Stage 6: {self.stage6}%')
        log.info(f'Stage 7: {self.stage7}%')
        log.info(f'Stage 8: {self.stage8}%')
        oh = open('progress.txt', 'wt')
        oh.write(f'Current Stage: {stage}, {stages[stage]}\n')
        oh.write(f'Stage 1: {self.stage1}%\n')
        oh.write(f'Stage 2: {self.stage2}%\n')
        oh.write(f'Stage 3: {self.stage3}%\n')
        oh.write(f'Stage 4: {self.stage4}%\n')
        oh.write(f'Stage 5: {self.stage5}%\n')
        oh.write(f'Stage 6: {self.stage6}%\n')
        oh.write(f'Stage 7: {self.stage7}%\n')
        oh.write(f'Stage 8: {self.stage8}%\n')

    def touch_all_outs(self, stage):
        """
        **Purpose**
            Touch all the outs, so that runner doesn't
            start up the jobs a second time
        """
        if stage == 1:
            # ERR1044300.align.out
            [pathlib.Path(f'{f.replace("_1.fastq.gz", "")}.align.out').touch() for f in glob.glob('*_1.fastq.gz')]
        elif stage == 2:
            # ERR1044300.bqsr.out
            [pathlib.Path(f'{f.replace("_1.fastq.gz", "")}.bqsr.out').touch() for f in glob.glob('*_1.fastq.gz')]
        elif stage == 3:
            pathlib.Path('merge_bams.out').touch()
        elif stage == 4:
            [pathlib.Path(f'called.chr{i}.out').touch() for i in range(1,23)]
        elif stage == 5:
            [pathlib.Path(f'genotypegvcfs.chr{i}.out').touch() for i in range(1,23)]
        elif stage == 6:
            pathlib.Path('gathervcfs.out').touch()
        elif stage == 7:
            pathlib.Path('variant_racalibrate.out').touch()
        elif stage == 8:
            pathlib.Path('annotate_snps.out').touch()

        return

    def estimate_genotype_completion(self, outs):
        completion_status = {a: 0 for a in outs}
        really_finished = {a: False for a in outs}
        for file in outs:
            oh = open(file, 'rt')
            for line in oh:
                if 'Stage 5: Genotyped chrom' in line:
                    completion_status[file] = 100
                    really_finished[file] = True
            oh.close()

        if False not in really_finished.values():
            return 100, True # 100% and really finsihed all samples
        return int(statistics.mean(completion_status.values())), False # At least one sample not finished

    def estimate_haplotype_completion(self, call_outs):
        '''
        **Purpose**
            Estimate the completion of the haplotype call
        '''
        completion_status = {a: 0 for a in call_outs}
        really_finished = {a: False for a in call_outs}
        for file in call_outs:
            oh = open(file, 'rt')
            for line in oh:
                if 'Stage 4: Completed chrom' in line:
                    completion_status[file] = 100
                    really_finished[file] = True
            oh.close()

        if False not in really_finished.values():
            return 100, True # 100% and really finsihed all samples
        return int(statistics.mean(completion_status.values())), False # At least one sample not finished

    def estimate_bqsr_completion(self, bqsr_outs):
        """
        **Purpose**
            Estimate the completion of the BQSR stage

        """
        completion_status = {a: False for a in bqsr_outs}
        really_finished = {a: False for a in bqsr_outs}
        for file in bqsr_outs:
            oh = open(file, 'rt')
            for line in oh:
                if 'Stage 2: Done BQSR for' in line:
                    completion_status[file] = 100
                    really_finished[file] = True
                elif 'ProgressMeter' in line:
                    if 'chr' in line:
                        reads_processed = int(line.split()[6]) // 2 # Reports as PE
                        completion_status[file] = reads_processed / self.mapped_reads[file.split('.')[0]] * 100
            oh.close()

        if False not in really_finished.values():
            return 100, True # 100% and really finsihed all samples
        return int(statistics.mean(completion_status.values())), False # At least one sample not finished

    def estimate_bwa_completion(self, align_outs):
        """
        **Purpose**
            Estimate from the bwa align.outs wahat the completion state is

        Known Bug: If the number of FASTQ samples is large then the estiamte can go down as jobs are started and finished

        """
        # Route 1: (Easy) Check for the completion string
        completion_status = {a: False for a in align_outs}
        really_finished = {a: False for a in align_outs}
        self.mapped_reads = {a.split('.')[0]: 1e200 for a in align_outs}
        num_reads = 1e200 # Stops a bug if we call runner too earley before reads have been counted
        for file in align_outs:
            oh = open(file, 'rt')
            estimated_number_of_done_reads = 0
            for line in oh:
                if 'Stage 1: Aligned Read for sample' in line:
                    completion_status[file] = 100
                    really_finished[file] = True # because it's possible to have 100% align,. but samtools is still working
                    break
                if 'Stage 1: Number of reads' in line:
                    num_reads = int(line.split()[-1]) // 4 # From wc -l
                if '[M::mem_process_seqs] Processed ' in line:
                    reads = int(line.split()[2]) //2 # bwa reports both pairs
                    estimated_number_of_done_reads += reads
                if line.startswith('WRITTEN:'):
                    self.mapped_reads[file.split('.')[0]] = int(line.split()[-1]) // 2
            oh.close()

            percent_done = estimated_number_of_done_reads / num_reads * 100
            completion_status[file] = int(percent_done)

        if False not in really_finished.values():
            return 100, True # 100% and really finsihed all samples

        return int(statistics.mean(completion_status.values())), False # At least one sample not finished, or samtools still working

    def setup_scripts(self):
        """
        **Purpose**
            We are empty, but have some FASTQ files, so symbolic link all the
            pipeline scripts
        """
        self.log.info('Setting up scripts')
        # Script paths is hardcoded, to change when put in GCManager
        script_path = '~/tools/final_pipeline'
        subprocess.run(f'ln -s {script_path}/*.sh .', shell=True)
        subprocess.run(f'ln -s {script_path}/*.slurm .', shell=True)
        subprocess.run(f'ln -s {script_path}/*.py .', shell=True)
        return True

    def get_total_read_count(self):
        # Load in the total number of unmapped reads

        oh = open('read_count.txt', 'rt')
        try:
            self.unmapped_reads_count = int(oh.readline().strip())
        except ValueError:
            # Probably counting reads hasn't finished yet.
            self.unmapped_reads_count = 1000000000000000 # Add a crazy high number temporarily
            return # Don't let the crazy number enter the logs;

        log.info(f'Total number of reads = {self.unmapped_reads_count:,}')

    def count_reads(self):
        """
        **Purpose**
            count the number of reads, and write the result in a text file
        """
        self.log.info('Counting number of unmapped reads')
        counts = []

        # I touch the file so that runner will not accidentally start
        oh = open('read_count.txt', 'wt')

        for p1 in glob.glob('*1.fastq.gz'):
            self.log.info(f'Counting {p1}')
            res = subprocess.run(f'gunzip -c {p1} | wc', shell=True, capture_output=True)
            counts.append(int(res.stdout.split()[0]) // 4)

        # merge the wc read counts
        reads = sum(counts)

        oh.write(f'{reads}\n')
        oh.close()

if __name__ == '__main__':
    # patient_id will come from GCManager later
    # Here, I just grab the .. PATH

    PID = os.path.split(os.path.dirname(os.path.abspath(sys.argv[0])))[-1]
    log = prepare_logging()

    log.info(f'PID = {PID}')

    run = runner(PID, log)
    result = run.run()

    #sys.quit() # retunr code?
