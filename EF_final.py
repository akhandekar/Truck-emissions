import serial
import signal
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

def utc_to_local(utc_dt):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt) # .normalize might be unnecessary

def sig_handler(signum, frame):
    sys.stdout.write("handling signal: %s\n" % signum)
    sys.stdout.flush()

    global stop_requested
    stop_requested = True

class area_time:
    #switch to lists so we don't have to save elements
    def __init__(self,area,start_time,end_time):
        # Create Area_Time object
        self.area = area
        #self.time = time
        self.start_time = start_time
        self.end_time = end_time
        # Potentially may want to add in baseline for subtracting base rectangle

class area_container:
    #switch to lists so we don't have to save elements
    def __init__(self):
        # create all area lists

        # CO2 Area Values
        self.area_time_li820  = []
        self.area_time_li7000  = []
        self.area_time_sba5  = []
        self.area_time_vco2  = []
        # BC Area Values
        self.area_time_abcd1  = []
        self.area_time_ae16 = []
        self.area_time_ae33 = []
        self.area_time_ma300 = []
        # NOx Area Values
        self.area_time_caps  = []
        self.area_time_ucb = []

        self.li820_bc_start = [4,1,5,5]
        self.li7000_bc_start = [5,1.5,6,6]
        self.sba5_bc_start = [1.5,3,3,3]
        self.vco2_bc_start = [3,6,3,3]

        self.li820_bc_end = [5,5,9.5,9.5]
        self.li7000_bc_end = [6,6,10,10]
        self.sba5_bc_end = [2,1.5,4.5,4.5]
        self.vco2_bc_end = [2,2,4,4]

        self.li820_nox_start = [2.5,1]
        self.li7000_nox_start = [3,1.5]
        self.sba5_nox_start = [1,3]
        self.vco2_nox_start = [4.5,6]

        self.li820_nox_end = [2.5,1]
        self.li7000_nox_end = [3,2]
        self.sba5_nox_end = [2.5,4]
        self.vco2_nox_end = [3,5]


        # CO2 Area_Time lengths
        self.li820_len = 0
        self.li7000_len = 0
        self.sba5_len = 0
        self.vco2_len = 0
        # BC Area_Time lengths
        self.abcd1_len = 0
        self.ae16_len = 0
        self.ae33_len = 0
        self.ma300_len = 0
        # NOx Area_Time length
        self.caps_len = 0
        self.ucb_len = 0
        self.delta_window = 10


    # Go through each item in the list and check to see if the timestamps match,
    # if they do push to influx, if the member of the list doesn't match with anything
    # else...then remove it make sure to only check through the current members of the list
    #
    def EF_calc_bc(self,area_time_quot,quot_len,divisor,start_window,end_window):
        print(quot_len)
        for x in range(quot_len):
            for y in range(self.abcd1_len):
                difference = area_time_quot[x].start_time - self.area_time_abcd1[y].start_time
                end_difference = area_time_quot[x].end_time - self.area_time_abcd1[y].end_time
                if (abs(difference) >= start_window[0]):
                    if (abs(end_difference) >= end_window[0]):
                        print("We have a match at EF with abcd and" + divisor)
                            EF = self.area_time_abcd1[y].area / area_time_quot[x].area
                            json =   {
                                'fields': {
                                    'EF': EF
                                    },
                                'time': area_time_quot[x].start_time,
                                'tags': {
                                    'co2_device': divisor,
                                    'bc_device': 'abcd1'
                                    },
                                'measurement': 'emission_factor'
                                }
                            print(test_client.write_json(json,'truck_test_2'))
            for y in range(self.ae16_len):
                difference = area_time_quot[x].start_time - self.area_time_ae16[y].start_time
                end_difference = area_time_quot[x].end_time - self.area_time_ae16[y].end_time
                if (abs(difference) >= start_window[1]):
                    if (abs(end_difference) >= end_window[1]):
                        print("We have a match at EF with ae16 and" + divisor)
                            EF = self.area_time_ae16[y].area / area_time_quot[x].area
                            json =   {
                                'fields': {
                                    'EF': EF
                                    },
                                'time': area_time_quot[x].start_time,
                                'tags': {
                                    'co2_device': divisor,
                                    'bc_device': 'ae16'
                                    },
                                'measurement': 'emission_factor'
                                }
                            print(test_client.write_json(json,'truck_test_2'))
            for y in range(self.ae33_len):
                difference = area_time_quot[x].start_time - self.area_time_ae33[y].start_time
                end_difference = area_time_quot[x].end_time - self.area_time_ae33[y].end_time
                if (abs(difference) >= start_window[2]):
                    if (abs(end_difference) >= end_window[2]):
                        print("We have a match at EF with ae33 and" + divisor)
                            EF = self.area_time_ae33[y].area / area_time_quot[x].area
                            json =   {
                                'fields': {
                                    'EF': EF
                                    },
                                'time': area_time_quot[x].start_time,
                                'tags': {
                                    'co2_device': divisor,
                                    'bc_device': 'ae33'
                                    },
                                'measurement': 'emission_factor'
                                }
                            print(test_client.write_json(json,'truck_test_2'))
            for y in range(self.ma300_len):
                difference = area_time_quot[x].start_time - self.area_time_ma300[y].start_time
                end_difference = area_time_quot[x].end_time - self.area_time_ma300[y].end_time
                if (abs(difference) >= start_window[3]):
                    if (abs(end_difference) >= end_window[3]):
                        print("We have a match at EF with ma300 and" + divisor)
                            EF = self.area_time_ma300[y].area / area_time_quot[x].area
                            json =   {
                                'fields': {
                                    'EF': EF
                                    },
                                'time': area_time_quot[x].start_time,
                                'tags': {
                                    'co2_device': divisor,
                                    'bc_device': 'ma300'
                                    },
                                'measurement': 'emission_factor'
                                }
                            print(test_client.write_json(json,'truck_test_2'))


    def EF_calc_nox(self,area_time_quot,quot_len,divisor,start_window,end_window):
        for x in range(quot_len):
            for y in range(self.caps_len):
                difference = area_time_quot[x].start_time - self.area_time_caps[y].start_time
                end_difference = area_time_quot[x].end_time - self.area_time_caps[y].end_time
                if (abs(difference) >= start_window[0]):
                    if (abs(end_difference) >= end_window[0]):
                        print("We have a match at EF with caps and" + divisor)
                            EF = self.area_time_caps[y].area / area_time_quot[x].area
                            json =   {
                                'fields': {
                                    'EF': EF
                                    },
                                'time': area_time_quot[x].start_time,
                                'tags': {
                                    'co2_device': divisor,
                                    'nox_device': 'caps'
                                    },
                                'measurement': 'emission_factor'
                                }
                            print(test_client.write_json(json,'truck_test_2'))


            for y in range(self.ucb_len):
                difference = area_time_quot[x].start_time - self.area_time_ucb[y].start_time
                end_difference = area_time_quot[x].end_time - self.area_time_ucb[y].end_time
                if (abs(difference) >= start_window[1]):
                    if (abs(end_difference) >= end_window[1]):
                        print("We have a match at EF with ucb and" + divisor)
                            EF = self.area_time_ucb[y].area / area_time_quot[x].area
                            json =   {
                                'fields': {
                                    'EF': EF
                                    },
                                'time': area_time_quot[x].start_time,
                                'tags': {
                                    'co2_device': divisor,
                                    'nox_device': 'ucb'
                                    },
                                'measurement': 'emission_factor'
                                }
                            print(test_client.write_json(json,'truck_test_2'))


    def EF_calc_all(self):
        print("Entered into EF_calc_all")
        # Retrieve lengths for all lists

        # CO2 Area_Time lengths
        self.li820_len = len(self.area_time_li820)
        self.li7000_len = len(self.area_time_li7000)
        self.sba5_len = len(self.area_time_sba5)
        self.vco2_len = len(self.area_time_vco2)
        # BC Area_Time lengths
        self.abcd1_len = len(self.area_time_abcd1)
        self.ae16_len = len(self.area_time_ae16)
        self.ae33_len = len(self.area_time_ae33)
        self.ma300_len = len(self.area_time_ma300)
        # NOx Area_Time length
        self.caps_len = len(self.area_time_caps)
        self.ucb_len = len(self.area_time_ucb)


        self.EF_calc_bc(self.area_time_li820,self.li820_len,'li820',self.li820_bc_start,self.li820_bc_end)
        self.EF_calc_bc(self.area_time_li7000,self.li7000_len,'li7000',self.li7000_bc_start,self.li7000_bc_end)
        self.EF_calc_bc(self.area_time_sba5,self.sba5_len,'sba5',self.sba5_bc_start,self.sba5_bc_end)
        self.EF_calc_bc(self.area_time_vco2,self.vco2_len,'vco2',self.vco2_bc_start,self.vco2_bc_end)

        self.EF_calc_nox(self.area_time_li820,self.li820_len,'li820',self.li820_nox_start,self.li820_nox_end)
        self.EF_calc_nox(self.area_time_li7000,self.li7000_len,'li7000',self.li7000_nox_start,self.li7000_nox_end)
        self.EF_calc_nox(self.area_time_sba5,self.sba5_len,'sba5',self.sba5_nox_start,self.sba5_nox_end)
        self.EF_calc_nox(self.area_time_vco2,self.vco2_len,'vco2',self.vco2_nox_start,self.vco2_nox_end)

        # Removes elements from from beginning to the amount of elements that were
        # in the list before hand
        del self.area_time_li820[0:self.li820_len]
        del self.area_time_li7000[0:self.li7000_len]
        del self.area_time_sba5[0:self.sba5_len]
        del self.area_time_vco2[0:self.vco2_len]

        del self.area_time_abcd1[0:self.abcd1_len]
        del self.area_time_ae16[0:self.ae16_len]
        del self.area_time_ae33[0:self.ae33_len]
        del self.area_time_ma300[0:self.ma300_len]

        del self.area_time_caps[0:self.caps_len]
        del self.area_time_ucb[0:self.ucb_len]


