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
    except requests.exceptions.RequestException:
        raise ValueError("Token-Generierung fehlgeschlagen. Bitte überprüfen Sie Ihren Access Key und Secret Key.")
    return response.json()["token"]


def get_project_info(project_id, token):
    """ Retrieves data on specific project """
    url = f"{BASE_URL}/working-times/projects/{project_id}"
    headers = {
    'Authorization': f'Bearer {token}',
    }
    response = requests.request("GET", url, headers=headers)
    return response.json()

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
            "projectNumber": working_hour.project_id,
        })


    payload = json.dumps({
        "deleteOverlappingWorkingTimes": False,
        "data": data
        })
    
    print(payload)

    headers = {
    'Authorization': f'Bearer {token}',
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.status_code