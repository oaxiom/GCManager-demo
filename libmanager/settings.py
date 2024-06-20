#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024 中基科生物保留所有权利
#
# Author(s):
# Andrew P. Hutchins
#

import os, sqlite3

class settings:
    def __init__(self, home_path):
        self.home_path = home_path

    def __get_cursor(self, end):
        assert end in ('Doctorend', 'Backend'), f'{end} not recognised'

        db = None
        db_cur = None

        if end == 'Doctorend':
            db = sqlite3.connect(os.path.join(self.home_path, "dbs/", "settings_doctor.db"))
            db_cur = db.cursor()

        elif end == 'Backend':
            db = sqlite3.connect(os.path.join(self.home_path, "dbs/", "settings_backend.db"))
            db_cur = db.cursor()

        return db, db_cur

    def initialize_dbs(self):
        '''
        **Purpose**
            Build the settings databases
        '''
        settings_doctor, settings_doctor_cur = self.__get_cursor('Doctorend')
        settings_doctor_cur.execute('CREATE TABLE settings (setting_name TEXT, value TEXT)')

        # add the settings;
        settings_doctor_cur.execute('INSERT INTO settings VALUES (?,?)', ('lang', 'CN'))
        settings_doctor_cur.execute('INSERT INTO settings VALUES (?,?)', ('hospital_name', 'N/A'))
        settings_doctor_cur.execute('INSERT INTO settings VALUES (?,?)', ('last_backup', '0'))

        settings_doctor.commit()
        settings_doctor.close()

        settings_backend, settings_backend_cur = self.__get_cursor('Backend')
        settings_backend_cur.execute('CREATE TABLE settings (setting_name TEXT, value TEXT)')

        settings_backend_cur.execute('INSERT INTO settings VALUES (?,?)', ('lang', 'CN'))
        settings_backend_cur.execute('INSERT INTO settings VALUES (?,?)', ('hospital_name', 'N/A'))
        settings_backend_cur.execute('INSERT INTO settings VALUES (?,?)', ('last_backup', '0'))

        settings_backend.commit()
        settings_backend.close()

    def get_lang(self, end_type):
        '''

        Convenience function to help improve language support

        '''
        if end_type == 'Doctorend':
            return self.get_doctor_setting('lang')
        elif end_type == 'Backend':
            return self.get_backend_setting('lang')
        return 'CN' # Default to CN

    def get_doctor_setting(self, key):
        '''
        get the setting for doctor interface

        '''
        # TODO: valid key checking
        settings_doctor, settings_doctor_cur = self.__get_cursor('Doctorend')
        settings_doctor_cur.execute('SELECT value FROM settings WHERE setting_name=?', (key, ))
        # TODO: return sanity check
        ret = settings_doctor_cur.fetchone()[0]
        settings_doctor.close()
        return ret

    def set_doctor_setting(self, key, value):
        '''
        change the setting for the doctor interface

        '''
        # TODO: valid key checking
        settings_doctor, settings_doctor_cur = self.__get_cursor('Doctorend')
        settings_doctor_cur.execute('UPDATE settings SET value=? WHERE setting_name=?', (value, key))
        settings_doctor.commit()
        settings_doctor.close()

    def get_backend_setting(self, key):
        '''
        get the setting for doctor interface

        '''
        # TODO: valid key checking
        settings_backend, settings_backend_cur = self.__get_cursor('Backend')
        settings_backend_cur.execute('SELECT value FROM settings WHERE setting_name=?', (key, ))
        # TODO: return sanity check
        ret = settings_backend_cur.fetchone()[0]
        settings_backend.close()

        return ret

    def set_backend_setting(self, key, value):
        '''
        change the setting for the doctor interface

        '''
        # TODO: valid key checking
        settings_backend, settings_backend_cur = self.__get_cursor('Backend')
        settings_backend_cur.execute('UPDATE settings SET value=? WHERE setting_name=?', (value, key))
        settings_backend.commit()
        settings_backend.close()
