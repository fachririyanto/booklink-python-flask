from flask import Flask, render_template
from flask_login import LoginManager
from .db import DB
from .models import User
import sqlite3


APP_NAME = 'Booklink'
PW_SALT = b'hello_playground'


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hello_world'

    # Register routes
    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    # Handle 404 error page
    app.register_error_handler(404, page_not_found)

    # Create database
    DB.create()

    # Authentication
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'error'
    login_manager.login_message = 'Session expired. Please login again.'

    @login_manager.user_loader
    def load_user(id):
        try:
            conn, c = DB.query("SELECT user_id FROM users WHERE user_id = ?", (id))
            conn.commit()
        except sqlite3.Error as err:
            print(err)
            return ''

        found_user = c.fetchone()

        conn.close()

        return User(found_user[0])

    login_manager.init_app(app)

    # Register API
    from .api import register_api
    register_api(app)

    return app


def page_not_found(e):
    return render_template('404.html', args={
        'app_name': APP_NAME,
        'page_title': 'Error 404: Page not found',
    }), 404
