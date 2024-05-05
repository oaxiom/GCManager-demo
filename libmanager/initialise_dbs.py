
import sys, os, sqlite3, shutil, glob, datetime

def init_dbs(home_path, script_path, log):
    log.info('Setting up tables')

    # Setup the PID database;
    # TODO: Setup the date properly.
    PID = sqlite3.connect(os.path.join(home_path, 'dbs/', "PID.db"))
    PIDcursor = PID.cursor()
    PIDcursor.execute('CREATE TABLE patients (PID TEXT, SID TEXT, analysis_done TEXT, date_added TEXT, date_analysis TEXT, data_dir TEXT)')
    PID.commit()

    PIDcursor.execute('CREATE TABLE patient_data (PID TEXT, space_used INT, data_packed TEXT, cram_avaialable TEXT, vcf_available TEXT)')
    PID.commit()

    # summary statistics DB:
    PIDcursor.execute('CREATE TABLE summary_statistics (PID TEXT, SID TEXT, aligned_reads TEXT)')
    PID.commit()
    PID.close()

    # TODO: Setup the disease code database, by packing the raw data
    disease_db = sqlite3.connect(os.path.join(home_path, "dbs/", "disease_codes.db"))
    disease_dbc = disease_db.cursor()
    disease_dbc.execute('CREATE TABLE diseasecodes (dis_code TEXT, desc_en TEXT, desc_cn TEXT)')
    # Load from spreadsheet
    oh = open(os.path.join(script_path, 'disDB', 'disease_targets.csv'), 'rt')
    for line in oh:
        if line.startswith('\ufeffcode'): # Excel stupidity;
            continue
        # TODO: Fix potential bug for comma's in names
        line = line.strip().split(',') # comma's in names...
        disease_dbc.execute('INSERT INTO diseasecodes VALUES (?, ?, ?)', line)
    oh.close()
    disease_db.commit()
    disease_db.close()

def build_demo_data(man, home_path, log):
    log.info('Setting up DEMO data')

    # Setup two patients, and copy the data
    man.add_patient('72210953309787', 'SEQ72210953309787') # Complete
    man.add_patient('NA12878', 'SEQNA12878') # Complete
    man.add_patient('PATIENTNOTSTARTED', 'SEQNOTSTARTED') # Not started
    # TODO: Add partially complete one;

    # Copy all the progress and logs;
    [shutil.copy(f, '../GC_demo/data/PID.72210953309787/') for f in glob.glob('../demo_data/data/PID.72210953309787/*.out')]
    shutil.copy('../demo_data/data/PID.72210953309787/72210953309787.recalibrated_snps_recalibrated_indels.vcf.gz', '../GC_demo/data/PID.72210953309787/')
    #[shutil.copy(f, '../GC_demo/data/PID.72210953309787/') for f in glob.glob('../demo_data/data/PID.72210953309787/*.cram')]

    [shutil.copy(f, '../GC_demo/data/PID.NA12878/') for f in glob.glob('../demo_data/data/PID.NA12878/*.out')]
    shutil.copy('../demo_data/data/PID.NA12878/NA12878.recalibrated_snps_recalibrated_indels.vcf.gz', '../GC_demo/data/PID.NA12878/')

    # Add fake details of the analysis to the database;

    db_PID = sqlite3.connect(os.path.join(home_path, 'dbs/', "PID.db"))
    db_PID_cursor = db_PID.cursor()

    newpid_row = {
            'patient_id': '72210953309787',
            'seq_id': 'SEQ72210953309787',
            'analysis_done': 1,
            'date_added': datetime.datetime.now().isoformat(' '),
            'date_analysis': datetime.datetime.now().isoformat(' '),
            'data_dir': '../GC_demo/data/PID.72210953309787/',
            'aligned_reads': 1000000,
            'space_used': '7.1Gb',
            'data_packed': 0,
            'cram_avaialable': 0,
            'vcf_available': 1,
        }
    db_PID_cursor.execute('UPDATE patients SET analysis_done = :analysis_done, date_added= :date_added, date_analysis = :date_analysis, data_dir = :data_dir WHERE PID = :patient_id', newpid_row)
    db_PID_cursor.execute('UPDATE summary_statistics SET aligned_reads = :aligned_reads WHERE PID = :patient_id', newpid_row)
    db_PID_cursor.execute('UPDATE patient_data SET space_used = :space_used, data_packed = :data_packed, cram_avaialable = :cram_avaialable, vcf_available =:vcf_available WHERE PID = :patient_id', newpid_row)

    newpid_row = {
            'patient_id': 'NA12878',
            'seq_id': 'SEQNA12878',
            'analysis_done': 1,
            'date_added': datetime.datetime.now().isoformat(' '),
            'date_analysis': datetime.datetime.now().isoformat(' '),
            'data_dir': '../GC_demo/data/PID.NA12878/',
            'aligned_reads': 2000000,
            'space_used': '12.0Gb',
            'data_packed': 0,
            'cram_avaialable': 0,
            'vcf_available': 1,
        }
    db_PID_cursor.execute('UPDATE patients SET analysis_done = :analysis_done, date_added= :date_added, date_analysis = :date_analysis, data_dir = :data_dir WHERE PID = :patient_id', newpid_row)
    db_PID_cursor.execute('UPDATE summary_statistics SET aligned_reads = :aligned_reads WHERE PID = :patient_id', newpid_row)
    db_PID_cursor.execute('UPDATE patient_data SET space_used = :space_used, data_packed = :data_packed, cram_avaialable = :cram_avaialable, vcf_available =:vcf_available WHERE PID = :patient_id', newpid_row)

    db_PID.commit()
    db_PID.close()

