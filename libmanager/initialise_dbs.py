#
# Initialise the databases, pack, etc, designed to be run once to setup a clean installation.
#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024 中基科生物保留所有权利
#
# Author(s):
# Andrew P. Hutchins,
# Huang Zongkang
#

import sys, os, sqlite3, shutil, glob, datetime, uuid

from . import settings
from . import user
from . import security

def init_dbs(gcmanager, home_path, script_path, log):
    log.info('Setting up tables')

    # Setup the PID database;
    # TODO: Setup the date properly.
    PID = sqlite3.connect(os.path.join(home_path, 'dbs', "PID.db"))
    PIDcursor = PID.cursor()
    PIDcursor.execute('CREATE TABLE patients (PID TEXT, SID TEXT, name TEXT, age INT, sex TEXT, analysis_done TEXT, date_added TEXT, date_analysis TEXT, data_dir TEXT, institution_sending TEXT)')
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
    # TODO: add the selectable drugs
    disease_dbc.execute('CREATE TABLE diseasecodes_pharma (dis_code TEXT, desc_en TEXT, desc_cn TEXT)')
    # Load pharma from spreadsheet
    with open(os.path.join(script_path, 'disDB', 'Pharma', 'EN_selectable_conditions.txt'), 'rt', encoding="utf-8") as ohEN, \
        open(os.path.join(script_path, 'disDB', 'Pharma', 'CN_selectable_conditions.txt'), 'rt', encoding="utf-8") as ohCN:
        for did, (lineEN, lineCN) in enumerate(zip(ohEN, ohCN)):
            if not (lineEN and lineCN): continue
            disease_dbc.execute('INSERT INTO diseasecodes_pharma VALUES (?, ?, ?)', (f'P{did+1}', lineEN.strip(), lineCN.strip()))
    log.info('Setting up Pharma table')

    with open(os.path.join(home_path, 'dbs', ".fren"), "wb") as f:
        fren = security.str_gen_key()
        f.write(fren)
    gcmanager.fren = fren

    # Load ClinVar
    # Isn't this per patient?
    disease_dbc.execute('CREATE TABLE diseasecodes_clinvar (dis_code TEXT, desc_en TEXT, desc_cn TEXT)')

    # Load Risk factors
    disease_dbc.execute('CREATE TABLE diseasecodes_risk (dis_code TEXT, desc_en TEXT, desc_cn TEXT)')
    # Load risk factors
    with open(os.path.join(script_path, 'disDB', 'Risk', 'EN_phenotypes.txt'), 'rt', encoding="utf-8") as ohEN, \
        open(os.path.join(script_path, 'disDB', 'Risk', 'CN_phenotypes.txt'), 'rt', encoding="utf-8") as ohCN:
        for did, (lineEN, lineCN) in enumerate(zip(ohEN, ohCN)):
            if not (lineEN and lineCN): continue
            disease_dbc.execute('INSERT INTO diseasecodes_risk VALUES (?, ?, ?)', (f'R{did+1}', lineEN.strip(), lineCN.strip()))
    log.info('Setting up Risk table')

    disease_db.commit()
    disease_db.close()

    # System preferences DB
    settings.settings(home_path).initialize_dbs()

    # users
    user.users(home_path, log).initialize_dbs()

