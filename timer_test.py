import datetime, threading, time
import serial
import signal
import time
import threading
from Influx_Dataframe_Client import Influx_Dataframe_Client
import datetime as dt
from datetime import datetime
import numpy as np
import os, sys, csv, re, math
import argparse
import peakutils

def foo():
    next_call = time.time()
    while True:
        print datetime.datetime.now()
        next_call = next_call+1;
        time.sleep(next_call - time.time())

timerThread = threading.Thread(target=foo)
timerThread.start()
