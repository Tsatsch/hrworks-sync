import csv
from dataclasses import dataclass
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from utils import api


@dataclass
class WorkingHoursRaw:
    person_number: str
    project_name: str
    date: str
    start_time: str
    end_time: str

@dataclass
class WorkingHoursAPI:
    person_number: str
    project_number: str
    begin_timestamp: str
    end_timestamp: str


def parse_csv(csv_file):
    """ parse given csv from user """
    data = []
    with open(csv_file, 'r') as file:
        reader = csv.reader(file, delimiter=';')
        next(reader)
        for row in reader:
            data.append(WorkingHoursRaw(*row))
    
    if duplicates_exist(data):
        raise ValueError("Duplicate entries found in CSV file")
    return data


def obtain_project_id(projects_list, project_name):
    """ obtain project id from project name """
    for project in projects_list:
        if(project["name"].strip() == project_name.strip()):
            return project["number"]
    return None

def convert_dmt_to_ISO8601_utc(date, time):
    """ combine separate date and time and convert to ISO8601 format and UTC timezone """
    # Combine the parsed time with the specific date and assign the timezone
    date_time = datetime.combine(date, time.time(), tzinfo=ZoneInfo("Europe/Berlin"))
    # Convert the datetime object to UTC
    date_time_utc = date_time.astimezone(timezone.utc)
    # Format datetime object to ISO8601
    formatted_date_time_utc = date_time_utc.strftime("%Y%m%dT%H%M%S") + "Z"
    return formatted_date_time_utc


def generate_api_working_hours(token, csv_file):
    working_hours = []
    data_list = parse_csv(csv_file)
    for data in data_list:
        project_number = obtain_project_id(api.get_projects(token), data.project_name)

        date_obj = datetime.strptime(data.date, "%d.%m.%Y")
        start_time_obj = datetime.strptime(data.start_time, "%H:%M")
        end_time_obj = datetime.strptime(data.end_time, "%H:%M")

        datetime_start = convert_dmt_to_ISO8601_utc(date_obj, start_time_obj)
        datetime_end = convert_dmt_to_ISO8601_utc(date_obj, end_time_obj)

        working_hours.append(WorkingHoursAPI(data.person_number, project_number, datetime_start, datetime_end))

    if time_overlapping(working_hours):
        raise ValueError("Overlapping working hours found in CSV file. Please verify the CSV file")
    return working_hours


def time_overlapping(working_hours):
    """ check if there are no overlapping working hours for sinlge person """
    for i in range(len(working_hours)):
        for j in range(i+1, len(working_hours)):
            if working_hours[i].person_number == working_hours[j].person_number:
                if (working_hours[i].datetime_start <= working_hours[j].datetime_start <= working_hours[i].datetime_end) or (working_hours[i].datetime_start <= working_hours[j].datetime_end <= working_hours[i].datetime_end):
                    return True
    return False


def duplicates_exist(data):
    duplicates = []
    seen = set()
    for item in data:
        if item in seen:
            duplicates.append(item)
        else:
            seen.add(item)
    return len(duplicates) > 0