from flask_restful import Resource, Api, reqparse, request
from flask_login import current_user
from functools import wraps
from .db import DB
from .models import Link
import datetime
import sqlite3


def register_api(app):
    api = Api(app)

    api.add_resource(REST_Link, '/api/link')
    api.representation('application/json')


def authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated:
            return func(*args, **kwargs)

        return {
            'code': 401,
            'message': 'Not authorized.',
            'data': [],
        }

    return wrapper


class REST_Link(Resource):
    method_decorators = [authenticate]


    def get(self):
        links = Link.get_links({
            'keyword': request.args.get('keyword', ''),
            'page': request.args.get('page', 1),
            'limit': request.args.get('limit', 8),
            'user': current_user.id,
        })

        return {
            'code': 200,
            'message': 'Fetch success.',
            'data': links,
        }
    

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('url')
        parser.add_argument('desc')

        args = parser.parse_args()

        if args['url'] == '':
            return {
                'code': 400,
                'message': '',
                'data': [],
            }
        
        time = datetime.datetime.now()
        unix = time.timestamp()
        
        try:
            conn, c = DB.query("INSERT INTO links (link_title, link_url, user_id, created_date_unix) VALUES (?, ?, ?, ?)", (args['desc'], args['url'], current_user.id, unix))
            conn.commit()
        except sqlite3.Error as err:
            print(err)
            return {
                'code': 400,
                'message': 'Failed to save link because an error.',
                'data': [],
            }

        conn.close()

        return {
            'code': 200,
            'message': 'Link inserted.',
            'data': {
                'link_id': c.lastrowid,
            },
        }
    

    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('link_id')
        parser.add_argument('url')
        parser.add_argument('desc')

        args = parser.parse_args()

        if args['url'] == '':
            return {
                'code': 400,
                'message': '',
                'data': [],
            }
        
        try:
            conn, c = DB.query("UPDATE links SET link_title = ?, link_url = ? WHERE user_id = ? AND link_id = ?", (args['desc'], args['url'], current_user.id, args['link_id']))
            conn.commit()
        except sqlite3.Error as err:
            print(err)
            return {
                'code': 400,
                'message': 'Failed to update link because an error.',
                'data': [],
            }

        conn.close()

        return {
            'code': 200,
            'message': 'Link updated.',
            'data': [],
        }
    

    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('link_id')

        args = parser.parse_args()

        try:
            conn, c = DB.query("DELETE FROM links WHERE link_id = ?", (args['link_id'],))
            conn.commit()
        except sqlite3.Error as err:
            print(err)
            return {
                'code': 400,
                'message': 'Failed to delete link because an error.',
                'data': [],
            }

        conn.close()

        return {
            'code': 200,
            'message': 'Link deleted.',
            'data': [args['link_id']],
        }
