from os import path
import sqlite3


DB_NAME = 'database.db'


class DB:
    def __init__(self) -> None:
        pass


    # Create database
    def create():
        if not path.exists(DB_NAME):
            conn = sqlite3.connect(DB_NAME)

            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT,
                password TEXT,
                fullname TEXT,
                created_date_unix TIMESTAMP
            );''')

            c.execute('''CREATE TABLE IF NOT EXISTS links (
                link_id INTEGER  PRIMARY KEY AUTOINCREMENT,
                link_title TEXT,
                link_url TEXT,
                user_id INTEGER,
                created_date_unix TIMESTAMP
            );''')

            conn.commit()
            conn.close()


    # Do query shortcut
    def query(sql, args):
        conn = sqlite3.connect(DB_NAME)

        c = conn.cursor()
        c.execute(sql, args)

        return conn, c