def serialGeneric(device,baudrate):
    ser = serial.Serial (port=device,
    baudrate=baudrate,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
    )
    return ser

if not os.path.isfile("abcd_readings.csv"):
    with open("abcd_readings.csv", "w") as fp:
        fp.write("timestamp,ATN_abcd,BC_abcd,Flowrate_abcd,Area_abcd\n")

if not os.path.isfile("ae16_readings.csv"):
    with open("ae16_readings.csv", "w") as fp:
        fp.write("timestamp,BC_ae16,ATN_ae16,Area_ae16\n")

if not os.path.isfile("ae33_readings.csv"):
    with open("ae33_readings.csv", "w") as fp:
        fp.write("timestamp,BC_ae33,ATN_ae33,Area_ae33\n")

if not os.path.isfile("li820_readings.csv"):
    with open("li820_readings.csv", "w") as fp:
        fp.write("timestamp,CO2_li820,Pressure_li820,Temp_li820,Area_li820\n")

if not os.path.isfile("li7000_readings.csv"):
    with open("li7000_readings.csv", "w") as fp:
        fp.write("timestamp,CO2_li7000,Pressure_li7000,Area_LI7000\n")

if not os.path.isfile("sba5_readings.csv"):
    with open("sba5_readings.csv", "w") as fp:
        fp.write("timestamp,CO2_sba5,Area_sba5\n")

if not os.path.isfile("ma300_readings.csv"):
    with open("ma300_readings.csv", "w") as fp:
        fp.write("timestamp,BC_ma300,Area_ma300\n")

if not os.path.isfile("vco2_readings.csv"):
    with open("vco2_readings.csv", "w") as fp:
        fp.write("timestamp,VCO2,Area_vco2\n")

if not os.path.isfile("caps_readings.csv"):
    with open("caps_readings.csv", "w") as fp:
        fp.write("timestamp,NOX_caps,Area_caps\n")

if not os.path.isfile("ucb_readings.csv"):
    with open("ucb_readings.csv", "w") as fp:
        fp.write("timestamp,NOX_ucb,Area_ucb\n")

if not os.path.isfile("ae51_readings.csv"):
    with open("ae51_readings.csv", "w") as fp:
        fp.write("timestamp,bc_ae51,Area_ae51\n")




serial1=serialGeneric("/dev/ttyUSB_abcd",57600)  ##abcd
serial2=serialGeneric("/dev/ttyUSB_ae16",9600)  ##ae16
serial3=serialGeneric("/dev/ttyUSB_ae33",9600)  ##ae33
serial4=serialGeneric("/dev/ttyUSB_li820",9600)  ##li820
serial5=serialGeneric("/dev/ttyUSB_li7000",9600)  ##li7000
serial6=serialGeneric("/dev/ttyUSB_sba5",19200)  ##sba5
serial7=serialGeneric("/dev/ttyUSB_ma300",1000000)  ##ma300
serial8=serialGeneric("/dev/ttyUSB_vco2",19200)  ##vaisala
serial9=serialGeneric("/dev/ttyUSB_nox_caps",9600)  ##caps

#ucb
serial10= serial.Serial (port='/dev/ttyUSB_nox_ucb',
        baudrate=9600,
        timeout = 1,
        bytesize=serial.SEVENBITS)

##serial11=serialGeneric("/dev/ttyUSB0",9600)  ##ae51


