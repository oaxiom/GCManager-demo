
import os, sqlite3

class settings:
    def __init__(self, home_path):
        self.home_path = home_path

        self.settings_doctor = sqlite3.connect(os.path.join(self.home_path, "dbs/", "settings_doctor.db"))
        self.settings_doctor_cur = self.settings_doctor.cursor()

        self.settings_backend = sqlite3.connect(os.path.join(self.home_path, "dbs/", "settings_backend.db"))
        self.settings_backend_cur = self.settings_backend.cursor()

    def initialize_dbs(self):
        '''
        **Purpose**
            Build the settings databases
        '''

        settings_doctor = sqlite3.connect(os.path.join(self.home_path, "dbs/", "settings_doctor.db"))
        settings_doctor_cur = settings_doctor.cursor()
        settings_doctor_cur.execute('CREATE TABLE settings (setting_name TEXT, value TEXT)')

        # add the settings;
        settings_doctor_cur.execute('INSERT INTO settings VALUES (?,?)', ('lang', 'CN'))
        settings_doctor_cur.execute('INSERT INTO settings VALUES (?,?)', ('hospital_name', 'N/A'))

        settings_doctor.commit()
        settings_doctor.close()

        settings_backend = sqlite3.connect(os.path.join(self.home_path, "dbs/", "settings_backend.db"))
        settings_backend_cur = settings_backend.cursor()
        settings_backend_cur.execute('CREATE TABLE settings (setting_name TEXT, value TEXT)')

        settings_backend_cur.execute('INSERT INTO settings VALUES (?,?)', ('lang', 'CN'))
        settings_backend_cur.execute('INSERT INTO settings VALUES (?,?)', ('hospital_name', 'N/A'))

        settings_backend.commit()
        settings_backend.close()

    def get_doctor_setting(self, key):
        '''
        get the setting for doctor interface

        '''
        # TODO: valid key checking
        self.settings_doctor_cur.execute('SELECT value FROM settings WHERE setting_name=?', (key, ))
        # TODO: return sanity check
        return self.settings_doctor_cur.fetchone()[0]

    def set_doctor_setting(self, key, value):
        '''
        change the setting for the doctor interface

        '''
        # TODO: valid key checking
        self.settings_doctor_cur.execute('UPDATE settings SET value=? WHERE setting_name=?', (value, key))

    def get_backend_setting(self, key):
        '''
        get the setting for doctor interface

        '''
        # TODO: valid key checking
        self.settings_backend_cur.execute('SELECT value FROM settings WHERE setting_name=?', (key, ))
        # TODO: return sanity check
        return self.settings_backend_cur.fetchone()[0]

    def set_backend_setting(self, key, value):
        '''
        change the setting for the doctor interface

        '''
        # TODO: valid key checking
        self.settings_backend_cur.execute('UPDATE settings SET value=? WHERE setting_name=?', (value, key))
