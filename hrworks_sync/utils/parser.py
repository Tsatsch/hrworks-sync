import csv
from dataclasses import dataclass
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
# from utils import api


@dataclass
class WorkingHoursRaw:
    person_number: str
    project_number: int
    date: str
    start_time: str
    end_time: str

@dataclass
class WorkingHoursAPI:
    person_number: str
    project_number: int
    begin_timestamp: str
    end_timestamp: str


def parse_csv(csv_file):
    """ parse given csv from user """
    data = read_and_validate_csv(csv_file)
    if (no_duplicated_rows_found(data)):
        workinghours_raw = [WorkingHoursRaw(*row) for row in data]
        return workinghours_raw    
    else:
        workinghours_raw = [WorkingHoursRaw(*row) for row in data]
        return workinghours_raw


# def obtain_project_id(projects_list, project_number):
#     """ obtain project id from project name """
#     for project in projects_list:
#         if(project["name"].strip() == project_number.strip()):
#             return project["number"]
#     return None

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
        project_number = int(data.project_number)

        date_obj = datetime.strptime(data.date, "%d.%m.%Y")
        start_time_obj = datetime.strptime(data.start_time, "%H:%M")
        end_time_obj = datetime.strptime(data.end_time, "%H:%M")

        datetime_start = convert_dmt_to_ISO8601_utc(date_obj, start_time_obj)
        datetime_end = convert_dmt_to_ISO8601_utc(date_obj, end_time_obj)

        working_hours.append(WorkingHoursAPI(data.person_number, project_number, datetime_start, datetime_end))

    overlapping_times = time_overlapping(working_hours)
    if len(overlapping_times) > 0:
        overlap1, overlap2 = overlapping_times[0]
        raise ValueError(f"Überschneidende Arbeitszeiten in der CSV-Datei gefunden:\n"
                 f"Personnummer: {overlap1.person_number}\n"
                 f"Überschneidung in:\n"
                 f"Eintrag Nr.1: {format_timestamp(overlap1.begin_timestamp)} - {format_timestamp(overlap1.end_timestamp)}\n"
                 f"Eintrag Nr.2: {format_timestamp(overlap2.begin_timestamp)} - {format_timestamp(overlap2.end_timestamp)}\n"
                 f"Bitte korrigieren Sie Ihre CSV-Datei\n"
                 )
    return working_hours


def time_overlapping(working_hours):
    """ check if there are no overlapping working hours for single person """
    overlapping_entries = []
    for i in range(len(working_hours)):
        for j in range(i+1, len(working_hours)):
            if working_hours[i].person_number == working_hours[j].person_number:
                begin_i = datetime.strptime(working_hours[i].begin_timestamp, "%Y%m%dT%H%M%SZ")
                end_i = datetime.strptime(working_hours[i].end_timestamp, "%Y%m%dT%H%M%SZ")
                begin_j = datetime.strptime(working_hours[j].begin_timestamp, "%Y%m%dT%H%M%SZ")
                end_j = datetime.strptime(working_hours[j].end_timestamp, "%Y%m%dT%H%M%SZ")
                if (begin_i < end_j and begin_j < end_i):
                    overlapping_entries.append((working_hours[i], working_hours[j]))
    return overlapping_entries


def duplicates_exist(data):
    duplicates = []
    seen = set()
    for item in data:
        if item in seen:
            duplicates.append(item)
        else:
            seen.add(item)
    return duplicates

def format_timestamp(timestamp):
    datetime_object = datetime.strptime(timestamp, "%Y%m%dT%H%M%SZ")
    formatted_time = datetime_object.strftime("%d-%m-%y %H:%M")
    return formatted_time

def read_and_validate_csv(file):
    with open(file, 'r') as f:
        first_line = f.readline()
        if ";" not in first_line:
            raise ValueError(f"Die CSV-Datei verwendet nicht das richtige Trennzeichen. Es wird ein Semikolon ';' in der ersten Reihe erwartet. Bitte korrigieren Sie die Datei und versuchen Sie es erneut.")
    with open(file, 'r') as f:
        reader = csv.reader(f, delimiter=';')
        headers = next(reader)

    expected_headers = ['Personalnummer', 'Projektname', 'Datum', 'Startzeit', 'Endzeit']
    if headers != expected_headers:
        raise ValueError(f"CSV file has incorrect headers. Expected {expected_headers}, but got {headers}")
    
    data = []
    with open(file, 'r') as f:
        reader = csv.reader(f, delimiter=';')
        next(reader)
        for row in reader:
            if len(row) != len(expected_headers):
                raise ValueError(f"Incorrect number of columns in row: {row}")
            data.append(row)

    return data

def no_duplicated_rows_found(data):
    duplicates = []
    seen = set()
    for item in data:
        item_tuple = tuple(item)
        if item_tuple in seen:
            duplicates.append(item)
        else:
            seen.add(item_tuple)


    if len(duplicates) > 0 :
        raise ValueError(f"Duplicate entries found in CSV file.\n{duplicates[0]}")
    return True