class abcd_thread(threading.Thread):

    def __init__(self, ser,all_area):
        threading.Thread.__init__(self)
        self.ser = ser
        self.N1 = 20

        # Timestamps for all data
        self.xs_abcd1 = []
        # All BC data
        self.ys_abcd1 = []
        # No pollution data
        self.ynp_abcd1 = [0 for i in range(self.N1)]
        # Timestamps for pollution data
        self.xp_abcd1 = []
        # Pollution data (temp, data held in memory to calculate area)
        # P=peak
        # 7% above mean
        self.yp_abcd1 = []
        # Pollution areas
        self.abcd_areas = []
        # Means
        self.ym_abcd1 = []
        # Polluting state
        self.polluting_abcd = [False]
        # Area class variable
        self.area_temp = 0.0

        self.thresh_abcd = 7
        self.logfile1 = "abcd_readings.csv"
        self.peak_start = 0
        self.peak_end = 0

    def run(self):
        i = 0
        #while i < 240:

        while not stop_requested:
            print("Entering thread 1")
            ser1 = self.ser.readline()
            #dt_object = datetime.now()
            dt_object = datetime.now()
            #dt_object = utc_to_local(dt_object)
            values_abcd1 = ser1.split('\n')[0].split(',')
            #print(values_abcd1)
            time_now=int(time.time()*1000000000)
            time_str1 = dt_object.strftime('%H:%M:%S')
            try:
                atn_abcd1 = float(values_abcd1[3])
                bc_abcd1 = float(values_abcd1[4])
                flow_abcd1 = float(values_abcd1[7])
                print(bc_abcd1)

            except (ValueError,IndexError) as e:
                print("abcd index failure")
                continue

            self.peak_abcd(time_str1,bc_abcd1)

            try:
                json =   {
                    'fields': {
                        'bc': bc_abcd1,
                        'atn': atn_abcd1,
                        'flow': flow_abcd1,
                        'area': self.area_temp                        },
                    'time': time_now,
                    'tags': {
                        'sensor_name': 'bc_abcd1',
                        },
                    'measurement': 'bc'
                    }
                new_time = area_time(self.area_temp,self.peak_start,self.peak_start)
                all_area.area_time_abcd1.append(new_time)
                print("The bc_abcd1 is: "+ str(bc_abcd1))
                print(test_client.write_json(json,'truck_test_2'))

            except (ValueError,IndexError) as e:
                print("abcd index failure")
                continue
            i += 1

            with open(self.logfile1, "a") as fp:
                fp.write("%s,%s,%s,%s\n"%(time_str1,atn_abcd1,bc_abcd1,flow_abcd1))


    def peak_abcd(self,time_str1, bc_abcd1):
        run_avg1 = sum(self.ynp_abcd1[-self.N1:])/float(self.N1)
        self.ym_abcd1.append(run_avg1)

        self.xs_abcd1.append(time_str1)
        self.ys_abcd1.append(bc_abcd1)

        if abs(run_avg1 - bc_abcd1) < self.thresh_abcd:
            # No event
            if self.polluting_abcd[-1] == True:
                # Just stopped polluting
                # Caclulate the statistics
                # Record ending timestamp
                # Add this to influx as well
                area_abcd = np.trapz(self.yp_abcd1, dx=1)
                base_line_y = [self.thresh_abcd for s in range(len(self.yp_abcd1))]
                base_area = np.trapz(base_line_y, dx=1)
                area_abcd = area_abcd - base_area
                self.area_temp = area_abcd
                self.abcd_areas.append(area_abcd)
                self.xp_abcd1.append(time_str1)
                with open(self.logfile1, "a") as fp:
                    fp.write("%s,%s,%s\n"%(time_str1,bc_abcd1,area_abcd))

                del self.yp_abcd1[:]
                self.peak_end = int(time.time()*1000000000)
                #print("ABCD Peak finished")
                json_start =   {
                    'fields': {
                        'peak_start_abcd': 1,
                        },
                    'time': self.peak_start,
                    'tags': {
                        'sensor_name': 'bc_abcd1',
                        },
                    'measurement': 'peak'
                    }

                json_end =   {
                    'fields': {
                        'peak_end_abcd': 1,
                        },
                    'time': self.peak_end,
                    'tags': {
                        'sensor_name': 'bc_abcd1',
                        },
                    'measurement': 'peak'
                    }
                print(test_client.write_json(json_start,'truck_test_2'))
                print(test_client.write_json(json_end,'truck_test_2'))

            self.polluting_abcd.append(False)
            self.ynp_abcd1.append(bc_abcd1)
        else:
            # Pollution event
            if self.polluting_abcd[-1] == False:
                #print("ABCD Peak started")
                self.peak_start = int(time.time()*1000000000)
                # Just started polluting
                 # Record starting timestamp
                self.xp_abcd1.append(time_str1)

            self.polluting_abcd.append(True)
            self.yp_abcd1.append(bc_abcd1)

        with open(self.logfile1, "a") as fp:
             fp.write("%s,%s\n"%(time_str1,bc_abcd1))

class ae16_thread(threading.Thread):
    def __init__(self, ser,all_area):
        threading.Thread.__init__(self)
        self.ser = ser
        self.N2 = 10

        #Could pass in an object here for all variables
        # Timestamps for all data
        self.xs_ae16 = []
        # All BC data
        self.ys_ae16 = []
        # No pollution data
        self.ynp_ae16 = [0 for j in range(self.N2)]
        # Timestamps for pollution data
        self.xp_ae16 = []
        # Pollution data (temp, data held in memory to calculate area)
        # P=peak
        # 7% above mean
        self.yp_ae16 = []
        # Pollution areas
        self.ae16_areas = []
        # Means
        self.ym_ae16 = []
        # Polluting state
        self.polluting_ae16 = [False]

        self.thresh_ae16 = 5
        self.logfile2 = "ae16_readings.csv"
        self.peak_start = 0
        self.peak_end = 0

    def run(self):
        j=0
        area_ae16 = 0.0
        while not stop_requested:
            #print("Entering thread2")
            ser2 = self.ser.readline()
            dt_object = datetime.now()
            #dt_object = utc_to_local(dt_object)
            time_str2 = dt_object.strftime('%H:%M:%S')
            values_ae16 = ser2.split('\n')[0].split(',')
            time_now=int(time.time()*1000000000)

            try:
                bc1 = float(values_ae16[2])
                bc_ae16 = bc1/1000
                atn_ae16 = float(values_ae16[9])
                #print("values for ae16 are:")
                #print(values_ae16)
                print(bc_ae16)

            except(ValueError,IndexError) as e:
                print("ae16 index error")
                continue

            run_avg2 = sum(self.ynp_ae16[-self.N2:])/float(self.N2)

            dif2 = abs(run_avg2 - bc_ae16)
            self.ym_ae16.append(run_avg2)

            self.xs_ae16.append(time_str2)
            self.ys_ae16.append(bc_ae16)

            if dif2 < self.thresh_ae16:
                # No event
                if self.polluting_ae16[-1] == True:
                    # Just stopped polluting
                    # Caclulate the statistics
                    # Record ending timestamp
                    area_ae16 = np.trapz(self.yp_ae16, dx=1)
                    self.ae16_areas.append(area_ae16)
                    self.xp_ae16.append(time_str2)
                    with open(self.logfile2, "a") as fp:
                        fp.write("%s,%s,%s,%s\n"%(time_str2,bc_ae16,atn_ae16,area_ae16))

                    del self.yp_ae16[:]
                    print("AE16 Peak end")
                    self.peak_end = int(time.time()*1000000000)
                    json_start =   {
                        'fields': {
                            'peak_start_ae16': 1,
                            },
                        'time': self.peak_start,
                        'tags': {
                            'sensor_name': 'bc_ae16',
                            },
                        'measurement': 'peak'
                        }

                    json_end =   {
                        'fields': {
                            'peak_end_ae16': 1,
                            },
                        'time': self.peak_end,
                        'tags': {
                            'sensor_name': 'bc_ae16',
                            },
                        'measurement': 'peak'
                        }
                    print(test_client.write_json(json_start,'truck_test_2'))
                    print(test_client.write_json(json_end,'truck_test_2'))

                self.polluting_ae16.append(False)
                self.ynp_ae16.append(bc_ae16)
            else:
                # Pollution event
                if self.polluting_ae16[-1] == False:
                    print("AE16 Peak start")
                    self.peak_start = int(time.time()*1000000000)
                    # Just started polluting
                    # Record starting timestamp
                    self.xp_ae16.append(time_str2)

                self.polluting_ae16.append(True)
                self.yp_ae16.append(bc_ae16)

            try:
                json =   {
                    'fields': {
                        'bc': bc_ae16,
                        'atn': atn_ae16,
                        'area': area_ae16
                        },
                    'time': time_now,
                    'tags': {
                        'sensor_name': 'bc_ae16',
                        },
                    'measurement': 'bc'
                    }
                #print("bc_ae16 value is: " +str(bc_ae16))
                print(test_client.write_json(json,'truck_test_2'))
                new_time = area_time(area_ae16,self.peak_start,self.peak_end)
                all_area.area_time_ae16.append(new_time)

            except(ValueError,IndexError) as e:
                print("ae16 index failure")
                continue

            j+= 1

            with open(self.logfile2, "a") as fp:
                fp.write("%s,%s,%s\n"%(time_str2,bc_ae16,atn_ae16))

