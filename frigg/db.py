import uuid
import hashlib
import mysql.connector

# from hashlib import pbkdf2_hmac
# import uuid
# pbkdf2_hmac('sha256', uuid.UUID('4b2ee001-62e0-4800-bee7-16578a339e5b').bytes, b'dictxiong'*2, 821).hex()
salt = b'dictxiong'*2
iterations = 821

class DBManager:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.init_db()

    def get_conn(self):
        return mysql.connector.connect(
            host = self.config['host'],
            user = self.config['user'],
            password = self.config['password'],
            database = 'frigg'
        )

    def init_db(self):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute('SHOW TABLES')
        tables = [i[0] for i in cursor]
        if 'host' not in tables:
            cursor.execute('CREATE TABLE host (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(32), shadow CHAR(64))')
        if  'var' not in tables:
            cursor.execute('CREATE TABLE var (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(32), value VARCHAR(255))')

    def set_host(self, name, uuid_str):
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            raw = uuid.UUID(uuid_str).bytes
        except:
            self.logger.error('Invalid UUID: %s', uuid_str)
            return False
        shadow = hashlib.pbkdf2_hmac('sha256', raw, salt, iterations).hex()
        cursor.execute('SELECT * FROM host WHERE name = %s', (name,))
        ret = cursor.fetchone()
        if ret:
            if ret[2] == shadow:
                self.logger.info('Host %s not changed', name)
            else:
                cursor.execute('UPDATE host SET shadow = %s WHERE name = %s', (shadow, name))
                self.logger.info('Host %s updated', name)
        else:
            cursor.execute('INSERT INTO host (name, shadow) VALUES (%s, %s)', (name, shadow))
            self.logger.info('Host %s added', name)
        conn.commit()
        return True

    def list_hosts(self):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT name,shadow FROM host')
        return [(i[0], i[1]) for i in cursor.fetchall()]

    def auth_host(self, name, uuid_str):
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            raw = uuid.UUID(uuid_str).bytes
        except:
            self.logger.warning('Invalid UUID: %s', uuid_str)
            return False
        shadow = hashlib.pbkdf2_hmac('sha256', raw, salt, iterations).hex()
        cursor.execute('SELECT * FROM host WHERE name = %s AND shadow = %s', (name, shadow))
        ret = cursor.fetchone()
        if ret:
            return True
        else:
            return False

    def set_var(self, name, value):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM var WHERE name = %s', (name,))
        ret = cursor.fetchone()
        if ret:
            cursor.execute('UPDATE var SET value = %s WHERE name = %s', (value, name))
            self.logger.info('Var %s updated', name)
        else:
            cursor.execute('INSERT INTO var (name, value) VALUES (%s, %s)', (name, value))
            self.logger.info('Var %s added', name)
        conn.commit()
        return True

    def get_var(self, name):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM var WHERE name = %s', (name,))
        ret = cursor.fetchone()
        if ret:
            return ret[2]
        else:
            return None

    def del_var(self, name):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM var WHERE name = %s', (name,))
        ret = cursor.fetchone()
        if ret:
            cursor.execute('DELETE FROM var WHERE name = %s', (name,))
            conn.commit()
            self.logger.info('Var %s deleted', name)
            return True
        else:
            self.logger.error('Var %s not found', name)
            return False

    def list_vars(self):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT name,value FROM var')
        return [(i[0], i[1]) for i in cursor.fetchall()]
