from flask import Blueprint, render_template, redirect, request as flask_request, make_response, session
import constants
import boto3
import botocore
import io
import pandas as pd
from sklearn.metrics import accuracy_score
from database import VALIDATE_USER, GET_TEAM_DETAIL, GET_COMPETITION_DETAIL, GET_ALL_COMPETITION_DETAILS, GET_USER_SUBMISSIONS_DETAIL, GET_TOP_SUBMISSIONS_DETAIL, SUBMIT_NEW_SUBMISSION, CREATE_NEW_USER, UPDATE_USER_DETAIL, VALIDATE_USER_EMAIL
from hashlib import sha256
import subprocess
from common_utils import getSessionInfo, get_app_title
from create_all_teams_code import CREATE_TEAM_1_GO


teams_page = Blueprint('teams_page', constants.APP_NAME,
                       template_folder='templates')


@teams_page.route('/create_team')
def create_team_view():
    final_nav_header, session_info_data = getSessionInfo(True)

    print(final_nav_header, session_info_data)
    current_member_email = ''
    if session_info_data:
        current_member_email = session_info_data['useremail']

        if session_info_data.get('team_id') and session_info_data['team_id'].strip() != '':
            return redirect('/view_team')

    return render_template('team/create_team.html', title=get_app_title(), final_nav_header=final_nav_header, current_member_email=current_member_email)


@teams_page.route('/create_team_submit', methods=['POST'])
def create_team_submit():
    final_nav_header = getSessionInfo()

    form_data = flask_request.form

    print(form_data)

    team_name = form_data.get("team_name")
    team_competition_id = form_data.get("team_competition_id")
    team_data = {
        'teamname': team_name,
        'competition_id': team_competition_id
    }

    for i in range(1, 7):
        user_member_email_i = form_data.get("member_{}".format(i))
        if user_member_email_i == '':
            user_member_email_i = ' '

        team_data['team_member{}'.format(i)] = user_member_email_i

    try:
        CREATE_TEAM_1_GO(team_data)

        response, user_data = VALIDATE_USER_EMAIL(session['user_data']['useremail'])
        if response:
            session['user_data'] = user_data
            resp = make_response(redirect("/create_team_success"))

    except Exception as e:
        print(e)
        # return "Unable to register, please contact LKM team"
        resp = make_response(redirect("/create_team_error"))

    return resp


@teams_page.route('/create_team_error')
def create_team_error():
    final_nav_header = getSessionInfo()

    return render_template('error/create_team.html', title=get_app_title(), final_nav_header=final_nav_header)


@teams_page.route('/create_team_success')
def create_team_success():
    final_nav_header = getSessionInfo()

    return render_template('success/create_team.html', title=get_app_title(), final_nav_header=final_nav_header)



@teams_page.route('/view_team')
def view_team():
    final_nav_header, session_info_data = getSessionInfo(True)

    current_member_email = ''
    if session_info_data:
        current_member_email = session_info_data['useremail']
        team_name = session_info_data.get('team_name')

        if team_name and team_name.strip() == '':
            return redirect('/create_team')


        status, team_details = GET_TEAM_DETAIL(team_name)

        if not status:
            return redirect('/create_team')

        
        team_members = team_details.get('team_member_ids')
        team_members = [ x.split('__')[0] for x in team_members ]

        return render_template('team/view_team.html', title=get_app_title(), final_nav_header=final_nav_header, team_name=team_name, team_members=team_members)

    return redirect('/signin')