class ae33_thread(threading.Thread):
    def __init__(self, ser,all_area):
        threading.Thread.__init__(self)
        self.ser = ser
        self.N3 = 10

        # Timestamps for all data
        self.xs_ae33 = []
        # All BC data
        self.ys_ae33 = []
        # No pollution data
        self.ynp_ae33 = [0 for l in range(self.N3)]
        # Timestamps for pollution data
        self.xp_ae33 = []
        # Pollution data (temp, data held in memory to calculate area)
        # P=peak
        # 7% above mean
        self.yp_ae33 = []
        # Pollution areas
        self.ae33_areas = []
        # Means
        self.ym_ae33 = []
        # Polluting state
        self.polluting_ae33 = [False]

        self.thresh_ae33 = 5
        self.logfile3 = "ae33_readings.csv"
        self.peak_start = 0
        self.peak_end = 0

    def run(self):
        l=0
        area_ae33 = 0.0
        while not stop_requested:
            ser3 = self.ser.readline()
            dt_object = datetime.now()
            time_str3 = dt_object.strftime('%H:%M:%S')
            values_ae33 = ser3.split('\n')[0].split(',')
            time_now=int(time.time()*1000000000)
            try:
                bc2 = float(values_ae33[9])
                bc_ae33 = bc2/1000
                print(bc_ae33)

            except(ValueError,IndexError) as e:
                print("ae33 index failure")
                continue


            run_avg3 = sum(self.ynp_ae33[-self.N3:])/float(self.N3)
            dif3 = abs(run_avg3 - bc_ae33)
            self.ym_ae33.append(run_avg3)

            self.xs_ae33.append(time_str3)
            self.ys_ae33.append(bc_ae33)

            if dif3 < self.thresh_ae33:
                # No event
                if self.polluting_ae33[-1] == True:
                    # Just stopped polluting
                    # Caclulate the statistics
                    # Record ending timestamp
                    area_ae33 = np.trapz(self.yp_ae33, dx=1)
                    self.ae33_areas.append(area_ae33)
                    self.xp_ae33.append(time_str3)
                    with open(self.logfile3, "a") as fp:
                        fp.write("%s,%s, %s\n"%(time_str3,bc_ae33,area_ae33))

                    del self.yp_ae33[:]
                    #print("AE33 Peak end")
                    self.peak_end = int(time.time()*1000000000)
                    json_start =   {
                        'fields': {
                            'peak_start_ae33': 1,
                            },
                        'time': self.peak_start,
                        'tags': {
                            'sensor_name': 'bc_ae33',
                            },
                        'measurement': 'peak'
                        }

                    json_end =   {
                        'fields': {
                            'peak_end_ae33': 1,
                            },
                        'time': self.peak_end,
                        'tags': {
                            'sensor_name': 'bc_ae33',
                            },
                        'measurement': 'peak'
                        }
                    print(test_client.write_json(json_start,'truck_test_2'))
                    print(test_client.write_json(json_end,'truck_test_2'))

                self.polluting_ae33.append(False)
                self.ynp_ae33.append(bc_ae33)
            else:
                # Pollution event
                if self.polluting_ae33[-1] == False:
                    #print("AE33 Peak start")
                    self.peak_start = int(time.time()*1000000000)
                    # Just started polluting
                    # Record starting timestamp
                    self.xp_ae33.append(time_str3)
                self.polluting_ae33.append(True)
                self.yp_ae33.append(bc_ae33)

            try:
                json =   {
                    'fields': {
                        'bc': bc_ae33,
                        'area': area_ae33
                        },
                    'time': time_now,
                    'tags': {
                        'sensor_name': 'bc_ae33',
                        },
                    'measurement': 'bc'
                    }
                #print("The value for bc_ae33 is: " + str(bc_ae33))
                print(test_client.write_json(json,'truck_test_2'))
                new_time = area_time(area_ae33,self.peak_start,self.peak_end)
                all_area.area_time_ae33.append(new_time)
            except(ValueError,IndexError) as e:
                print("ae33 index failure")
                continue

            l+= 1

            with open(self.logfile3, "a") as fp:
                fp.write("%s,%s\n"%(time_str3,bc_ae33))

