import requests
import json
from utils import parser

BASE_URL = "https://api.hrworks.de/v2"

def generate_token(access_key, secret_access_key):
    url = f"{BASE_URL}/authentication"

    payload = json.dumps({
        "accessKey": access_key,
        "secretAccessKey": secret_access_key
    })
    try:
        response = requests.request("POST", url, data=payload)
    except requests.exceptions.RequestException as e:
        raise ValueError("Token generation failed. Please check your credentials.")
    return response.json()["token"]


def get_projects(token):
    url = f"{BASE_URL}/working-times/projects"
    headers = {
    'Authorization': f'Bearer {token}',
    }
    response = requests.request("GET", url, headers=headers)
    return response.json()["projects"]

def update_working_hours(token, csv_file):
    url = f"{BASE_URL}/working-times"
    data = []
    working_hours = parser.generate_api_working_hours(token, csv_file)
    for working_hour in working_hours:
        data.append({
            "personnelNumber": working_hour.person_number,
            "beginDateAndTime": working_hour.begin_timestamp,
            "endDateAndTime": working_hour.end_timestamp,
            "type": "workingTime",
            "projectNumber": working_hour.project_number,
        })


    payload = json.dumps({
        "deleteOverlappingWorkingTimes": False,
        "data": data
        })

    headers = {
    'Authorization': f'Bearer {token}',
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.status_code