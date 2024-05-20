#
# Initialise the databases, pack, etc, designed to be run once to setup a clean installation.
#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024
#
# Author(s):
# Andrew P. Hutchins,
# Huang Zongkang
#

import sys, os, sqlite3, shutil, glob, datetime
from . import settings

def init_dbs(home_path, script_path, log):
    log.info('Setting up tables')

    # Setup the PID database;
    # TODO: Setup the date properly.
    PID = sqlite3.connect(os.path.join(home_path, 'dbs', "PID.db"))
    PIDcursor = PID.cursor()
    PIDcursor.execute('CREATE TABLE patients (PID TEXT, SID TEXT, name TEXT, age INT, sex TEXT, analysis_done TEXT, date_added TEXT, date_analysis TEXT, data_dir TEXT)')
    PID.commit()

    PIDcursor.execute('CREATE TABLE patient_data (PID TEXT, space_used INT, data_packed TEXT, cram_available TEXT, vcf_available TEXT)')
    PID.commit()

    # summary statistics DB:
    PIDcursor.execute('CREATE TABLE summary_statistics (PID TEXT, SID TEXT, aligned_reads TEXT)')
    PID.commit()
    PID.close()

    # Setup the disease code database, by packing the raw data
    disease_db = sqlite3.connect(os.path.join(home_path, "dbs", "disease_codes.db"))
    disease_dbc = disease_db.cursor()

    # PharmaGKB table:
    disease_dbc.execute('CREATE TABLE diseasecodes_pharma (dis_code TEXT, desc_en TEXT, desc_cn TEXT)')
    # Load pharma from spreadsheet
    with open(os.path.join(script_path, 'disDB', 'Pharma', 'EN_selectable_conditions.txt'), 'rt', encoding="utf-8") as ohEN, \
        open(os.path.join(script_path, 'disDB', 'Pharma', 'CN_selectable_conditions.txt'), 'rt', encoding="utf-8") as ohCN:
        for did, (lineEN, lineCN) in enumerate(zip(ohEN, ohCN)):
            if not (lineEN and lineCN): continue
            disease_dbc.execute('INSERT INTO diseasecodes_pharma VALUES (?, ?, ?)', (f'P{did+1}', lineEN.strip(), lineCN.strip()))

    # Load ClinVar
    # Isn't this per patient?
    disease_dbc.execute('CREATE TABLE diseasecodes_clinvar (dis_code TEXT, desc_en TEXT, desc_cn TEXT)')

    # Load Risk factors
    disease_dbc.execute('CREATE TABLE diseasecodes_risk (dis_code TEXT, desc_en TEXT, desc_cn TEXT)')
    # Load from risk factor spreadsheet

    disease_db.commit()
    disease_db.close()

    # System preferences DB
    settings.settings(home_path).initialize_dbs()


def build_demo_data(man, home_path, script_path, log):
    log.info('Moving DEMO data')

    # Setup two patients, and copy the data
    man.add_patient('72210953309787', 'SEQ72210953309787', '何XX', '男', 43) # Complete
    man.add_patient('NA12878', 'SEQNA12878', '王XX', '男', 22) # Complete
    man.add_patient('PATIENTNOTSTARTED', 'SEQNOTSTARTED', '李XX', '女', 24) # Not started
    # TODO: Add partially complete one;

    user_home_path = os.path.expanduser('~')

    # Copy all the progress and logs;
    user_home_path = os.path.expanduser('~')
    [shutil.copy(f, os.path.join(home_path, 'data', 'PID.72210953309787')) for f in glob.glob(os.path.join(script_path, 'demo_data', 'PID.72210953309787', '*.out'))]
    shutil.copy(os.path.join(script_path, 'demo_data', 'PID.72210953309787', '72210953309787.pharmagkb.txt'), os.path.join(home_path, 'data', 'PID.72210953309787'))
    shutil.copy(os.path.join(script_path, 'demo_data', 'PID.72210953309787', '72210953309787.sorted.dedupe.recal.cram'), os.path.join(home_path, 'data', 'PID.72210953309787'))
    shutil.copy(os.path.join(script_path, 'demo_data', 'PID.72210953309787', '72210953309787.gatk.dbsnp.vcf.gz'), os.path.join(home_path, 'data', 'PID.72210953309787'))


    [shutil.copy(f, os.path.join(home_path, 'data', 'PID.NA12878')) for f in glob.glob(os.path.join(script_path, 'demo_data', 'PID.NA12878', '*.out'))]
    shutil.copy(os.path.join(script_path, 'demo_data', 'PID.NA12878', 'NA12878.gatk.dbsnp.vcf.gz'), os.path.join(home_path, 'data', 'PID.NA12878'))
    shutil.copy(os.path.join(script_path, 'demo_data', 'PID.NA12878', 'NA12878.pharmagkb.txt'), os.path.join(home_path, 'data', 'PID.NA12878'))
    #shutil.copy(os.path.join(script_path, 'demo_data', 'PID.NA12878', 'NA12878.pharmagkb.final.txt'), os.path.join(home_path, 'data', 'PID.NA12878'))

    # Add fake details of the analysis to the database;

    db_PID = sqlite3.connect(os.path.join(home_path, 'dbs', "PID.db"))
    db_PID_cursor = db_PID.cursor()

    newpid_row = {
            'patient_id': '72210953309787',
            'seq_id': 'SEQ72210953309787',
            'analysis_done': 1,
            'date_added': datetime.datetime.now().isoformat(' '),
            'date_analysis': datetime.datetime.now().isoformat(' '),
            'data_dir': os.path.join(home_path, 'data', 'PID.72210953309787'),
            'aligned_reads': 1000000,
            'space_used': '7.1Gb',
            'data_packed': datetime.datetime.now().isoformat(' '),
            'cram_available': 1,
            'vcf_available': 1,
        }
    db_PID_cursor.execute('UPDATE patients SET analysis_done = :analysis_done, date_added= :date_added, date_analysis = :date_analysis, data_dir = :data_dir WHERE PID = :patient_id', newpid_row)
    db_PID_cursor.execute('UPDATE summary_statistics SET aligned_reads = :aligned_reads WHERE PID = :patient_id', newpid_row)
    db_PID_cursor.execute('UPDATE patient_data SET space_used = :space_used, data_packed = :data_packed, cram_available = :cram_available, vcf_available =:vcf_available WHERE PID = :patient_id', newpid_row)

    newpid_row = {
            'patient_id': 'NA12878',
            'seq_id': 'SEQNA12878',
            'analysis_done': 1,
            'date_added': datetime.datetime.now().isoformat(' '),
            'date_analysis': datetime.datetime.now().isoformat(' '),
            'data_dir': os.path.join(home_path, 'data', 'PID.NA12878'),
            'aligned_reads': 2000000,
            'space_used': '12.0Gb',
            'data_packed': 0,
            'cram_available': 0,
            'vcf_available': 1,
        }
    db_PID_cursor.execute('UPDATE patients SET analysis_done = :analysis_done, date_added= :date_added, date_analysis = :date_analysis, data_dir = :data_dir WHERE PID = :patient_id', newpid_row)
    db_PID_cursor.execute('UPDATE summary_statistics SET aligned_reads = :aligned_reads WHERE PID = :patient_id', newpid_row)
    db_PID_cursor.execute('UPDATE patient_data SET space_used = :space_used, data_packed = :data_packed, cram_available = :cram_available, vcf_available =:vcf_available WHERE PID = :patient_id', newpid_row)

    db_PID.commit()
    db_PID.close()