class li820_thread(threading.Thread):
    def __init__(self, ser,all_area):
        threading.Thread.__init__(self)
        self.ser = ser
        self.N4 = 10

        # Timestamps for all data
        self.xs_li820 = []
        # All BC data
        self.ys_li820 = []
        # No pollution data
        self.ynp_li820 = [450 for m in range(self.N4)]
        # Timestamps for pollution data
        self.xp_li820 = []
        # Pollution data (temp, data held in memory to calculate area)
        # P=peak
        # 7% above mean
        self.yp_li820 = []
        # Pollution areas
        self.li820_areas = []
        # Means
        self.ym_li820 = []
        # Polluting state
        self.polluting_li820 = [False]
        self.thresh_li820 = 700
        self.logfile4 = "li820_readings.csv"

        self.temp_area_li820 = 0.0
        self.peak_start = 0
        self.peak_end = 0


    def run(self):
        m = 0
        area_li820 = 0.0
        while not stop_requested:
            ser4 = self.ser.readline()
            dt_object = datetime.now()
            time_str4 = dt_object.strftime('%H:%M:%S')
            time_now=int(time.time()*1000000000)
            try:
                values_li820 = re.split(r'[<>]', ser4)
                #print("The values for li820:")
                #print(values_li820)
                co2_li820 = float(values_li820[14])
                temp_li820 = float(values_li820[6])
                press_li820 = float(values_li820[10])

            except(ValueError,IndexError) as e:
                print("li820 index failure")
                continue

            self.ys_li820.append(co2_li820)
            run_avg4 = sum(self.ynp_li820[-self.N4:])/float(self.N4)
            dif4 = abs(run_avg4 - co2_li820)

            self.ym_li820.append(run_avg4)

            self.xs_li820.append(time_str4)
            self.ys_li820.append(co2_li820)
            self.thresh_li820 = 1.07* run_avg4



            if dif4 < self.thresh_li820:
                # No event
                if self.polluting_li820[-1] == True:
                    # Just stopped polluting
                    # Caclulate the statistics
                    # Record ending timestamp
                    area_li820 = np.trapz(self.yp_li820, dx=1)
                    #self.temp_area_li820 = area_li820
                    self.li820_areas.append(area_li820)
                    self.xp_li820.append(time_str4)
                    with open(self.logfile4, "a") as fp:
                        fp.write("%s,%s, %s\n"%(time_str4,co2_li820,area_li820))

                    del self.yp_li820[:]
                    print("LI820 Peak end")
                    self.peak_end = int(time.time()*1000000000)
                    json_start =   {
                        'fields': {
                            'peak_start_li820': 1,
                            },
                        'time': self.peak_start,
                        'tags': {
                            'sensor_name': 'co2_li820',
                            },
                        'measurement': 'peak'
                        }

                    json_end =   {
                        'fields': {
                            'peak_end_li820': 1,
                            },
                        'time': self.peak_end,
                        'tags': {
                            'sensor_name': 'co2_li820',
                            },
                        'measurement': 'peak'
                        }
                    print(test_client.write_json(json_start,'truck_test_2'))
                    print(test_client.write_json(json_end,'truck_test_2'))

                self.polluting_li820.append(False)
                self.ynp_li820.append(co2_li820)
            else:
                # Pollution event

                if self.polluting_li820[-1] == False:
                    #print("LI820 Peak start")
                    self.peak_start = int(time.time()*1000000000)
                    # Just started polluting
                    # Record starting timestamp
                    self.xp_li820.append(time_str4)

                self.polluting_li820.append(True)
                self.yp_li820.append(co2_li820)

            m+= 1
            try:
                json =   {
                    'fields': {
                        'co2': co2_li820,
                        'area': area_li820,
                        'temp': temp_li820,
                        'pressure': press_li820
                        },
                    'time': time_now,
                    'tags': {
                        'sensor_name': 'co2_li820',
                        },
                    'measurement': 'co2'
                    }
                #print("The co2_li820 value is: " + str(co2_li820))
                print(test_client.write_json(json,'truck_test_2'))
                new_time = area_time(area_li820,self.peak_start,self.peak_end)
                all_area.area_time_ae33.append(new_time)

            except(ValueError,IndexError) as e:
                print("li820 index failure")
                continue

            with open(self.logfile4, "a") as fp:
                fp.write("%s,%s\n"%(time_str4,co2_li820))

class li7000_thread(threading.Thread):
    def __init__(self, ser,all_area):
        threading.Thread.__init__(self)
        self.ser = ser
        self.N5 = 10

        # Timestamps for all data
        self.xs_li7000 = []
        # All BC data
        self.ys_li7000 = []
        # No pollution data
        self.ynp_li7000 = [450 for n in range(self.N5)]
        # Timestamps for pollution data
        self.xp_li7000 = []
        # Pollution data (temp, data held in memory to calculate area)
        # P=peak
        # 7% above mean
        self.yp_li7000 = []
        # Pollution areas
        self.li7000_areas = []
        # Means
        self.ym_li7000 = []
        # Polluting state
        self.polluting_li7000 = [False]

        self.thresh_li7000 = 700

        self.logfile5 = "li7000_readings.csv"
        self.peak_start = 0
        self.peak_end = 0

    def run(self):
        n=0
        area_li7000 = 0.0
        while not stop_requested:
            ser5 = self.ser.readline()
            dt_object = datetime.now()
            time_str5 = dt_object.strftime('%H:%M:%S')
            time_now=int(time.time()*1000000000)
            try:
                values_li7000 = ser5.split('\n')[0].split('\t')
                #print("The values for li700 are:")
                #print(values_li7000)
                co2_li7000 = float(values_li7000[2])
                press_li7000 = float(values_li7000[4])
                temp_li7000 = float(values_li7000[5])


            except (ValueError,IndexError) as e:
                print("li7000 index failure")
                continue


            self.ys_li7000.append(co2_li7000)
            run_avg5 = sum(self.ynp_li7000[-self.N5:])/float(self.N5)
            dif5 = abs(run_avg5 - co2_li7000)
            self.ym_li7000.append(run_avg5)

            self.xs_li7000.append(time_str5)
            self.ys_li7000.append(co2_li7000)
            self.thresh_li7000 = 1.07* run_avg5


            if dif5 < self.thresh_li7000:
                # No event
                if self.polluting_li7000[-1] == True:
                    # Just stopped polluting
                    # Caclulate the statistics
                    # Record ending timestamp
                    area_li7000 = np.trapz(self.yp_li7000, dx=0.2)
                    self.li7000_areas.append(area_li7000)
                    self.xp_li7000.append(time_str5)
                    with open(self.logfile5, "a") as fp:
                        fp.write("%s,%s, %s\n"%(time_str5,co2_li7000,area_li7000))
                    del self.yp_li7000[:]
                    print("LI7000 Peak end")

                    self.peak_end = int(time.time()*1000000000)
                    json_start =   {
                        'fields': {
                            'peak_start_li7000': 1,
                            },
                        'time': self.peak_start,
                        'tags': {
                            'sensor_name': 'co2_li7000',
                            },
                        'measurement': 'peak'
                        }

                    json_end =   {
                        'fields': {
                            'peak_end_li7000': 1,
                            },
                        'time': self.peak_end,
                        'tags': {
                            'sensor_name': 'co2_li7000',
                            },
                        'measurement': 'peak'
                        }
                    print(test_client.write_json(json_start,'truck_test_2'))
                    print(test_client.write_json(json_end,'truck_test_2'))

                self.polluting_li7000.append(False)
                self.ynp_li7000.append(co2_li7000)
            else:
                # Pollution event

                if self.polluting_li7000[-1] == False:
                    print("LI7000 Peak start")
                    self.peak_start = int(time.time()*1000000000)
                    # Just started polluting
                    # Record starting timestamp
                    self.xp_li7000.append(time_str5)

                self.polluting_li7000.append(True)
                self.yp_li7000.append(co2_li7000)
            try:
                json =   {
                    'fields': {
                        'co2': co2_li7000,
                        'area': area_li7000,
                        'temp': temp_li7000,
                        'pressure': press_li7000
                        },
                    'time': time_now,
                    'tags': {
                        'sensor_name': 'co2_li7000',
                        },
                    'measurement': 'co2'
                    }
                #print("The co2_li7000 value is: "+ str(co2_li7000))
                print(test_client.write_json(json,'truck_test_2'))
                new_time = area_time(area_li7000,time_str5)
                all_area.area_time_ae33.append(new_time)

            except(ValueError,IndexError) as e:
                print("li7000 index failure")
                continue

            n+= 1

            with open(self.logfile5, "a") as fp:
                fp.write("%s,%s\n"%(time_str5,co2_li7000))

