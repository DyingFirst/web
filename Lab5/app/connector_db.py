import mysql.connector
from flask import g



class MySQL:
    def __init__(self, cfg):
        self.cfg = cfg

    def config(self):
        return {
            "user": self.cfg['database']['user'],
            "password": self.cfg['database']['password'],
            "database": self.cfg['database']['database'],
            "host": self.cfg['database']['host'],
            "port": self.cfg['database']['port'],
            "auth_plugin": 'mysql_native_password'
        }

    def connection(self):
        if 'db' not in g:
            g.db = mysql.connector.connect(**self.config())
        return g.db

    def close_connection(self, e=None):
        db = g.pop('db', None)
        if db is not None:
            db.close()
