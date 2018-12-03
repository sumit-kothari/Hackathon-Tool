from flask import Blueprint, render_template, redirect, request as flask_request, make_response, session
import constants
import boto3
import botocore
import io
import pandas as pd 
from sklearn.metrics import accuracy_score
from database import VALIDATE_USER, GET_COMPETITION_DETAIL, GET_ALL_COMPETITION_DETAILS, GET_USER_SUBMISSIONS_DETAIL, GET_TOP_SUBMISSIONS_DETAIL, SUBMIT_NEW_SUBMISSION, CREATE_NEW_USER, UPDATE_USER_DETAIL
from hashlib import sha256
import subprocess
from common_utils import getSessionInfo, get_app_title, parseMarkdownLocal


terms_page = Blueprint('terms_page', constants.APP_NAME,
                       template_folder='templates')


@terms_page.route('/rules')
def terms_page_view():
    final_nav_header = getSessionInfo()

    content_html = parseMarkdownLocal(constants.TERMS_RULES_MARKDOWN_FILE)

    return render_template('terms/terms_global.html', title=get_app_title(), final_nav_header=final_nav_header, content_html=content_html)


@terms_page.route('/faq')
def faq_page():
    final_nav_header = getSessionInfo()

    content_html = parseMarkdownLocal(constants.FAQ_MARKDOWN_FILE)

    return render_template('faq_global.html', title=get_app_title(), final_nav_header=final_nav_header, content_html=content_html)


@terms_page.route('/contactus')
def contact_us():
    final_nav_header = getSessionInfo()

    content_html = parseMarkdownLocal(constants.CONTACT_US_MARKDOWN_FILE)

    return render_template('terms/contact_us.html', title=get_app_title(), final_nav_header=final_nav_header, content_html=content_html)

@terms_page.route('/about')
def about_us():
    final_nav_header = getSessionInfo()

    content_html = parseMarkdownLocal(constants.ABOUT_US_MARKDOWN_FILE)

    return render_template('terms/about_us.html', title=get_app_title(), final_nav_header=final_nav_header, content_html=content_html)
