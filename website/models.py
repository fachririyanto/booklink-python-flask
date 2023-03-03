from flask_login import UserMixin
from .db import DB
import sqlite3


class User(UserMixin):
    def __init__(self, id):
        self.id = id

    
    def get(id):
        try:
            conn, c = DB.query("SELECT email, fullname FROM users WHERE user_id = ?", (id,))
            conn.commit()
        except sqlite3.Error as err:
            print(err)
            return False

        found_user = c.fetchone()

        conn.close()

        return found_user


    def get_user_by_email(email):
        try:
            conn, c = DB.query("SELECT email, fullname FROM users WHERE email = ?", (email,))
            conn.commit()
        except sqlite3.Error as err:
            print(err)
            return False

        found_user = c.fetchone()

        conn.close()

        return found_user


    def list(args={
        'keyword': '',
        'page': 1,
        'limit': 10
    }):
        sql_string = "SELECT user_id, email, fullname FROM users"
        params = list()

        if args['keyword'] != '':
            sql_string += " WHERE email LIKE ? OR fullname LIKE ?"
            params.append('%' + args['keyword'] + '%')
            params.append('%' + args['keyword'] + '%')

        params = tuple(params)

        offset = (int(args['page']) * int(args['limit'])) - int(args['limit'])

        sql_string += " LIMIT " + str(offset) + ", " + str(args['limit'])

        try:
            conn, c = DB.query(sql_string, params)
            conn.commit()
        except sqlite3.Error as err:
            print(err)
            return []

        found_users = c.fetchall()

        conn.close()

        return found_users
    

class Link:
    def get_links(args={
        'keyword': '',
        'page': 1,
        'limit': 10,
        'user': 0,
    }):
        sql_string = "SELECT link_id, link_title, link_url FROM links WHERE user_id = ?"
        params = list()
        params.append(args['user'])

        if args['keyword'] != '':
            sql_string += " AND link_title LIKE ? OR link_url LIKE ?"
            params.append('%' + args['keyword'] + '%')
            params.append('%' + args['keyword'] + '%')

        params = tuple(params)

        sql_string += " ORDER BY created_date_unix DESC"

        offset = (int(args['page']) * int(args['limit'])) - int(args['limit'])

        sql_string += " LIMIT " + str(offset) + ", " + str(args['limit'])

        try:
            conn, c = DB.query(sql_string, params)
            conn.commit()
        except sqlite3.Error as err:
            print(err)
            return []
        
        found_links = c.fetchall()

        conn.close()

        return found_links
    

    def get_total_links(args={
        'keyword': '',
        'user': 0,
    }):
        sql_string = "SELECT COUNT(link_id) as total FROM links WHERE user_id = ?"
        params = list()
        params.append(args['user'])

        if args['keyword'] != '':
            sql_string += " AND link_title LIKE ? OR link_url LIKE ?"
            params.append('%' + args['keyword'] + '%')
            params.append('%' + args['keyword'] + '%')

        params = tuple(params)

        try:
            conn, c = DB.query(sql_string, params)
            conn.commit()
        except sqlite3.Error as err:
            print(err)
            return 0
        
        found_total = c.fetchone()

        conn.close()

        return found_total[0]
