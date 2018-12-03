from flask import session, Markup as flask_markup
import mistune
import boto3
import botocore
import constants
import io


markdown = mistune.Markdown()

BUCKET_NAME_S3 = constants.S3_BUCKET_NAME
s3 = boto3.client(
    's3',
    aws_access_key_id=constants.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=constants.AWS_SECRET_ACCESS_KEY
)


def getSessionInfo(all_info = False):
    final_nav_header = 'signin'
    user_session_data = None

    if 'user_data' in session:
        final_nav_header = '({0})'.format(session['user_data']['username'])
        
        if 'team_name' in session['user_data']:
            final_nav_header = '{0} ({1})'.format(session['user_data']['team_name'], session['user_data']['username'])
        
        # override
        final_nav_header = '{0} ({1})'.format('Logout', session['user_data']['username'])
        user_session_data = session['user_data']


    if all_info:
        return final_nav_header, user_session_data

    return final_nav_header


def getS3FilePath(filepath):
    parsedFilePath = filepath

    if ('https://' in filepath) or ('https://' in filepath):
        filepathUrl = filepath.split(BUCKET_NAME_S3 + '/')
        parsedFilePath = filepathUrl[1]

    return parsedFilePath


def parseMarkdown(filepath):
    parsedFilePath = getS3FilePath(filepath)

    try:
        obj = s3.get_object(Bucket=BUCKET_NAME_S3, Key=parsedFilePath)
        file_data_obj = io.BytesIO(obj['Body'].read())
        file_data_md = file_data_obj.getvalue().decode("utf-8")
        file_data_html = markdown(file_data_md)

        return file_data_html
    except Exception as error:
        print(error)
        return '<h1>Data file unavaiable, please try again later</h1>'


def parseMarkdownLocal(filepath):
    with open(filepath, 'r') as file_object:
        file_data_html = markdown(file_object.read())

        return flask_markup(file_data_html)

    return flask_markup('<h1>Data unavaiable, please try again later</h1>')
        

def get_app_title():
    app_title = '<p class="app-header-title">{0}<br><span class="app-header-sub-title">Powered By: <b>{1}</b></span></p>'.format(
        constants.APP_NAME, constants.APP_POWERED_BY)

    return flask_markup(app_title)
