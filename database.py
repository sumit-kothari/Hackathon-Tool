from boto3 import resource
from boto3.dynamodb.conditions import Key, Attr
import time
import constants
from hashlib import sha256
import pandas as pd


USER_TABLE = constants.USER_TABLE_NAME
COMPETITION_TABLE = constants.COMPETITION_TABLE_NAME
SUBMISSION_TABLE = constants.SUBMISSION_TABLE_NAME
TEAM_TABLE = constants.TEAM_TABLE

# The boto3 dynamoDB resource
dynamodb_resource = resource('dynamodb', region_name='eu-west-1', aws_access_key_id=constants.AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=constants.AWS_SECRET_ACCESS_KEY)


def VALIDATE_USER(email, password):

    print(email, password)
    table = dynamodb_resource.Table(USER_TABLE)
    response = table.scan(
        FilterExpression=Attr('useremail').eq(
            email) & Attr('userpassword').eq(password)
    )
    items = response['Items']
    
    if len(items) == 1:
        return True, items[0]

    return False, None

def VALIDATE_USER_EMAIL(email):
    if '.com' in email:
        table = dynamodb_resource.Table(USER_TABLE)
        response = table.scan(
            FilterExpression=Attr('useremail').eq(email) 
        )
        items = response['Items']
        
        if len(items) > 0:
            return True, items[0]

    return False, None


def GET_COMPETITION_DETAIL(competition_id):

    table = dynamodb_resource.Table(COMPETITION_TABLE)
    response = table.scan(
        FilterExpression=Attr('competition_id').eq(competition_id)
    )
    items = response['Items']

    if len(items) == 1:
        return True, items[0]

    return False, None


def GET_ALL_COMPETITION_DETAILS():

    table = dynamodb_resource.Table(COMPETITION_TABLE)
    response = table.scan(
        FilterExpression=Attr('open').ne('False')
    )
    items = response['Items']

    if len(items) > 0:
        return True, items

    return False, None



def GET_USER_SUBMISSIONS_DETAIL(competition_id, user_id):

    table = dynamodb_resource.Table(SUBMISSION_TABLE)
    response = table.scan(
        FilterExpression=Attr('competition_id').eq(
            competition_id) & Attr('user_id').eq(user_id)
    )
    items = response['Items']

    if len(items) > 0:
        return True, items[0]

    return False, []



def GET_COMPETITION_SUBMISSIONS_DETAIL(competition_id):

    table = dynamodb_resource.Table(SUBMISSION_TABLE)
    response = table.scan(
        FilterExpression=Attr('competition_id').eq(competition_id)
    )
    items = response['Items']

    if len(items) > 0:
        return True, items

    return False, []


def __filter_top_submissions(items):
    df = pd.DataFrame(items)

    print("df.shape original =", df.shape)

    df['submission_score'] = df['submission_score'].apply(
        lambda x: float(x) if len(x.strip()) > 0 else None)

    df = df[df['submission_score'].notnull()]

    print("df.shape null removed =", df.shape)
    print("df.info() =", df.info())

    if df.shape[0] < 1:
        return []

    data_sorted = df.sort_values(['submission_score'], ascending=[True],inplace=False) 
    data_sorted1 = data_sorted.drop_duplicates(subset='team_name')

    df_top_10 = data_sorted1.nsmallest(10, 'submission_score')

    return_list = df_top_10.to_dict('records')

    return return_list


def GET_TOP_SUBMISSIONS_DETAIL(competition_id):
    status, all_items = GET_COMPETITION_SUBMISSIONS_DETAIL(competition_id)

    # print(status, all_items)
    if status:
        items = __filter_top_submissions(all_items)

        return True, items

    return False, []



