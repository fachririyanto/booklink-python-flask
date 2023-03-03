from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, current_user, login_required, logout_user
from . import APP_NAME, PW_SALT
from .db import DB
from .models import User
from .func import is_email
import hashlib
import datetime
import sqlite3


auth = Blueprint('auth', __name__)


# Login Controller
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        data = request.form

        email = data.get('email')
        password = data.get('password')
        remember = data.get('remember')

        if email == '':
            flash('Email required.', category='error')
        elif not is_email(email):
            flash('Invalid email.', category='error')
        elif password == '':
            flash('Password required.', category='error')
        else:
            found_user = do_login(email)

            if found_user:
                hashed_password = hashlib.pbkdf2_hmac(
                    'sha256',
                    password.encode('utf-8'),
                    PW_SALT,
                    100000
                )

                if hashed_password == found_user[1]:
                    user = User(
                        found_user[0]
                    )

                    is_remember = True if remember == 'on' else False

                    login_user(user, remember=is_remember)

                    return redirect(url_for('views.home'))
                else:
                    flash('Invalid password.', category='error')
            else:
                flash('User not found.', category='error')

    return render_template('login.html', args={
        'app_name': APP_NAME,
        'page_title': 'Login',
        'user': current_user
    })


def do_login(email):
    try:
        conn, c = DB.query("SELECT user_id, password FROM users WHERE email = ?", (email,))
        conn.commit()
    except sqlite3.Error as err:
        print(err)
        return False

    found_user = c.fetchone()

    conn.close()

    return found_user


# Sign up Controller
@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        data = request.form

        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        fullname = data.get('fullname')

        if email == '':
            flash('Email required.', category='error')
        elif not is_email(email):
            flash('Invalid email.', category='error')
        elif password == '':
            flash('Password required.', category='error')
        elif confirm_password == '':
            flash('Confirm password required.', category='error')
        elif password != confirm_password:
            flash('Invalid confirm password.', category='error')
        elif fullname == '':
            flash('Full name required.', category='error')
        else:
            found_user = User.get_user_by_email(email)

            if not found_user:
                is_saved = do_signup(email, password, fullname)

                if is_saved:
                    flash('Account created!', category='success')
                else:
                    flash('Failed to sign up.', category='error')
            else:
                flash('Email is already exists.', category='error')

    return render_template('signup.html', args={
        'app_name': APP_NAME,
        'page_title': 'Sign Up',
        'user': current_user
    })


def do_signup(email, password, fullname):
    time = datetime.datetime.now()
    unix = time.timestamp()

    hashed_password = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        PW_SALT,
        100000
    )

    try:
        conn, c = DB.query("INSERT INTO users (email, password, fullname, created_date_unix) VALUES (?, ?, ?, ?)", (email, hashed_password, fullname, unix))
        conn.commit()
    except sqlite3.Error as err:
        print(err)
        return False
    
    conn.close()

    return True


# Logout Controller
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
