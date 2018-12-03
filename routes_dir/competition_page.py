from flask import Blueprint, render_template, redirect, request as flask_request, make_response, session, Markup
import constants
import boto3
import botocore
import io
import time
import pandas as pd 
from sklearn.metrics import accuracy_score, r2_score
from database import VALIDATE_USER, VALIDATE_USER_EMAIL, GET_COMPETITION_DETAIL, GET_ALL_COMPETITION_DETAILS, GET_USER_SUBMISSIONS_DETAIL, GET_TOP_SUBMISSIONS_DETAIL, SUBMIT_NEW_SUBMISSION, CREATE_NEW_USER, UPDATE_USER_DETAIL, GET_TEAM_DETAIL
import subprocess
from common_utils import getSessionInfo, get_app_title, parseMarkdown, getS3FilePath


competition_page = Blueprint('competition_page', constants.APP_NAME, template_folder='templates')


BUCKET_NAME_S3 = constants.S3_BUCKET_NAME
s3 = boto3.client(
    "s3",
    aws_access_key_id=constants.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=constants.AWS_SECRET_ACCESS_KEY
)


def upload_file_to_s3(file, bucket_name, current_timestamp):

    filePath = '{dir}/{user}/{timestamp}/{fileDataObj}'.format(dir=constants.S3_SUBMISSION_DIRECTORY,
                                                            user=session['user_data']['username'], timestamp=current_timestamp, fileDataObj=file.filename)
    print(filePath)
    try:

        s3.upload_fileobj(
            file,
            bucket_name,
            filePath,
            ExtraArgs={
                "ContentType": file.content_type
            }
        )

    except Exception as e:
        print("Something Happened: ", e)
        return None

    return filePath


def allowed_file(filename):
    is_file_allow = filename.lower().endswith(('.csv', '.py', '.r', '.zip'))
    print('is_file_allow =', is_file_allow)
    
    return is_file_allow


def __getEval_Classification(df_real, df_predict, competition_data):
    df_merge = pd.merge(left=df_real, right=df_predict, on="Index", how="left")

    print("df_real.shape =", df_real.shape)
    print("df_predict.shape =", df_predict.shape)
    print("df_merge.shape =", df_merge.shape)

    column_x = '{}_x'.format(competition_data['competition_y_label'])
    column_y = '{}_y'.format(competition_data['competition_y_label'])

    accuracy_score_value = accuracy_score(
        df_merge[column_x], df_merge[column_y])

    accuracy_score_value_display = '{} %'.format(round(float(accuracy_score_value) * 100, 2))

    return accuracy_score_value, accuracy_score_value_display


def __getEval_Regression(df_real, df_predict, competition_data):
    df_merge = pd.merge(left=df_real, right=df_predict, on="Index", how="left")

    print("df_real.shape =", df_real.shape)
    print("df_predict.shape =", df_predict.shape)
    print("df_merge.shape =", df_merge.shape)

    column_x = '{}_x'.format(competition_data['competition_y_label'])
    column_y = '{}_y'.format(competition_data['competition_y_label'])

    r2_score_value = r2_score(
        df_merge[column_x], df_merge[column_y])

    return r2_score_value, r2_score_value


def getEvaluation(competition_id, file, bucket_name):

    df_predict = pd.read_csv(file)

    flag, competition_data = GET_COMPETITION_DETAIL(competition_id)
    
    if not flag:
        print("competition_detail not found, competition_id = " , competition_id)

    filePathValidation = getS3FilePath(competition_data['competition_validation_data_url'])

    obj = s3.get_object(Bucket=bucket_name, Key=filePathValidation)
    df_real = pd.read_csv(io.BytesIO(obj['Body'].read()))

    print(df_predict.head())

    if competition_data['competition_type'] == 'classification':
        print('finding classification score')
        submission_score, submission_score_display = __getEval_Classification(
            df_real, df_predict, competition_data)
    else:
        print('finding classification score')
        submission_score, submission_score_display = __getEval_Regression(
            df_real, df_predict, competition_data)

    submission_data = {
        'submission_score': str(submission_score),
        'user_id': str(session['user_data']["userid"]),
        'user_name': str(session['user_data']["username"]),
        'team_name': str(session['user_data']["team_name"]),
        'team_id': str(session['user_data']["team_id"]),
        'competition_id': str(competition_id),
        'submission_type': competition_data['competition_type'],
        'submission_score_display': str(submission_score_display)
    }

    return submission_data



def __filter_competition_data(competition_data):
    competition_data_dict = {
        'active': [],
        'old': []
    }

    for competition in competition_data:
        if competition.get('register_allowed') and competition.get('register_allowed') == 'True':
            competition_data_dict['active'].append(competition)
        else:
            competition_data_dict['old'].append(competition)


    return competition_data_dict


