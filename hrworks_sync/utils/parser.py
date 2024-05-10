import pandas as pd
from dataclasses import dataclass
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from utils import api


@dataclass
class WorkingHoursRaw:
    person_number: str
    project_name: str
    project_id: int
    date: str
    start_time: str
    end_time: str

@dataclass
class WorkingHoursAPI:
    person_number: str
    project_id: int
    begin_timestamp: str
    end_timestamp: str


def parse_excel(csv_file):
    """ parse given excel from user """
    data = read_and_validate_excel(csv_file)
    if (no_duplicated_rows_found(data)):
        workinghours_raw = [WorkingHoursRaw(*row) for row in data]
        return workinghours_raw    
    else:
        raise ValueError("Es gibt doppelte Einträge in der Excel-Tabelle.")


def convert_dmt_to_ISO8601_utc(date, time):
    """ combine separate date and time and convert to ISO8601 format and UTC timezone """
    # Combine the parsed time with the specific date and assign the timezone
    date_time = datetime.combine(date, time, tzinfo=ZoneInfo("Europe/Berlin"))
    # Convert the datetime object to UTC
    date_time_utc = date_time.astimezone(timezone.utc)
    # Format datetime object to ISO8601
    formatted_date_time_utc = date_time_utc.strftime("%Y%m%dT%H%M%S") + "Z"
    return formatted_date_time_utc


def generate_api_working_hours(token, excel_file):
    working_hours = []
    data_list = parse_excel(excel_file)
    for data in data_list:
        datetime_start = convert_dmt_to_ISO8601_utc(data.date, data.start_time)
        datetime_end = convert_dmt_to_ISO8601_utc(data.date, data.end_time)

        working_hours.append(WorkingHoursAPI(data.person_number, int(data.project_id), datetime_start, datetime_end))

    overlapping_times = time_overlapping(working_hours)
    if len(overlapping_times) > 0:
        overlap1, overlap2 = overlapping_times[0]
        raise ValueError(f"Überschneidende Arbeitszeiten in der Excel-Tabelle gefunden:\n"
                 f"Personnummer: {overlap1.person_number}\n"
                 f"Überschneidung in:\n"
                 f"Eintrag Nr.1: {format_timestamp(overlap1.begin_timestamp)} - {format_timestamp(overlap1.end_timestamp)}\n"
                 f"Eintrag Nr.2: {format_timestamp(overlap2.begin_timestamp)} - {format_timestamp(overlap2.end_timestamp)}\n"
                 f"Bitte korrigieren Sie Ihre Excel-Tabelle\n"
                 )
    
    # verification if worktime update is possible
    for working_hour_entry in working_hours:
        project_data = api.get_project_info(working_hour_entry.project_id, token)
        # verify that all projects are active
        if not project_data['status'] == 'Active':
            raise ValueError(f"Projekt {project_data['name']} ist nicht aktiv. Es ist hat den status {project_data['status']}.\nBuchung auf dieses Projekt ist nicht erlaubt.")
        # verify that person is included into the project
        project_members = project_data['projectTeam']['activePersons']
        if not any(person['personnelNumber'] == working_hour_entry.person_number for person in project_members):
            raise ValueError(f"Person {working_hour_entry.person_number} ist nicht ein aktives Teammitgleid im Projekt {project_data['name']} enthalten.\nBuchung auf dieses Projekt ist nicht erlaubt.")
    
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

def read_and_validate_excel(file):
    df = pd.read_excel(file, sheet_name='Arbeitszeiten')

    expected_headers = ['Personalnummer', 'ProjektName', 'ProjektID', 'Datum', 'Startzeit', 'Endzeit']
    if list(df.columns) != expected_headers:
        raise ValueError(f"Die Kopfzeilen der Excel-Tabelle stimmen nicht übereins. Erwartet sind: {expected_headers}")


    for index, row in df.iterrows():
        if row.isnull().any() and row.notnull().any():
            raise ValueError(f"Die Zeile {index+1} in der Excel-Tabelle hat leere Felder.")

    data = df.values.tolist()

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
