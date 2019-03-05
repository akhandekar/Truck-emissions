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
import configparser
import subprocess
import numpy as np
from datetime import datetime
import os
import sys
import ast
import datetime     # for general datetime object handling
import rfc3339      # for date object -> date string
import iso8601      # for date string -> date object




from Influx_Dataframe_Client import Influx_Dataframe_Client
#To run this script clone the repo and use the command: python3 demo.py conf.ini


######################## MAIN ########################
def get_date_object(date_string):
  return iso8601.parse_date(date_string)

def get_date_string(date_object):
  return rfc3339.rfc3339(date_object)



def main():
    # read arguments passed at .py file call
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="Need to specify config file, see example_server.ini")


    args = parser.parse_args()
    conf_file = args.config
    bc_sensors = ['abcd','ae16','ae33','ma300']

    co2_sensors = ['li820','li7000','sba5','vco2']
    nox_sensors = ['caps','ucb']

    fields_list = ["AP_count","test_field"]
    test_client = Influx_Dataframe_Client(conf_file,'DB_config')
    database='ef_test_4'
    df_list = []

    query_string = "select * from co2"
    iflux_result = test_client.query(query_string,database)
    iflux_gen = iflux_result.get_points()
    i=0
    df_collection = pd.DataFrame()
    for sensor_name in  co2_sensors:
        json = []
        tag_dict = {"sensor_name": sensor_name}
        iflux_gen = iflux_result.get_points(tags=tag_dict)
        #print(iflux_gen)
        for x in iflux_gen:
            sensor_dict = {}
            x['time'] = get_date_object(x['time'])
            #print(x['time']) time is string and can be manipulated for correct format
            #print(type(x['time']))
            #ts = time.strptime(x['time'], '%Y-%m-%dT%H:%M:%S.%f')
            #print(time.mktime(ts))
            sensor_dict[sensor_name] = x['co2']
            sensor_dict['time'] = x['time']
            json.append(sensor_dict)
        #print(json)
        df_list.append(pd.DataFrame.from_dict(json, orient='columns'))
        #df.to_csv(sensor_name + '.csv')
        print(df_list[i].head())
        df_list[i] = df_list[i].set_index('time')
        df_list[i] = df_list[i].resample('1S').mean()
        print(df_list[i].head())
        i +=1

    query_string = "select * from nox"
    iflux_result = test_client.query(query_string,database)
    iflux_gen = iflux_result.get_points()
    for sensor_name in  nox_sensors:
        json = []
        tag_dict = {"sensor_name": sensor_name}
        iflux_gen = iflux_result.get_points(tags=tag_dict)
        #print(iflux_gen)
        for x in iflux_gen:
            sensor_dict = {}
            x['time'] = get_date_object(x['time'])
            #print(x['time']) time is string and can be manipulated for correct format
            #print(type(x['time']))
            #ts = time.strptime(x['time'], '%Y-%m-%dT%H:%M:%S.%f')
            #print(time.mktime(ts))
            sensor_dict[sensor_name] = x['nox']
            sensor_dict['time'] = x['time']
            json.append(sensor_dict)
        #print(json)
        df_list.append(pd.DataFrame.from_dict(json, orient='columns'))
        #df.to_csv(sensor_name + '.csv')
        print(df_list[i].head())
        df_list[i] = df_list[i].set_index('time')
        df_list[i] = df_list[i].resample('1S').mean()
        print(df_list[i].head())
        i +=1

    query_string = "select * from bc"
    iflux_result = test_client.query(query_string,database)
    iflux_gen = iflux_result.get_points()
    for sensor_name in  bc_sensors:
        json = []
        tag_dict = {"sensor_name": sensor_name}
        iflux_gen = iflux_result.get_points(tags=tag_dict)
        #print(iflux_gen)
        for x in iflux_gen:
            sensor_dict = {}
            x['time'] = get_date_object(x['time'])
            #print(x['time']) time is string and can be manipulated for correct format
            #print(type(x['time']))
            #ts = time.strptime(x['time'], '%Y-%m-%dT%H:%M:%S.%f')
            #print(time.mktime(ts))
            sensor_dict[sensor_name] = x['bc']
            sensor_dict['time'] = x['time']
            json.append(sensor_dict)
        #print(json)
        df_list.append(pd.DataFrame.from_dict(json, orient='columns'))
        #df.to_csv(sensor_name + '.csv')
        print(df_list[i].head())
        df_list[i] = df_list[i].set_index('time')
        df_list[i] = df_list[i].resample('1S').mean()
        print(df_list[i].head())
        i +=1




    #df_collection = pd.DataFrame(index=index, columns=columns)
    for df_i in df_list:
        df_collection = pd.concat([df_collection, df_i], axis=1)

    print(df_collection.head(100))

    return

if __name__ == "__main__":
    main()
