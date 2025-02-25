from db.sybase import DbConnection
from db.sql_queries import get_surveys_list, insert_survey_grade, check_access_survey_for_user, survey_long_name,\
    all_voted_surveys_for_user, insert_survey_grade_as_commentary


def get_all_surveys():
    result = DbConnection.execute_query(get_surveys_list)
    return result


def insert_grade(survey_id:int, user_id: int, grade: int):
    result = DbConnection.execute_query(insert_survey_grade, survey_id, user_id, grade)
    return result


def insert_grade_as_commentary(survey_id: int, user_id: int, grade: str):
    result = DbConnection.execute_query(insert_survey_grade_as_commentary, survey_id, user_id, grade)
    return result


def split_survey_callback(callback_data: str) -> tuple:
    return callback_data.split()[1], callback_data.split()[2]


def get_available_surveys(user_id: int) -> list:
    result = DbConnection.execute_query(check_access_survey_for_user, user_id)
    return result


def get_all_surveys_voted_by_user(user_id: int):
    result = DbConnection.execute_query(all_voted_surveys_for_user, user_id)
    return result


def get_survey_description(survey_id: int) -> list:
    result = DbConnection.execute_query(survey_long_name, survey_id)
    return result
