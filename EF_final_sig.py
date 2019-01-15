import serial
import signal
from datetime import timedelta
#from time import time
import time
import threading
from Influx_Dataframe_Client import Influx_Dataframe_Client
import datetime as dt
from datetime import datetime
#from datetime import timedelta
import numpy as np
#import matplotlib.pyplot as plt
#import matplotlib.animation as animation
import os, sys, csv, re, math
import pytz

local_tz = pytz.timezone('Etc/GMT+8') # use your local timezone name here
stop_requested = False

def sig_handler(signum, frame):
    sys.stdout.write("handling signal: %s\n" % signum)
    sys.stdout.flush()

    global stop_requested
    stop_requested = True

def utc_to_local(utc_dt):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt) # .normalize might be unnecessary


class myThread1(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

        # Timestamps for all data
        self.xs_abcd1 = []

    def run(self):
        i = 0
        #while i < 240:

        while not stop_requested:
            time_now=int(time.time()*1000000000)#*1000000000
            print(time_now)
            #e_time = e_time
            json =   {
                'fields': {
                    'count': i                       },
                'time': time_now,
                'tags': {
                    'sensor_name': 'bc_acbd1',
                    },
                'measurement': 'truck_sensor'
                }
            print("Continuing thread 1")
            print(test_client.write_json(json,'timestamp_test'))
            time.sleep(1)
            i+=1
        sys.stdout.write("run exited\n")
        sys.stdout.flush()


signal.signal(signal.SIGTERM, sig_handler)
signal.signal(signal.SIGINT, sig_handler)

conf_file = "local_server.yaml"
test_client = Influx_Dataframe_Client(conf_file,'DB_config')
thread1=myThread1()

thread1.start()
'''
while (True):
    if stop_requested == True:
        exit()
'''
while not stop_requested:
    time.sleep(1)

exit()
