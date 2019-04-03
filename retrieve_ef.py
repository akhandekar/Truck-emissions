import time
import json
import pandas as pd
import math
from influxdb import InfluxDBClient
from influxdb import DataFrameClient
from datetime import datetime, timedelta
from pytz import timezone
import datetime######################## MAIN ########################
import pytz
import hashlib
import argparse
#import configparser
import subprocess
import numpy as np
from datetime import datetime
import os
import sys
import ast
import datetime     # for general datetime object handling
import rfc3339      # for date object -> date string
import iso8601      # for date string -> date object

import pytz

local_tz = pytz.timezone('US/Pacific') # use your local timezone name here



from Influx_Dataframe_Client import Influx_Dataframe_Client
#To run this script clone the repo and use the command: python3 demo.py conf.ini


######################## MAIN ########################
def get_date_object(date_string):
  return iso8601.parse_date(date_string)

def get_date_string(date_object):
  return rfc3339.rfc3339(date_object)

def utc_to_local(utc_dt):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt)


def main():
    # read arguments passed at .py file call
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="Need to specify config file, see example_server.ini")
    parser.add_argument("file_name", help="Filename to put data in")
    args = parser.parse_args()
    conf_file = args.config
    file_name = args.file_name

    bc_sensors = ['abcd','ae16','ae33','ma300']

    co2_sensors = ['li820','li7000','sba5','vco2']
    nox_sensors = ['caps','ucb']

    fields_list = ["AP_count","test_field"]
    test_client = Influx_Dataframe_Client(conf_file,'DB_config')
    database='ef_test_4'
    df_list = []

    # Build query string
    query_string = "select * from emission_factor"
    print(query_string)
    # Query influx server and return generator
    iflux_result = test_client.query(query_string,database)
    # Get dictionary
    iflux_gen = iflux_result.get_points()
    sensor_dict = {}
    json_data = []
    for x in iflux_gen:
        sensor_dict = {}
        x['time'] = get_date_object(x['time'])
        localtz = timezone('US/Pacific')
        x['time'] = utc_to_local(x['time'])
        x['time'] = x['time'].replace(tzinfo=None)

        for key, value in x.items():
            sensor_dict[key] = value
        json_data.append(sensor_dict)

    df_test = pd.DataFrame.from_dict(json_data, orient='columns')
    df_test = df_test.set_index('time')

    print(df_test.head(5))

    df_test.to_csv(file_name)

    return

if __name__ == "__main__":
    main()