class sba5_thread(threading.Thread):
    def __init__(self, ser,all_area):
        threading.Thread.__init__(self)
        self.ser = ser
        self.N6 = 10

        # Timestamps for all data
        self.xs_sba5 = []
        # All BC data
        self.ys_sba5 = []
        # No pollution data
        self.ynp_sba5 = [450 for o in range(self.N6)]
        # Timestamps for pollution data
        self.xp_sba5 = []
        # Pollution data (temp, data held in memory to calculate area)
        # P=peak
        # 7% above mean
        self.yp_sba5 = []
        # Pollution areas
        self.sba5_areas = []
        # Means
        self.ym_sba5 = []
        # Polluting state
        self.polluting_sba5 = [False]

        self.thresh_sba5 = 700

        self.logfile6 = "sba5_readings.csv"
        self.peak_start = 0
        self.peak_end = 0

    def run(self):
        o=0
        area_sba5 = 0.0
        while not stop_requested:
            ser6 = self.ser.readline()
            dt_object = datetime.now()
            time_str6 = dt_object.strftime('%H:%M:%S')
            values_sba5 = ser6.split('\n')[0].split(' ')
            time_now=int(time.time()*1000000000)

            try:
                co2_sba5 = float(values_sba5[3])

            except (ValueError, IndexError) as e:
                print("sba5 index failure")
                continue


            self.ys_sba5.append(co2_sba5)

            run_avg6 = sum(self.ynp_sba5[-self.N6:])/float(self.N6)
            dif6 = abs(run_avg6 - co2_sba5)

            self.ym_sba5.append(run_avg6)

            self.xs_sba5.append(time_str6)
            self.ys_sba5.append(co2_sba5)
            self.thresh_sba5 = 1.07* run_avg6


            if dif6 < self.thresh_sba5:
                # No event
                if self.polluting_sba5[-1] == True:
                    # Just stopped polluting
                    # Caclulate the statistics
                    # Record ending timestamp
                    area_sba5 = np.trapz(self.yp_sba5, dx=1)
                    self.sba5_areas.append(area_sba5)
                    self.xp_sba5.append(time_str6)
                    with open(self.logfile6, "a") as fp:
                        fp.write("%s,%s, %s\n"%(time_str6,co2_sba5,area_sba5))

                    del self.yp_sba5[:]
                    print("SBA5 Peak end")
                    self.peak_end = int(time.time()*1000000000)
                    json_start =   {
                        'fields': {
                            'peak_start_sba5': 1,
                            },
                        'time': self.peak_start,
                        'tags': {
                            'sensor_name': 'co2_sba5',
                            },
                        'measurement': 'peak'
                        }

                    json_end =   {
                        'fields': {
                            'peak_end_sba5': 1,
                            },
                        'time': self.peak_end,
                        'tags': {
                            'sensor_name': 'co2_sba5',
                            },
                        'measurement': 'peak'
                        }
                    print(test_client.write_json(json_start,'truck_test_2'))
                    print(test_client.write_json(json_end,'truck_test_2'))

                self.polluting_sba5.append(False)
                self.ynp_sba5.append(co2_sba5)
            else:
                # Pollution event
                if self.polluting_sba5[-1] == False:
                    print("SBA5 Peak start")
                    self.peak_start = int(time.time()*1000000000)
                    # Just started polluting
                    # Record starting timestamp
                    self.xp_sba5.append(time_str6)

                self.polluting_sba5.append(True)
                self.yp_sba5.append(co2_sba5)
            try:
                json =   {
                    'fields': {
                        'co2': co2_sba5,
                        'area': area_sba5
                        },
                    'time': time_now,
                    'tags': {
                        'sensor_name': 'co2_sba5',
                        },
                    'measurement': 'co2'
                    }
                #print("The co2_sba2 value is: " +str(co2_sba5))
                print(test_client.write_json(json,'truck_test_2'))
                new_time = area_time(area_sba5,self.peak_start,self.peak_end)
                all_area.area_time_ae33.append(new_time)

            except(ValueError,IndexError) as e:
                print("sba5 index failure")
                continue

            o+= 1

            with open(self.logfile6, "a") as fp:
                fp.write("%s,%s\n"%(time_str6,co2_sba5))

class ma300_thread(threading.Thread):
    def __init__(self, ser,all_area):
        threading.Thread.__init__(self)
        self.ser = ser
        self.N7 = 10

        # Timestamps for all data
        self.xs_ma300 = []
        # All BC data
        self.ys_ma300 = []
        # No pollution data
        self.ynp_ma300 = [0 for p in range(self.N7)]
        # Timestamps for pollution data
        self.xp_ma300 = []
        # Pollution data (temp, data held in memory to calculate area)
        # P=peak
        # 7% above mean
        self.yp_ma300 = []
        # Pollution areas
        self.ma300_areas = []
        # Means
        self.ym_ma300 = []
        # Polluting state
        self.polluting_ma300 = [False]

        self.thresh_ma300 = 5000
        self.logfile7 = "ma300_readings.csv"
        self.peak_start = 0
        self.peak_end = 0

    def run(self):
        p=0
        area_ma300 = 0.0
        while not stop_requested:
            ser7 = self.ser.readline()
            dt_object = datetime.now()
            time_str7 = dt_object.strftime('%H:%M:%S')
            values_ma300 = ser7.split('\n')[0].split(',')
            time_now=int(time.time()*1000000000)

            try:
                bc3 = float(values_ma300[44])
                bc_ma300 = bc3/1000

            except (ValueError, IndexError) as e:
                print("ma300 index failure")
                continue


            self.ys_ma300.append(bc_ma300)
            run_avg7 = sum(self.ynp_ma300[-self.N7:])/float(self.N7)
            dif7 = abs(run_avg7 - bc_ma300)

            self.ym_ma300.append(run_avg7)

            self.xs_ma300.append(time_str7)
            self.ys_ma300.append(bc_ma300)


            if dif7 < self.thresh_ma300:
                # No event
                if self.polluting_ma300[-1] == True:
                    # Just stopped polluting
                    # Caclulate the statistics
                    # Record ending timestamp
                    area_ma300 = np.trapz(self.yp_ma300, dx=1)
                    self.ma300_areas.append(area_ma300)
                    self.xp_ma300.append(time_str7)
                    with open(self.logfile7, "a") as fp:
                        fp.write("%s,%s, %s\n"%(time_str7,bc_ma300,area_ma300))

                    del self.yp_ma300[:]
                    print("MA300 Peak end")
                    self.peak_end = int(time.time()*1000000000)
                    json_start =   {
                        'fields': {
                            'peak_start_ma300': 1,
                            },
                        'time': self.peak_start,
                        'tags': {
                            'sensor_name': 'bc_ma300',
                            },
                        'measurement': 'peak'
                        }

                    json_end =   {
                        'fields': {
                            'peak_end_ma300': 1,
                            },
                        'time': self.peak_end,
                        'tags': {
                            'sensor_name': 'bc_ma300',
                            },
                        'measurement': 'peak'
                        }
                    print(test_client.write_json(json_start,'truck_test_2'))
                    print(test_client.write_json(json_end,'truck_test_2'))

                self.polluting_ma300.append(False)
                self.ynp_ma300.append(bc_ma300)

            else:
                # Pollution event

                if self.polluting_ma300[-1] == False:
                    print("MA300 Peak start")
                    # Just started polluting
                    # Record starting timestamp
                    self.xp_ma300.append(time_str7)

                self.polluting_ma300.append(True)
                self.yp_ma300.append(bc_ma300)
            try:
                json =   {
                    'fields': {
                        'bc': bc_ma300,
                        'area': area_ma300
                        },
                    'time': time_now,
                    'tags': {
                        'sensor_name': 'bc_ma300',
                        },
                    'measurement': 'bc'
                    }
                #print("The bc_ma300 value is: " + str(bc_ma300))
                print(test_client.write_json(json,'truck_test_2'))
                new_time = area_time(area_ma300,self.peak_start,self.peak_end)
                all_area.area_time_ae33.append(new_time)

            except(ValueError,IndexError) as e:
                print("ma300 index failure")
                continue

            p+= 1

            with open(self.logfile7, "a") as fp:
                fp.write("%s,%s\n"%(time_str7,bc_ma300))

