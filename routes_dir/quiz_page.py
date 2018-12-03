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
from s3_bucket import GET_S3_FILE


quiz_page = Blueprint('quiz_page', constants.APP_NAME,
                       template_folder='templates')

@quiz_page.route('/quiz_page')
def quiz_page_route():
    final_nav_header = getSessionInfo()
    content_html = parseMarkdownLocal(constants.QUIZ_RULES_MARKDOWN_FILE)

    return render_template('quiz/quiz.html', title=get_app_title(), final_nav_header=final_nav_header, iframe_url=constants.QUIZ_IFRAME_URL, quiz_rules_html=content_html)


@quiz_page.route('/quiz_leaderboard')
def quiz_leaderboard():
    final_nav_header = getSessionInfo()

    file_object = GET_S3_FILE(constants.QUIZ_LEADERBOARD_DATAFILE)
    df_top_10 = pd.read_csv(io.BytesIO(file_object))
    top_10_list = df_top_10.to_dict('records')

    return render_template('quiz/quiz_leaderboard.html', title=get_app_title(), final_nav_header=final_nav_header, quiz_data=top_10_list)
