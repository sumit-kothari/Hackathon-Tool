from flask import Blueprint, render_template, redirect, request as flask_request, make_response, session
import constants
import boto3
import botocore
import io
import pandas as pd
from sklearn.metrics import accuracy_score
from database import VALIDATE_USER, GET_COMPETITION_DETAIL, GET_ALL_COMPETITION_DETAILS, GET_USER_SUBMISSIONS_DETAIL, GET_TOP_SUBMISSIONS_DETAIL, SUBMIT_NEW_SUBMISSION, CREATE_NEW_USER, UPDATE_USER_DETAIL
from hashlib import sha256, sha512
import subprocess
from common_utils import getSessionInfo, get_app_title
import re


profile_page = Blueprint('profile_page', constants.APP_NAME, template_folder='templates')


@profile_page.route('/profile_update')
def profile_update():
    if "user_data" not in session:
        return redirect("/signin")

    final_nav_header = getSessionInfo()

    user_data = {
        "email": session['user_data']['useremail'],
        "username": session['user_data']['username']
    }

    return render_template('profile_update.html', title=get_app_title(), final_nav_header=final_nav_header, user_data=user_data)


@profile_page.route('/submit_profile_update_data', methods=['POST'])
def submit_profile_update_data():
    if "user_data" not in session:
        return redirect("/signin")

    form_data = flask_request.form

    user_email = form_data.get("user_email")
    user_name_unique = form_data.get("user_name_unique")

    if not ((re.match("^[a-zA-Z0-9]+$", form_data.get("user_password"))) and (re.match("^[a-zA-Z0-9]+$", form_data.get("user_new_password")))):
        return redirect("/profile_update_error")
    else:
        user_old_password = form_data.get("user_password")
        user_new_password = form_data.get("user_new_password")

    hex_password = sha512(str(user_new_password).encode('utf-8')).hexdigest()
    hex_old_password = sha512(str(user_old_password).encode('utf-8')).hexdigest()

    responseValidateUser, user_data = VALIDATE_USER(
        user_email, hex_old_password)

    if responseValidateUser:
        user_detail_object = {
            'username': user_name_unique,
            'userpassword': hex_password,
        }
        response = UPDATE_USER_DETAIL(
            session['user_data']['userid'], user_detail_object)

        if not response:
            return redirect("/profile_update_error")

        subprocess.Popen(["bash", "update_password_in_all.sh",
                          user_name_unique, user_email, user_new_password])
    else:
        return redirect("/profile_update_error")

    return redirect("/competitions")


@profile_page.route('/profile_update_error')
def profile_update_error():
    if "user_data" not in session:
        return redirect("/signin")

    final_nav_header = session['user_data']['username']

    return render_template('error/profile_update.html', title=get_app_title(), final_nav_header=final_nav_header)
