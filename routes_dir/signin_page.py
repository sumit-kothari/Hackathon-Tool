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


signin_page = Blueprint('signin_page', constants.APP_NAME, template_folder='templates')


@signin_page.route('/signin')
def signin():
    if "user_data" in session:
        return redirect("/competitions")

    return render_template('signin.html', title=get_app_title())


@signin_page.route('/signout')
def signout():
    if "user_data" in session:
        del session["user_data"]
        session.clear()

    return redirect("/signin")


@signin_page.route('/signout_confirm')
def signout_confirm():
    if "user_data" in session:
        final_nav_header = getSessionInfo()
        return render_template('signout.html', title=get_app_title(), final_nav_header=final_nav_header)

    return redirect("/signout")


@signin_page.route('/signin_error')
def signin_error():
    if "user_data" in session:
        return redirect("/competitions")

    return render_template('error/signin.html', title=get_app_title())


@signin_page.route('/submit_signin_data', methods=['POST'])
def submit_signin_data():
    form_data = flask_request.form

    email = form_data.get("user_email")
   
    if not (re.match("^[a-zA-Z0-9]+$", form_data.get("user_password"))):        
        return redirect("/signin_error")
    else:
        password = form_data.get("user_password")

    hex_password = sha512(str(password).encode('utf-8')).hexdigest()


    response, user_data = VALIDATE_USER(email, hex_password)
    if response:
        session['user_data'] = user_data

        resp = make_response(redirect("/competitions"))
        if session['user_data']['reset_password_flag'] and session['user_data']['reset_password_flag'] == "True":
            resp = make_response(redirect("/profile_update"))
    else:
        resp = make_response(redirect("/signin_error"))

    return resp