class vco2_thread(threading.Thread):
    def __init__(self, ser,all_area):
        threading.Thread.__init__(self)
        self.ser = ser
        self.N8 = 10

        # Timestamps for all data
        self.xs_vco2 = []
        # All BC data
        self.ys_vco2 = []
        # No pollution data
        self.ynp_vco2 = [450 for q in range(self.N8)]
        # Timestamps for pollution data
        self.xp_vco2 = []
        # Pollution data (temp, data held in memory to calculate area)
        # P=peak
        # 7% above mean
        self.yp_vco2 = []
        # Pollution areas
        self.vco2_areas = []
        # Means
        self.ym_vco2 = []
        # Polluting state
        self.polluting_vco2 = [False]

        self.thresh_vco2 = 700

        self.logfile8 = "vco2_readings.csv"
        self.peak_start = 0
        self.peak_end = 0

    def run(self):
        q=0
        area_vco2 = 0.0
        self.ser.write("R\r\n")
        response=self.ser.readline()

        while not stop_requested:
            ser8 = self.ser.readline()
            dt_object = datetime.now()
            time_str8 = dt_object.strftime('%H:%M:%S')
            values_vco2 = ser8.split('\n')[0].split('\t')
            time_now=int(time.time()*1000000000)

            try:
                vco2 = float(values_vco2[0])

            except (ValueError, IndexError) as e:
                print("vco2 index failure")
                continue


            self.ys_vco2.append(vco2)

            run_avg8 = sum(self.ynp_vco2[-self.N8:])/float(self.N8)
            dif8 = abs(run_avg8 - vco2)
            self.thresh_vco2 = 1.07* run_avg8
            self.ym_vco2.append(run_avg8)

            self.xs_vco2.append(time_str8)
            self.ys_vco2.append(vco2)


            if dif8 < self.thresh_vco2:
                # No event
                if self.polluting_vco2[-1] == True:
                    # Just stopped polluting
                    # Caclulate the statistics
                    # Record ending timestamp
                    area_vco2 = np.trapz(self.yp_vco2, dx=1)
                    self.vco2_areas.append(area_vco2)
                    self.xp_vco2.append(time_str8)
                    with open(self.logfile8, "a") as fp:
                        fp.write("%s,%s, %s\n"%(time_str8,vco2,area_vco2))

                    del self.yp_vco2[:]
                    print("VCO2 Peak end")
                    self.peak_end = int(time.time()*1000000000)
                    json_start =   {
                        'fields': {
                            'peak_start_vco2': 1,
                            },
                        'time': self.peak_start,
                        'tags': {
                            'sensor_name': 'vco2',
                            },
                        'measurement': 'peak'
                        }

                    json_end =   {
                        'fields': {
                            'peak_end_vco2': 1,
                            },
                        'time': self.peak_end,
                        'tags': {
                            'sensor_name': 'vco2',
                            },
                        'measurement': 'peak'
                        }
                    print(test_client.write_json(json_start,'truck_test_2'))
                    print(test_client.write_json(json_end,'truck_test_2'))

                self.polluting_vco2.append(False)
                self.ynp_vco2.append(vco2)

            else:
                # Pollution event

                if self.polluting_vco2[-1] == False:
                    print("VCO2 Peak start")
                    self.peak_start = int(time.time()*1000000000)
                    # Just started polluting
                    # Record starting timestamp
                    self.xp_vco2.append(time_str8)

                self.polluting_vco2.append(True)
                self.yp_vco2.append(vco2)
            try:
                json =   {
                    'fields': {
                        'co2': vco2,
                        'area': area_vco2
                        },
                    'time': time_now,
                    'tags': {
                        'sensor_name': 'vco2',
                        },
                    'measurement': 'co2'
                    }
                #print("The vco2 value is: " + str(vco2))
                print(test_client.write_json(json,'truck_test_2'))
                new_time = area_time(area_vco2,self.peak_start,self.peak_end)
                all_area.area_time_ae33.append(new_time)

            except(ValueError,IndexError) as e:
                print("vco2 index failure")
                continue

            q+= 1

            with open(self.logfile8, "a") as fp:
                fp.write("%s,%s\n"%(time_str8,vco2))

class caps_thread(threading.Thread):
    def __init__(self, ser,all_area):
        threading.Thread.__init__(self)
        self.ser = ser
        self.N9 = 10

        # Timestamps for all data
        self.xs_caps = []
        # All BC data
        self.ys_caps = []
        # No pollution data
        self.ynp_caps = [0 for r in range(self.N9)]
        # Timestamps for pollution data
        self.xp_caps = []
        # Pollution data (temp, data held in memory to calculate area)
        # P=peak
        # 7% above mean
        self.yp_caps = []
        # Pollution areas
        self.caps_areas = []
        # Means
        self.ym_caps = []
        # Polluting state
        self.polluting_caps = [False]

        self.thresh_caps = .1

        self.logfile9 = "caps_readings.csv"
        self.peak_start = 0
        self.peak_end = 0

    def run(self):
        r=0
        area_caps = 0.0
        while not stop_requested:
            ser9 = self.ser.readline()
            dt_object = datetime.now()
            time_str9 = dt_object.strftime('%H:%M:%S')
            values_caps = ser9.split('\n')[0].split(',')
            time_now=int(time.time()*1000000000)

            try:
                nox1 = float(values_caps[1])
                nox_caps = nox1/1000

            except (ValueError, IndexError) as e:
                print("caps index failure")
                continue


            self.ys_caps.append(nox_caps)

            run_avg9 = sum(self.ynp_caps[-self.N9:])/float(self.N9)
            dif9 = abs(run_avg9 - nox_caps)
            self.ym_caps.append(run_avg9)

            self.xs_caps.append(time_str9)
            self.ys_caps.append(nox_caps)
            if dif9 < self.thresh_caps:
                # No event
                if self.polluting_caps[-1] == True:
                    # Just stopped polluting
                    # Caclulate the statistics
                    # Record ending timestamp
                    area_caps = np.trapz(self.yp_caps, dx=1)
                    self.caps_areas.append(area_caps)
                    self.xp_caps.append(time_str9)
                    with open(self.logfile9, "a") as fp:
                        fp.write("%s,%s, %s\n"%(time_str9,nox_caps,area_caps))

                    del self.yp_caps[:]
                    print("CAPS Peak end")
                    self.peak_end = int(time.time()*1000000000)
                    json_start =   {
                        'fields': {
                            'peak_start_caps': 1,
                            },
                        'time': self.peak_start,
                        'tags': {
                            'sensor_name': 'nox_caps',
                            },
                        'measurement': 'peak'
                        }

                    json_end =   {
                        'fields': {
                            'peak_end_caps': 1,
                            },
                        'time': self.peak_end,
                        'tags': {
                            'sensor_name': 'nox_caps',
                            },
                        'measurement': 'peak'
                        }
                    print(test_client.write_json(json_start,'truck_test_2'))
                    print(test_client.write_json(json_end,'truck_test_2'))
                self.polluting_caps.append(False)
                self.ynp_caps.append(nox_caps)
            else:
                # Pollution event

                if self.polluting_caps[-1] == False:
                    print("CAPS Peak start")
                    self.peak_start = int(time.time()*1000000000)
                    # Just started polluting
                    # Record starting timestamp
                    self.xp_caps.append(time_str9)

                self.polluting_caps.append(True)
                self.yp_caps.append(nox_caps)
            try:
                json =   {
                    'fields': {
                        'nox': nox_caps,
                        'area': area_caps
                        },
                    'time': time_now,
                    'tags': {
                        'sensor_name': 'nox_caps',
                        },
                    'measurement': 'nox'
                    }
                #print("The nox_caps value is: " + str(nox_caps))
                new_time = area_time(area_caps,self.peak_start,self.peak_end)
                all_area.area_time_ae33.append(new_time)
                print(test_client.write_json(json,'truck_test_2'))

            except(ValueError,IndexError) as e:
                print("caps index failure")
                continue

            r+= 1

            with open(self.logfile9, "a") as fp:
                fp.write("%s,%s\n"%(time_str9,nox_caps))