@competition_page.route('/competitions')
def competition():
    final_nav_header = getSessionInfo()
    route_competition_detail = 'competition_detail_overview'
    flag_current_old = False
    
    if 'user_data' in session:
        response, user_data = VALIDATE_USER_EMAIL(session['user_data']['useremail'])
        session['user_data'] = user_data

    if 'user_data' in session and 'team_name' in session['user_data'] and session['user_data']['team_name'].strip() is not '':
        team_success_flag, team_data = GET_TEAM_DETAIL(session['user_data']['team_name'])
        
        route_competition_detail = 'competition_detail'

        if team_success_flag:
            competition_status, competition_data = GET_COMPETITION_DETAIL(
                team_data["competition_id"])
            competition_data = [competition_data]

            if not competition_status:
                competition_data = []

        else:
            competition_data = []
    else:
        competition_status, competition_data = GET_ALL_COMPETITION_DETAILS()

        competition_data = __filter_competition_data(competition_data)
        flag_current_old = True

        route_competition_detail = 'competition_detail_overview'

        if not competition_status:
            competition_data = []

    return render_template('competition.html', title=get_app_title(), final_nav_header=final_nav_header, competition_data=competition_data, route_competition_detail=route_competition_detail, flag_current_old=flag_current_old)


def __competition_detail_data(competition_id):
    
    final_nav_header = getSessionInfo()

    competition_detail = GET_COMPETITION_DETAIL(competition_id)
    
    competition_detail_readme_overview_path = competition_detail[1]['competition_overview_readme']
    competition_detail_readme_overview_parsed = parseMarkdown(competition_detail_readme_overview_path)

    competition_detail_readme_faq_path = competition_detail[1]['competition_faq_readme']
    competition_detail_readme_faq_parsed = parseMarkdown(competition_detail_readme_faq_path)

    competition_data_readme_path = competition_detail[1]['competition_data_readme']
    competition_data_readme_parsed = parseMarkdown(competition_data_readme_path)
    
    competition_submission_readme_path = competition_detail[1]['competition_submission_readme']
    competition_submission_readme_parsed = parseMarkdown(competition_submission_readme_path)

    competition_leaderboard_readme_path = competition_detail[1]['competition_leaderboard_readme']
    competition_leaderboard_readme_parsed = parseMarkdown(competition_leaderboard_readme_path)

    competition_leaderboard_readme_path = competition_detail[1]['competition_leaderboard_readme']
    competition_leaderboard_readme_parsed = parseMarkdown(competition_leaderboard_readme_path)


    competition_detail_rules_readme_path = competition_detail[1]['competition_detail_rules_readme']
    competition_detail_rules_readme_parsed = parseMarkdown(
        competition_detail_rules_readme_path)


    dynamic_competition_data = {
        "competition_detail": competition_detail[1],
        "competition_detail_faq_overview": Markup(competition_detail_readme_overview_parsed),
        "competition_detail_faq_readme": Markup(competition_detail_readme_faq_parsed),
        "competition_detail_data_readme": Markup(competition_data_readme_parsed),
        "competition_detail_submission_readme": Markup(competition_submission_readme_parsed),
        "competition_detail_leaderboard_readme": Markup(competition_leaderboard_readme_parsed),
        "competition_detail_rules_readme": Markup(competition_detail_rules_readme_parsed),
    }

    if session.get('user_data') and session['user_data']["userid"]:
        user_id = session['user_data']["userid"]
        user_submissions_detail = GET_USER_SUBMISSIONS_DETAIL(competition_id, str(user_id))
        top_submissions_detail = GET_TOP_SUBMISSIONS_DETAIL(competition_id)

        dynamic_competition_data["user_submissions_detail"] = user_submissions_detail[1]
        dynamic_competition_data["top_submissions_detail"] = top_submissions_detail[1]

        print("user_submissions_detail ", user_submissions_detail)
        print("top_submissions_detail ", top_submissions_detail)

    print("competition_detail ", competition_detail)
    print("competition_detail_readme_overview_parsed")
    print(competition_detail_readme_overview_parsed)
    print("competition_detail_readme_faq_parsed")
    print(competition_detail_readme_faq_parsed)

    return {
        'dynamic_competition_data': dynamic_competition_data,
        'final_nav_header': final_nav_header
    }


@competition_page.route('/competition_detail_overview/<competition_id>')
def competition_detail_overview(competition_id):
    competition_response = __competition_detail_data(competition_id)

    final_nav_header = getSessionInfo()

    return render_template('competition_detail_overview.html', title=get_app_title(), final_nav_header=final_nav_header, tab_active={"overview": "is-active", "leaderboard": ""}, competition_data=competition_response['dynamic_competition_data'])


