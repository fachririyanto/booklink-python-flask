from flask import Blueprint, render_template, request
from flask_login import current_user, login_required
from . import APP_NAME, PW_SALT
from .db import DB
from .models import User, Link
import hashlib
import sqlite3


views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'GET':
        keyword = request.args.get('keyword', '')

    links = Link.get_links({
        'keyword': keyword,
        'page': 1,
        'limit': 8,
        'user': current_user.id,
    })

    total_links = Link.get_total_links({
        'keyword': keyword,
        'user': current_user.id,
    })

    return render_template('index.html', args={
        'app_name': APP_NAME,
        'page_title': 'Home',
        'user': current_user,
        'current_user': User.get(current_user.id),
        'links': links,
        'total_links': total_links,
        'keyword': keyword,
    })


@views.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    message = ''
    message_category = ''
    save_button = ''

    if request.method == 'POST':
        data = request.form

        save_button = data.get('save_button')

        match save_button:
            case 'save_profile':
                message, message_category = do_save_profile(data)
            case 'save_new_password':
                message, message_category = do_save_new_password(data)

    return render_template('edit-profile.html', args={
        'app_name': APP_NAME,
        'page_title': 'Home',
        'user': current_user,
        'current_user': User.get(current_user.id),
        'save_button': save_button,
        'message_category': message_category,
        'message': message
    })


def do_save_profile(data):
    email = data.get('email')
    fullname = data.get('fullname')

    from .func import is_email

    if email == '':
        return 'Email required.', 'error'
    elif not is_email(email):
        return 'Invalid email.', 'error'
    elif fullname == '':
        return 'Full name required.', 'error'
    else:
        old_email = data.get('old_email')

        if email != old_email:
            found_user = User.get_user_by_email(email)

            if found_user:
                return 'Email is already exists.', 'error'

        try:
            conn, c = DB.query("UPDATE users SET email = ?, fullname = ? WHERE user_id = ?", (email, fullname, current_user.id,))
            conn.commit()
        except sqlite3.Error as err:
            print(err)
            return 'Failed to save profile because an error.', 'error'

        conn.close()

        return 'Profile saved.', 'success'


def do_save_new_password(data):
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')

    if old_password == '':
        return 'Old password is empty.', 'error'
    elif new_password == '':
        return 'New password is empty.', 'error'
    elif confirm_password == '':
        return 'Confirm password is empty.', 'error'
    elif confirm_password != new_password:
        return 'Invalid confirm password.', 'error'
    else:
        hashed_old_password = hashlib.pbkdf2_hmac(
            'sha256',
            old_password.encode('utf-8'),
            PW_SALT,
            100000
        )

        # Check user old password
        try:
            conn, c = DB.query("SELECT email FROM users WHERE user_id = ? AND password = ?", (current_user.id, hashed_old_password))
            conn.commit()
        except sqlite3.Error as err:
            print(err)
            return 'Failed to check old password because an error.', 'error'

        found_password = c.fetchone()

        if not found_password:
            return 'Invalid old password.', 'error'

        # Save new password
        hashed_new_password = hashlib.pbkdf2_hmac(
            'sha256',
            new_password.encode('utf-8'),
            PW_SALT,
            100000
        )

        try:
            conn, c = DB.query("UPDATE users SET password = ? WHERE user_id = ?", (hashed_new_password, current_user.id,))
            conn.commit()
        except sqlite3.Error as err:
            print(err)
            return 'Failed to save new password because an error', 'error'

        conn.close()

        return 'New password saved.', 'success'
