from datetime import datetime, timedelta
import re
from pandas import Timestamp
import pendulum
from typing import List

import time
from bson import ObjectId
import pytz

import pandas as pd

# time is greater than 7 hours
MINUS_TIME = 7 * 60 * 60 * 1000

LOCAL_TZ = pendulum.timezone("Asia/Ho_Chi_Minh")

def convert_datetime_to_unix(value) -> int:
    v = time.mktime(value.timetuple())
    return int(v)

def convert_str_datetime_to_unix(date_str: str, date_format: str = '%Y-%m-%d %H:%M:%S') -> int:
    try:
        value = datetime.strptime(date_str, date_format)
        timestamp = int(time.mktime(value.timetuple()))
        return timestamp
    except ValueError as e:
        raise ValueError(f"Incorrect date format: {e}")
    
def convert_str_datetime_to_milisecond(date_str: str, date_format: str = '%Y-%m-%d %H:%M:%S') -> int:
    try:
        value = datetime.strptime(date_str, date_format)
        timestamp = int(value.timestamp() * 1000)
        return timestamp
    except ValueError as e:
        raise ValueError(f"Incorrect date format: {e}")

# Convert dates to datetime.date objects
def convert_to_date(strdate, date_format:str="%Y%m%d"):
    return datetime.strptime(str(strdate), date_format).date()

def get_current_with_format(format: str = '%Y-%m-%d'):
    return convert_timestamp_without_tz(get_current_unixtime()).strftime(format)

def is_correct_datetime(value) -> bool:
    if isinstance(value, datetime):
        return True
    if isinstance(value, int):
        return True
    return False


def convert_datetime_data(source: dict, datetime_fields: List[str]):
    """
        datetime fields format: datefield$date
            $date: 2023-01-30T07:59:35.108Z
    """
    for field in datetime_fields:
        if field not in source:
            continue
        value = source[field]
        if isinstance(value, dict) and '$date' in value:
            correct_date = value['$date']
            source[field] = pendulum.parse(correct_date, tz=LOCAL_TZ)
            continue
        if is_correct_datetime(value):
            continue
        source[field] = None


def get_current_time():
    return pendulum.now(tz=LOCAL_TZ)

def get_current_unixtime():
    return int(pendulum.now(tz=LOCAL_TZ).timestamp() * 1000)


def convert_timestamp_to_integer(value: Timestamp):
    # Define the UTC+7 timezone
    utc_plus_7 = pytz.timezone('Asia/Ho_Chi_Minh')  # UTC+7
    
    # Localize the naive timestamp to UTC+7, then convert to milliseconds
    if value.tzinfo is None:  # Check if the timestamp is naive
        value = value.tz_localize(utc_plus_7)
    else:
        value = value.astimezone(utc_plus_7)

    return int(value.timestamp())

def convert_timestamp_to_milisecond(value: Timestamp):
    # Define the UTC+7 timezone
    utc_plus_7 = pytz.timezone('Asia/Ho_Chi_Minh')  # UTC+7
    
    # Localize the naive timestamp to UTC+7, then convert to milliseconds
    if value.tzinfo is None:  # Check if the timestamp is naive
        value = value.tz_localize(utc_plus_7)
    else:
        value = value.astimezone(utc_plus_7)

    return int(value.timestamp()) * 1000


def convert_date_to_millisecond(value: datetime) -> int:
    datetime_value = datetime.combine(value, datetime.min.time())
    return convert_timestamp_to_milisecond(pd.Timestamp(datetime_value))



def get_partition_prefix_utc_plus_7(data, partition_field):
    # Get the generation time in UTC
    if isinstance(data['_id'], str):
        generation_time_utc = ObjectId(data[partition_field]).generation_time
    else:
        generation_time_utc = data[partition_field].generation_time
        
    # Define the UTC+7 timezone
    utc_plus_7 = pytz.timezone('Asia/Ho_Chi_Minh')  # UTC+7
    
    # Convert the UTC time to UTC+7
    generation_time_utc_plus_7 = generation_time_utc.astimezone(utc_plus_7)
    
    # Format the time as 'YYYYMM'
    prefix_partition = generation_time_utc_plus_7.strftime('%Y%m')
    
    return prefix_partition

def convertObjectId2VNZone(data, field=None, ts=True):
    if not field:
        field = "_id"

    if isinstance(data[field], str):
        
        generation_time_utc = ObjectId(data[field]).generation_time
    else: # dict
        if isinstance(data[field], dict):
            if "$oid" in data[field].keys():
                strField = data[field]["$oid"]
                generation_time_utc = ObjectId(strField).generation_time   
            else:
                return get_current_unixtime()
        else:
            return get_current_unixtime()

    # Define the UTC+7 timezone
    utc_plus_7 = pytz.timezone('Asia/Ho_Chi_Minh')  # UTC+7
    
    # Convert the UTC time to UTC+7
    generation_time_utc_plus_7 = generation_time_utc.astimezone(utc_plus_7)

    # Convert to unix timestamp
    if ts:
        output_time = int(time.mktime(generation_time_utc_plus_7.timetuple()) * 1000)
    else:
        output_time = generation_time_utc_plus_7


    return output_time

def convertObjectIdValue2VNZone(value, ts=True):

    generation_time_utc = ObjectId(value).generation_time

    # Define the UTC+7 timezone
    utc_plus_7 = pytz.timezone('Asia/Ho_Chi_Minh')  # UTC+7
    
    # Convert the UTC time to UTC+7
    generation_time_utc_plus_7 = generation_time_utc.astimezone(utc_plus_7)

    # Convert to unix timestamp
    if ts:
        output_time = int(time.mktime(generation_time_utc_plus_7.timetuple()) * 1000)
    else:
        output_time = generation_time_utc_plus_7


    return output_time


