from flask import Blueprint, render_template, redirect, request as flask_request, make_response, session
import constants
import boto3
import botocore
import io
import pandas as pd
from sklearn.metrics import accuracy_score
from database import VALIDATE_USER, VALIDATE_USER_EMAIL, GET_COMPETITION_DETAIL, GET_ALL_COMPETITION_DETAILS, GET_USER_SUBMISSIONS_DETAIL, GET_TOP_SUBMISSIONS_DETAIL, SUBMIT_NEW_SUBMISSION, CREATE_NEW_USER, UPDATE_USER_DETAIL
from hashlib import sha256, sha512
import subprocess
from common_utils import getSessionInfo, get_app_title
import re


signup_page = Blueprint('signup_page', constants.APP_NAME, template_folder='templates')


@signup_page.route('/signup')
def signup():
    if "user_data" in session:
        return redirect("/competitions")

    final_nav_header = getSessionInfo()

    return render_template('signup.html', title=get_app_title(), final_nav_header=final_nav_header)


@signup_page.route('/signup_error')
def signup_error():
    if "user_data" in session:
        return redirect("/competitions")

    return render_template('error/signup.html', title=get_app_title())


@signup_page.route('/signup_success')
def signup_success():
    final_nav_header = getSessionInfo()

    return render_template('success/signup.html', title=get_app_title(), final_nav_header=final_nav_header)


@signup_page.route('/submit_signup_data', methods=['POST'])
def submit_signup_data():
    form_data = flask_request.form

    email = form_data.get("user_email")
    #password = form_data.get("user_password")
    user_name = form_data.get("user_name").strip()
    user_name_unique = form_data.get("user_name").strip()
    user_eid = ' '

    if not (re.match("^[a-zA-Z0-9]+$", form_data.get("user_password"))):
        return redirect("/signup_error")
    else:
        password = form_data.get("user_password")

    hex_password = sha512(str(password).encode('utf-8')).hexdigest()

    new_user_data = {
        'useremail': email,
        'username': user_name_unique,
        'userdisplayname': user_name,
        'userpassword': hex_password,
        'user_empid': user_eid,
        'reset_password_flag': 'True'
    }

    response, user_data = VALIDATE_USER_EMAIL(email)
    print("User already registered :", response)

    if not response:
        try:
            success_flag, userid = CREATE_NEW_USER(new_user_data)

            if success_flag:
                new_user_data["userid"] = userid
                session['user_data'] = new_user_data
                resp = make_response(redirect("/signup_success"))

            else:
                # return "Unable to register, please contact LKM team"
                resp = make_response(redirect("/signup_error"))
        except Exception as e:
            print(e)
            # return "Unable to register, please contact LKM team"
            resp = make_response(redirect("/signup_error"))

    else:
        resp = make_response(redirect("/signup_error"))

    return resp
