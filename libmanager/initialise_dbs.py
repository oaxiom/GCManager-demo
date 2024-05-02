
import sqlite3

def init_dbs(self, home_path):
    # Setup the PID database;
    # TODO: Setup the date properly.
    PID = sqlite3.connect(os.path.join(home_path, 'dbs/', "PID.db"))
    PIDcursor = self.sql.cursor()
    PIDcursor.execute('CREATE TABLE patients (PID TEXT, SID TEXT, analysis_done TEXT, date_added TEXT, date_analysis TEXT, data_dir TEXT)')
    PID.commit()

    PIDcursor.execute('CREATE TABLE patient_data (PID TEXT, space_used INT, data_packed TEXT, cram_avaialable TEXT, vcf_available TEXT)')
    PID.commit()
    PID.close()

    # summary statistics DB:
    PIDcursor.execute('CREATE TABLE summary_statistics (PID TEXT, SID TEXT, aligned_reads TEXT, )')
    PID.commit()
    PID.close()

    # TODO: Setup the disease code database, by packing the raw data
    disease_db = sqlite3.connect(os.path.join(home_path, "dbs/", "disease_codes.db"))
    disease_dbc = disease_db.cursor()
    disease_dbc.execute('CREATE TABLE diseasecodes (dis_code TEXT, desc_en TEXT, desc_cn TEXT)')
    # TODO: Load from spreadsheet;
    disease_db.commit()
    disease_db.close()


