#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024
#
# Author(s):

import sys, os, sqlite3

from . import security

class user_db:
    def __init__(self, home_path, log):
        '''
        **Purpose**

        '''
        self.home_path = home_path
        self.log = log

    def initialize_dbs(self):
        """
        **Purpose**
            Initialise and empty DB

        """
        user_db, user_db_cursor = self.__get_db()
        user_db_cursor.execute('CREATE TABLE users (UID INT, email TEXT, hpass TEXT)')
        user_db.commit()
        user_db.close()

        env_path = os.path.join(self.home_path, 'dbs', ".env")
        if os.path.exists(env_path):
            self.log.warning(".env file already exists. Exiting...")
        else:
            self.log.info(f'Set up new .env')
            with open(env_path, "w") as f:
                f.write(os.urandom(24).hex())

        self.log.info(f'Setup user DB')

        return True

    def __get_db(self):
        '''
        **Purpose**
            Get the db cursor.

        '''
        user_db = sqlite3.connect(os.path.join(self.home_path, 'dbs', "user.db"))
        user_db_cursor = user_db.cursor()
        return user_db, user_db_cursor

    def add_user(self, uuid, email, password):
        """
        **Purpose**
            Add a user;
        """
        user_db, user_db_cursor = self.__get_db()

        hpass = security.hash_password(password)

        user_db_cursor.execute('INSERT INTO users VALUES (?, ?, ?)', (uuid.bytes_le, email, hpass))

        user_db.commit()
        user_db.close()
        self.log.info(f'Added User: {email}')

    def check_password(self, password, user_email):
        # get the hpass:
        user_db, user_db_cursor = self.__get_db()
        user_db_cursor.execute("SELECT hpass FROM users WHERE email=?", user_email)
        hpass = user_db_cursor.fetchone()[0] # I presume you checked user_exists()
        user_db.close()

        return security.verify_password(password, hpass)

    def get(self, user):
        '''
        **Purpose**
            get user details, or return None
            Also works as a 'is_user_valid()' method
        '''
        user_db, user_db_cursor = self.__get_db()
        user_db_cursor.execute("SELECT email FROM users WHERE email= :email", {'email': email})
        res = user_db_cursor.fetchone()
        user_db.close()
        if res: return res[0]
        return None

    def user_exists(self, email:str) -> bool:
        """
        **Purpose**
            Check if a user exists already

        """
        user_db, user_db_cursor = self.__get_db()
        user_db_cursor.execute("SELECT email FROM users WHERE email= :email", {'email': email})
        res = user_db_cursor.fetchone()
        user_db.close()
        if res: return True
        return None
