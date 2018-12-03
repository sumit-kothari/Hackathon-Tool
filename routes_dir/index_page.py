from flask import Blueprint, render_template, redirect, request as flask_request, make_response, session
import constants
import boto3
import botocore
import io
import pandas as pd 
from sklearn.metrics import accuracy_score
from database import VALIDATE_USER, GET_COMPETITION_DETAIL, GET_ALL_COMPETITION_DETAILS, GET_USER_SUBMISSIONS_DETAIL, GET_TOP_SUBMISSIONS_DETAIL, SUBMIT_NEW_SUBMISSION, CREATE_NEW_USER, UPDATE_USER_DETAIL
import subprocess
from common_utils import getSessionInfo, get_app_title, parseMarkdownLocal


index_page = Blueprint('index_page', constants.APP_NAME,
                       template_folder='templates')

@index_page.route('/home')
def home():
    final_nav_header = getSessionInfo()

    return render_template('index.html', title=get_app_title(), final_nav_header=final_nav_header)

@index_page.route('/')
def index():
    final_nav_header = getSessionInfo()

    return render_template('index.html', title=get_app_title(), final_nav_header=final_nav_header)