def build_demo_data(man, home_path, script_path, log):
    log.info('Moving data')

    # Setup two patients, and copy the data
    man.add_patient('demo_user', '72210953309787', 'SEQ72210953309787', '何XX', '男', 43, 'HOSPITAL1') # Complete
    man.add_patient('demo_user', 'NA12878', 'SEQNA12878', '王XX', '男', 22, 'HOSPITAL1') # Complete
    man.add_patient('demo_user', 'RESTRICTED1', 'SEQRESTRICTED1', '李XX', '女', 24, 'HOSPITAL2') # Not started

    #man.add_patient('demo_user', 'PATIENTNOTSTARTED', 'SEQNOTSTARTED', '李XX', '女', 24, 'HOSPITAL1') # Not started

    user_home_path = os.path.expanduser('~')

    # Copy all the progress and logs;
    user_home_path = os.path.expanduser('~')
    shutil.copy(os.path.join(script_path, 'demo_data', 'PID.72210953309787', 'PID.72210953309787.vcf.gz'), os.path.join(home_path, 'data', 'PID.72210953309787'))
    shutil.copy(os.path.join(script_path, 'demo_data', 'PID.72210953309787', 'PID.72210953309787.data.gcm'), os.path.join(home_path, 'data', 'PID.72210953309787'))
    shutil.copy(os.path.join(script_path, 'demo_data', 'PID.72210953309787', 'PID.72210953309787.cram'), os.path.join(home_path, 'data', 'PID.72210953309787'))


    [shutil.copy(f, os.path.join(home_path, 'data', 'PID.NA12878')) for f in glob.glob(os.path.join(script_path, 'demo_data', 'PID.NA12878', '*.out'))]
    shutil.copy(os.path.join(script_path, 'demo_data', 'PID.NA12878', 'PID.NA12878.data.gcm'), os.path.join(home_path, 'data', 'PID.NA12878'))
    shutil.copy(os.path.join(script_path, 'demo_data', 'PID.NA12878', 'PID.NA12878.vcf.gz'), os.path.join(home_path, 'data', 'PID.NA12878'))

    # Add details of the analysis to the database;

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
            'space_used': '1.1Gb',
            'data_packed': datetime.datetime.now().isoformat(' '),
            'cram_available': 1,
            'vcf_available': 1,
            'institution_sending': 'HOSPITAL1',
        }
    db_PID_cursor.execute('UPDATE patients SET analysis_done = :analysis_done, date_added= :date_added, date_analysis = :date_analysis, data_dir = :data_dir, institution_sending= :institution_sending WHERE PID = :patient_id', newpid_row)
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
            'space_used': '1.0Gb',
            'data_packed': datetime.datetime.now().isoformat(' '),
            'cram_available': 0,
            'vcf_available': 1,
            'institution_sending': 'HOSPITAL2',
        }
    db_PID_cursor.execute('UPDATE patients SET analysis_done = :analysis_done, date_added= :date_added, date_analysis = :date_analysis, data_dir = :data_dir, institution_sending= :institution_sending WHERE PID = :patient_id', newpid_row)
    db_PID_cursor.execute('UPDATE summary_statistics SET aligned_reads = :aligned_reads WHERE PID = :patient_id', newpid_row)
    db_PID_cursor.execute('UPDATE patient_data SET space_used = :space_used, data_packed = :data_packed, cram_available = :cram_available, vcf_available =:vcf_available WHERE PID = :patient_id', newpid_row)

    ########## RESTRICTED patient:

    shutil.copy(os.path.join(script_path, 'demo_data', 'PID.RESTRICTED1', 'PID.RESTRICTED1.restricted1.data.gcm'),
        os.path.join(home_path, 'data', 'PID.RESTRICTED1', 'PID.RESTRICTED1.data.gcm'))

    newpid_row = {
            'patient_id': 'RESTRICTED1',
            'seq_id': 'SEQRESTRICTED1',
            'analysis_done': 1,
            'date_added': datetime.datetime.now().isoformat(' '),
            'date_analysis': datetime.datetime.now().isoformat(' '),
            'data_dir': os.path.join(home_path, 'data', 'PID.RESTRICTED1'),
            'aligned_reads': 2000000,
            'space_used': '1.0Gb',
            'data_packed': datetime.datetime.now().isoformat(' '),
            'cram_available': 0,
            'vcf_available': 0,
            'institution_sending': 'HOSPITAL2',
        }
    db_PID_cursor.execute('UPDATE patients SET analysis_done = :analysis_done, date_added= :date_added, date_analysis = :date_analysis, data_dir = :data_dir, institution_sending= :institution_sending WHERE PID = :patient_id', newpid_row)
    db_PID_cursor.execute('UPDATE summary_statistics SET aligned_reads = :aligned_reads WHERE PID = :patient_id', newpid_row)
    db_PID_cursor.execute('UPDATE patient_data SET space_used = :space_used, data_packed = :data_packed, cram_available = :cram_available, vcf_available =:vcf_available WHERE PID = :patient_id', newpid_row)


    db_PID.commit()
    db_PID.close()

    man.update_patient_space_used('NA12878')
    man.update_patient_space_used('72210953309787')
    man.update_patient_space_used('RESTRICTED1')

    # Add some users;
    man.users.add_user(uuid.uuid4(), 'anormaluser', 'user123', is_admin=False)

