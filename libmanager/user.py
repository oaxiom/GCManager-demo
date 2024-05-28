#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024
#
# Author(s):

import sys, os, sqlite3, uuid

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
        user_db_cursor.execute('CREATE TABLE users (UID INT, username TEXT, hpass TEXT, is_admin INT)')
        user_db_cursor.execute('INSERT INTO users VALUES (?, ?, ?, ?)', (uuid.uuid4().bytes_le, 'sysadminrescue', '$2b$12$Q2mKXhVenm.EtRfdzkcAf.EWikxvRbu/KZ4zkMQmioY.RCiMRrYJC', True))
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

    def add_user(self, uuid, username, password, is_admin=False):
        """
        **Purpose**
            Add a user;
        """
        user_db, user_db_cursor = self.__get_db()

        hpass = security.hash_password(password)

        # TODO: Salt the user db with the MAC address?

        user_db_cursor.execute('INSERT INTO users VALUES (?, ?, ?, ?)', (uuid.bytes_le, username, hpass, is_admin))

        user_db.commit()
        user_db.close()

        if is_admin:
            self.log.info(f'Added an Admin User: {username}')
        else:
            self.log.info(f'Added a Normal User: {username}')

        return True

    def delete_user(self, username):
        """

        **Purpose**
            Delete a non-admin user

        """
        if self.is_admin(username):
            return False

        user_db, user_db_cursor = self.__get_db()
        user_db_cursor.execute("DELETE FROM users WHERE username=?", (username, ))
        user_db.commit()
        user_db.close()

        return True

    def check_password(self, username, password):
        # get the hpass:
        user_db, user_db_cursor = self.__get_db()
        user_db_cursor.execute("SELECT hpass FROM users WHERE username=?", (username, ))
        hpass = user_db_cursor.fetchone()[0] # I presume you checked user_exists()
        user_db.close()

        # Bad? surely, as password is transmitted in the clear...
        # But if it's wrong, it doesn't matter?
        # But if it's right, it does...

        """
        Yeah, the CURL is like this:
        curl -X 'POST' \
        'http://127.0.0.1:8000/auth/token' \
        -H 'accept: application/json' \
        -H 'Content-Type: application/x-www-form-urlencoded' \
        -d 'grant_type=&username=admin%40notanemail.edu.cn&password=notarealpass&scope=&client_id=aa&client_secret=aa'

        # That can't be right...
        """
        return security.verify_password(password, hpass)

    def change_password(self, username, newpassword):
        # Check old != new
        ret = self.check_password(username, newpassword)
        if ret:
            return False # old password == new password!

        hpass = security.hash_password(newpassword)

        user_db, user_db_cursor = self.__get_db()
        user_db_cursor.execute("UPDATE users SET hpass=? WHERE username=?", (hpass, username, ))
        user_db.commit()
        user_db.close()

        return True

    def get(self, username:str):
        '''
        **Purpose**
            get user details, or return None
            Also works as a 'is_user_valid()' method
        '''
        user_db, user_db_cursor = self.__get_db()
        user_db_cursor.execute("SELECT username FROM users WHERE username= :username", {'username': username})
        res = user_db_cursor.fetchone()
        user_db.close()
        if res: return res[0]
        return None

    def user_exists(self, username:str) -> bool:
        """
        **Purpose**
            Check if a user exists already

        """
        user_db, user_db_cursor = self.__get_db()
        user_db_cursor.execute("SELECT username FROM users WHERE username= :username", {'username': username})
        res = user_db_cursor.fetchone()
        user_db.close()
        if res: return True
        return None

    def is_admin(self, username:str) -> bool:
        """
        **Purpose**
            Check if this user is an admin

        """
        if not self.user_exists(username):
            return False

        user_db, user_db_cursor = self.__get_db()
        user_db_cursor.execute("SELECT is_admin FROM users WHERE username= :username", {'username': username})
        res = user_db_cursor.fetchone()
        user_db.close()
        return bool(res[0])