@competition_page.route('/competition_detail/<competition_id>')
def competition_detail(competition_id):
    if "user_data" not in session:
        if 'user_data' in session:
            response, user_data = VALIDATE_USER_EMAIL(session['user_data']['useremail'])
            session['user_data'] = user_data
        return redirect("/signin")

    competition_response = __competition_detail_data(competition_id)

    return render_template('competition_detail.html', title=get_app_title(), final_nav_header=competition_response['final_nav_header'], tab_active={"overview": "is-active", "leaderboard": ""}, competition_data=competition_response['dynamic_competition_data'])


@competition_page.route('/competition_detail_leaderboard/<competition_id>')
def competition_detail_leaderboard(competition_id):
    if "user_data" not in session:
        return redirect("/signin")

    competition_response = __competition_detail_data(competition_id)

    return render_template('competition_detail.html', title=get_app_title(), final_nav_header=competition_response['final_nav_header'], tab_active={"overview": "", "leaderboard": "is-active"}, competition_data=competition_response['dynamic_competition_data'])

def __user_submission_allowed(competition_id):
    if "user_data" not in session or "team_name" not in session["user_data"]:
        return False

    team_name = session["user_data"]["team_name"]

    flag, team_data = GET_TEAM_DETAIL(team_name)

    if team_data["competition_id"] and int(competition_id) == int(team_data["competition_id"]):
        return True

    return False


@competition_page.route('/submit_competition_submission', methods=['POST'])
def submit_competition_submission():
    print((flask_request.args))
    print((flask_request.form))
    print((len(flask_request.files)))

    try:
        if len(flask_request.files) < 2:
            print("error invalid files missing ")
            return make_response(redirect(
                "/competition_submission_error/" + flask_request.form.get("competition_id")))
       
        submission_allowed_flag = __user_submission_allowed(
            flask_request.form.get("competition_id"))

        if not submission_allowed_flag:
            print("__user_submission_allowed =", submission_allowed_flag)
            return make_response(redirect(
                "/competition_submission_error/" + flask_request.form.get("competition_id")))



        current_timestamp = str(int(time.time()))
        
        # B
        # model_file = flask_request.files["model_file"]
        code_file = flask_request.files["code_file"]
        submission_file = flask_request.files["submission_file"]

        submission_url = '{dir}/{user}/{timestamp}/{fileDataObj}'.format(dir=constants.S3_SUBMISSION_DIRECTORY,
                                                                                          user=session['user_data']['username'], timestamp=current_timestamp, fileDataObj=submission_file.filename)
        print('submission_url =', submission_url)

        submission_data = {
            'submission_score': ' ', 
            'user_id': str(session['user_data']["userid"]), 
            'user_name': str(session['user_data']["username"]),
            'team_name': str(session['user_data']["team_name"]), 
            'team_id': str(session['user_data']["team_id"]),
            'competition_id': '' + flask_request.form.get("competition_id"),
            'submission_type': ' ', 
            'submission_score_display': ' ', 
            'submission_url': submission_url
        }
        
        upoadFileList = [code_file, submission_file]

        for file in upoadFileList:
            # C.
            if file.filename == "":
                print("error invalid filename ", file)
                return make_response(redirect(
                    "/competition_submission_error/" + flask_request.form.get("competition_id")))

            # D.
            if file and allowed_file(file.filename):
                
                output = upload_file_to_s3(
                    file, BUCKET_NAME_S3, current_timestamp)
                print(str(output))
            else:
                print("error invalid file extensions", file)
                return make_response(redirect(
                    "/competition_submission_error/" + flask_request.form.get("competition_id")))

       
        SUBMIT_NEW_SUBMISSION(submission_data)

        resp = make_response(redirect(
            "/competition_submission_success/" + flask_request.form.get("competition_id")))
        # resp = make_response(redirect(
        #     "/competition_detail_leaderboard/" + flask_request.form.get("competition_id")))

        return resp
    except Exception as e:
        print(e)
        return make_response(redirect(
            "/competition_submission_error/" + flask_request.form.get("competition_id")))

    


@competition_page.route('/competition_submission_error/<competition_id>')
def competition_submission_error(competition_id):
    if "user_data" not in session:
        return redirect("/signin")

    final_nav_header = getSessionInfo()

    return render_template('error/competition_submission.html', title=get_app_title(), final_nav_header=final_nav_header, competition_id=competition_id)


@competition_page.route('/competition_submission_success/<competition_id>')
def competition_submission_success(competition_id):
    if "user_data" not in session:
        return redirect("/signin")

    final_nav_header = getSessionInfo()

    return render_template('success/competition_submission.html', title=get_app_title(), final_nav_header=final_nav_header, competition_id=competition_id)