def SUBMIT_NEW_SUBMISSION(submission_dict):
    print(submission_dict)
    table = dynamodb_resource.Table(SUBMISSION_TABLE)
    table.put_item(
        Item={
            'submission_id': str(int(time.time())),
            'submission_score': submission_dict['submission_score'],
            'user_id': submission_dict['user_id'],
            'submission_timestamp': str(time.time()),
            'competition_id': submission_dict['competition_id'],
            'submission_url': submission_dict['submission_url'],
            'team_name': submission_dict['team_name'],
            'team_id': submission_dict['team_id'],
            'user_name':  submission_dict['user_name'],
            'submission_type': submission_dict['submission_type'],
            'submission_score_display': submission_dict['submission_score_display']
        }
    )

    return True


def UPDATE_SUBMISSION(submission_id, submission_dict):
    print(submission_id, submission_dict)
    
    table = dynamodb_resource.Table(SUBMISSION_TABLE)
   
    response = table.update_item(
        Key={
            'submission_id': submission_id
        },
        UpdateExpression="set submission_score_display = :x, submission_score = :y",
        ExpressionAttributeValues={
            ':y': submission_dict['submission_score'],
            ':x': submission_dict['submission_score_display']
        },
        ReturnValues="UPDATED_NEW"
    )

    if response:
        print("UpdateItem succeeded:")
        print(response)
        return True

    return False



def CREATE_NEW_USER(user_dict):
    print(user_dict)
    table = dynamodb_resource.Table(USER_TABLE)

    userid = user_dict['useremail'] + '__' + str(int(time.time()))  # unix_timestamp
    
    user_empid = ' '
    if user_dict['user_empid']:
        user_empid = user_dict['user_empid']

    table.put_item(
        Item={
            'userid': userid,
            'useremail': user_dict['useremail'],
            'username': user_dict['username'],
            'userdisplayname': user_dict['userdisplayname'],
            'userpassword': user_dict['userpassword'],
            'reset_password_flag': user_dict['reset_password_flag'],
            'team_id': ' ',
            'team_name': ' ',
            'user_empid': user_empid
        }
    )

    return True, userid


def UPDATE_USER_DETAIL(userid, user_dict):
    table = dynamodb_resource.Table(USER_TABLE)
    response = table.update_item(
        Key={
            'userid': userid
        },
        UpdateExpression="set userpassword = :p, reset_password_flag = :r",
        ExpressionAttributeValues={
            ':p': user_dict['userpassword'],
            ':r': 'False'
        },
        ReturnValues="UPDATED_NEW"
    )

    if response:
        print("UpdateItem succeeded:")
        print(response)
        return True

    return False


def UPDATE_USER_TEAM_DETAIL(userid, teamid, teamname):
    table = dynamodb_resource.Table(USER_TABLE)
    response = table.update_item(
        Key={
            'userid': userid
        },
        UpdateExpression="set team_id = :t, team_name = :n",
        ExpressionAttributeValues={
            ':t': teamid,
            ':n': teamname
        },
        ReturnValues="UPDATED_NEW"
    )

    if response:
        print("UpdateItem succeeded:")
        print(response)
        return True

    return False



def GET_TEAM_DETAIL(team_name):
    table = dynamodb_resource.Table(TEAM_TABLE)
    response = table.scan(
        FilterExpression=Attr('team_name').eq(team_name)
    )
    items = response['Items']

    if len(items) == 1:
        return True, items[0]

    return False, None


def CREATE_NEW_TEAM(team_dict):
    print(team_dict)
    table = dynamodb_resource.Table(TEAM_TABLE)

    teamid = team_dict['team_name'] + '__' + \
        str(int(time.time()))  # unix_timestamp

    try:
        table.put_item(
            Item={
                'teamid': teamid,
                'competition_id': str(team_dict['competition_id']),
                'team_name': team_dict['team_name'],
                'team_member_ids': team_dict['team_member_ids'],
                'team_created_timestamp': str(int(time.time()))
            }
        )
        return True, teamid
    except Exception as error:
        print(error)
        return False, None
    


def CREATE_NEW_COMPETITION(create_competition_dict):
    print(create_competition_dict)
    table = dynamodb_resource.Table(COMPETITION_TABLE)

    try:
        table.put_item(
            Item=create_competition_dict
        )
        return True
    except Exception as error:
        print(error)
        return False
