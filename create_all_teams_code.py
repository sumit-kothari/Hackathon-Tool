import pandas as pd
import re
from database import VALIDATE_USER_EMAIL, CREATE_NEW_USER, CREATE_NEW_TEAM, GET_TEAM_DETAIL, UPDATE_USER_TEAM_DETAIL

TEAM_REGISTER_FILE = "static/data/teams_register.csv"


def __get_member_columns(row):
    team_data = row.dropna()
    keys_list = list(team_data.keys())

    r = re.compile("team_member*")
    team_member_columns = list(filter(r.match, keys_list))

    return team_member_columns, team_data


def __validate_team_users(row):
    print("-" * 50)
    print("Validate team member email ids for team =", row["teamname"])
    print("-" * 50)

    team_member_columns, team_data = __get_member_columns(row)
    print(team_member_columns)

    return_flag_list = []
    return_user_data = []

    for member_column in team_member_columns:
        if team_data[member_column]:
            user_email_id = team_data[member_column].strip()

            if not user_email_id == '':
                validate_user_response, user_data = VALIDATE_USER_EMAIL(
                    user_email_id)

                print(user_email_id, validate_user_response)

                if user_data:
                    if  user_data['team_name'] and (user_data['team_name'] == '' or user_data['team_name'] == ' '):
                        return_flag = validate_user_response
                    else:
                        print('User already part of team')
                        return_flag = False

                return_user_data.append(user_data["userid"])
                return_flag_list.append(return_flag)

    response_return = True
    if False in return_flag_list:
        response_return = False

    return response_return, return_user_data


def __create_team(team_data, user_data):
    team_dict = {
        "team_name": team_data["teamname"],
        "team_member_ids": user_data,
        "competition_id": team_data["competition_id"]
    }
    
    success, team_id = CREATE_NEW_TEAM(team_dict)

    return success, team_id 


def __update_user_team_information(user_data, team_id, team_name):
    for user_id in user_data:
        UPDATE_USER_TEAM_DETAIL(user_id, team_id, team_name)


def CREATE_TEAM_1_GO(inputParam):
    df_dict_list= [{
        'teamname': inputParam['teamname'],
        'competition_id': inputParam['competition_id'],
        'team_member1': inputParam['team_member1'],
        'team_member2': inputParam['team_member2'],
        'team_member3': inputParam['team_member3'],
        'team_member4': inputParam['team_member4'],
        'team_member5': inputParam['team_member5'],
        'team_member6': inputParam['team_member6']
    }]
    
    if len(set(df_dict_list[0].values())) < 4:
        print(set(df_dict_list[0].values()))
        print('member are not valid')
        raise AssertionError()

    df = pd.DataFrame(df_dict_list)
    root(df)


def root(df):
    print("-" * 100)
    print("df.head()")
    print(df.head())
    print("-" * 100)

    for index, row in df.iterrows():

        users_auth_response, user_data = __validate_team_users(row)

        if not users_auth_response:
            print("-" * 50)
            print("Not entering data for team {} as some member emails are not registered".format(row["teamname"]))
            print("-" * 50)
            raise AssertionError()
            continue

        print(users_auth_response, user_data)

        validate_team, team_data = GET_TEAM_DETAIL(row["teamname"].strip())

        if validate_team:
            print("-" * 50)
            print("Not entering data for team {} as team is already registered".format(
                row["teamname"]))
            print("-" * 50)
            raise AssertionError()
            continue

        create_team_success, team_id = __create_team(row, user_data)

        print(create_team_success, team_id)
        if not create_team_success: 
            print("-" * 50)
            print("Unable to create team = {} , server issue".format(row["teamname"]))
            print("-" * 50)
            raise AssertionError()
            continue

        __update_user_team_information(user_data, team_id, row["teamname"].strip())
        
        print("-" * 50)
        print(">>>>> DONE for team =", row["teamname"])

    print("-" * 100)
    print(">>>>> DONE for all teams")


if __name__ == '__main__':
    df = pd.read_csv(TEAM_REGISTER_FILE)

    try:
        root(df)
    except Exception as ex:
        print('Exceptition ', ex)
    