class ucb_thread(threading.Thread):
    def __init__(self, ser,all_area):
        threading.Thread.__init__(self)
        self.ser = ser
        self.N10 = 10

        # Timestamps for all data
        self.xs_ucb = []
        # All BC data
        self.ys_ucb = []
        # No pollution data
        self.ynp_ucb = [0 for s in range(self.N10)]
        # Timestamps for pollution data
        self.xp_ucb = []
        # Pollution data (temp, data held in memory to calculate area)
        # P=peak
        # 7% above mean
        self.yp_ucb = []
        # Pollution areas
        self.ucb_areas = []
        # Means
        self.ym_ucb = []
        # Polluting state
        self.polluting_ucb = [False]

        self.thresh_ucb = 0.1

        self.logfile10 = "ucb_readings.csv"
        self.peak_start = 0
        self.peak_end = 0

    def run(self):
        s=0
        area_ucb = 0.0
        nox_ucb = 0.0
        while not stop_requested:

            serial10.write(b'\x0201RD0\x03\x26')
            ser10 = serial10.readline()
            dt_object = datetime.now()
            time_str10 = dt_object.strftime('%H:%M:%S')
            time_now=int(time.time()*1000000000)

            try:
                output_ucb = ser10.decode('ascii')
                values_ucb = output_ucb.split('\n')[0].split(',')
                print("values_ucb:")
                print(values_ucb)
                if float(values_ucb[1])!=0:
                    nox_ucb = float(values_ucb[1])


            except Exception as e:
                print("ucb index failure")
                print (e)
                continue


            self.ys_ucb.append(nox_ucb)
            run_avg10 = sum(self.ynp_ucb[-self.N10:])/float(self.N10)
            dif10 = abs(run_avg10 - nox_ucb)
            self.ym_ucb.append(run_avg10)
            self.xs_ucb.append(time_str10)
            self.ys_ucb.append(nox_ucb)
            if dif10 < self.thresh_ucb:
                # No event
                if self.polluting_ucb[-1] == True:
                    # Just stopped polluting
                    # Caclulate the statistics
                    # Record ending timestamp
                    area_ucb = np.trapz(self.yp_ucb, dx=1)
                    base_line_y = [self.thresh_ucb for s in range(len(self.yp_ucb))]
                    base_area = np.trapz(base_line_y, dx=1)
                    area_ucb = area_ucb - base_area
                    self.ucb_areas.append(area_ucb)
                    self.xp_ucb.append(time_str10)
                    with open(self.logfile10, "a") as fp:
                        fp.write("%s,%s, %s\n"%(time_str10,nox_ucb,area_ucb))

                    del self.yp_ucb[:]
                    print("UCB Peak end")
                    self.peak_end = int(time.time()*1000000000)
                    json_start =   {
                        'fields': {
                            'peak_start_ucb': 1,
                            },
                        'time': self.peak_start,
                        'tags': {
                            'sensor_name': 'nox_ucb',
                            },
                        'measurement': 'peak'
                        }

                    json_end =   {
                        'fields': {
                            'peak_end_ucb': 1,
                            },
                        'time': self.peak_end,
                        'tags': {
                            'sensor_name': 'nox_ucb',
                            },
                        'measurement': 'peak'
                        }
                    print(test_client.write_json(json_start,'truck_test_2'))
                    print(test_client.write_json(json_end,'truck_test_2'))

                self.polluting_ucb.append(False)
                self.ynp_ucb.append(nox_ucb)

            else:
                # Pollution event

                if self.polluting_ucb[-1] == False:
                    print("UCB Peak start")
                    self.peak_start = int(time.time()*1000000000)
                    # Just started polluting
                    # Record starting timestamp
                    self.xp_ucb.append(time_str10)

                self.polluting_ucb.append(True)
                self.yp_ucb.append(nox_ucb)
            try:
                json =   {
                    'fields': {
                        'nox': nox_ucb,
                        'area': area_ucb
                        },
                    'time': time_now,
                    'tags': {
                        'sensor_name': 'nox_ucb',
                        },
                    'measurement': 'nox'
                    }
                #print("The nox_ucb value is: " + str(nox_ucb))
                print(test_client.write_json(json,'truck_test_2'))
                new_time = area_time(area_ucb,self.peak_start,self.peak_end)
                all_area.area_time_ae33.append(new_time)

            except(ValueError,IndexError) as e:
                print("ucb index failure push")
                continue

            s+= 1

            with open(self.logfile10, "a") as fp:
                fp.write("%s,%s\n"%(time_str10,nox_ucb))

class areaThread(threading.Thread):
    def __init__(self,all_area):
        threading.Thread.__init__(self)
        print("Started influx thread")

    def run(self):
        i = 0
        while not stop_requested:
            time.sleep(5)
            all_area.EF_calc_all()
            i+=1

signal.signal(signal.SIGTERM, sig_handler)
signal.signal(signal.SIGINT, sig_handler)



all_area=area_container()
conf_file = "local_server.yaml"
test_client = Influx_Dataframe_Client(conf_file,'DB_config')
thread1=abcd_thread(serial1,all_area)
thread2=ae16_thread(serial2,all_area)
thread3=ae33_thread(serial3,all_area)
thread4=li820_thread(serial4,all_area)
thread5=li7000(serial5,all_area)
thread6=sba5_thread(serial6,all_area)
thread7=ma300_thread(serial7,all_area)
thread8=vco2_thread(serial8,all_area)
thread9=caps_thread(serial9,all_area)
thread10=ucb_thread(serial10,all_area)
#thread11=myThread11(serial11,all_area)
area_thread=areaThread(all_area)
thread1.start()
thread2.start()
thread3.start()
thread4.start()
thread5.start()
thread6.start()
thread7.start()
thread8.start()
thread9.start()
thread10.start()
#thread11.start()
area_thread.start()
while not stop_requested:
    time.sleep(1)

exit()
