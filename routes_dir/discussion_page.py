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

discussion_page = Blueprint('discussion_page', constants.APP_NAME, template_folder='templates')

@discussion_page.route('/discussion')
def discussion_page_view():
    final_nav_header = getSessionInfo()
    content_html = parseMarkdownLocal(constants.DISCUSSION_RULES_MARKDOWN_FILE)

    return render_template('discussion_page.html', title=get_app_title(), final_nav_header=final_nav_header, iframe_url=constants.DISCUSSION_IFRAME_URL, discussion_rules_html=content_html)


@discussion_page.route('/learning_board')
def learning_board():
    final_nav_header = getSessionInfo()
    content_html = parseMarkdownLocal(constants.LEARNING_BOARD_MARKDOWN_FILE)

    return render_template('learning_board.html', title=get_app_title(), final_nav_header=final_nav_header, content_html=content_html)
