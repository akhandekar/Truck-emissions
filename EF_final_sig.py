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

stop_requested = False # Condition flag for keyboard interrupt

def serialGeneric(device,baudrate):
    ser = serial.Serial (port=device,
    baudrate=baudrate,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
    )
    return ser

def sig_handler(signum, frame):
    sys.stdout.write("handling signal: %s\n" % signum)
    sys.stdout.flush()

    global stop_requested
    stop_requested = True

# Container for peak information

class area_time:
    #switch to lists so we don't have to save elements
    def __init__(self,area,start_time,end_time):
        # Create Area_Time object
        self.area = area
        #self.time = time
        self.start_time = start_time
        self.end_time = end_time
        # Potentially may want to add in baseline for subtracting base rectangle

# Storage of peaks for each instrument as well function for calculating EF

class area_container:
    #switch to lists so we don't have to save elements
    def __init__(self,influx_client):
        # create all area lists
        self.influx_client = influx_client
        # CO2 Area Values
        self.co2_peaks[0]  = [] #li820 sensor
        self.co2_peaks[1]  = [] #li7000 sensor
        self.co2_peaks[2]  = [] #sba5 sensor
        self.co2_peaks[3]  = [] #vco2 sensor
        # BC Area Values
        self.bc_peaks[0]  = [] #abcd sensor
        self.bc_peaks[1]  = [] #ae16 sensor
        self.bc_peaks[2]  = [] #ae33 sensor
        self.bc_peaks[3]  = [] #ma300 sensor
        # Nox areav values
        self.nox_peaks[0] = []
        self.nox_peaks[1] = []

        # Windows for matching peaks between instruments
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
    def bc_peak_match(self,single_co2_peaks,bc_peaks,bc_device,co2_device,dev_id,start_window,end_window):
            print("The co2 timestamp start is " + co2_device + "is" + str(self.co2_peaks[dev_id].start_time))
            for y in range(len(single_bc_peaks)):
                difference = single_co2_peak.start_time - bc_peaks[y].start_time
                end_difference = single_co2_peak.end_time - bc_peaks[y].end_time
                json =   {
                    'fields': {
                        'start_difference': float(difference/1000000000),
                        'end_difference': float(end_difference/1000000000),
                        },
                    'time': single_co2_peak.start_time,
                    'tags': {
                        'co2_device': co2_device,
                        'bc_device': bc_device
                        },
                    'measurement': 'emission_factor'
                    }
                self.influx_client.write_json(json)
                if (abs(difference) >= start_window[dev_id]*1000000000):
                    if (abs(end_difference) >= end_window[dev_id]*1000000000):
                        print("We have a match at EF with abcd and" + divisor)
                        EF = bc_peaks[y].area / single_co2_peak.area
                        json =   {
                            'fields': {
                                'EF': EF
                                },
                            'time': single_co2_peak[x].start_time,
                            'tags': {
                                'co2_device': co2_device,
                                'bc_device': bc_device
                                },
                            'measurement': 'emission_factor'
                            }
                        self.influx_client.write_json(json)

    def nox_peak_match(self,single_co2_peaks,nox_peaks,nox_device,co2_device,dev_id,start_window,end_window):
        for y in range(self.caps_len):
            difference = single_co2_peak.start_time - nox_peaks[y].start_time
            end_difference = single_co2_peak.end_time - nox_peaks[y].end_time
            json =   {
                'fields': {
                    'start_difference': float(difference/1000000000),
                    'end_difference': float(end_difference/1000000000)
                    },
                'time': single_co2_peak.start_time,
                'tags': {
                    'co2_device': co2_device,
                    'nox_device': nox_device
                    },
                'measurement': 'emission_factor'
                }
            self.influx_client.write_json(json)
            if (abs(difference) >= start_window[dev_id]*1000000000):
                if (abs(end_difference) >= end_window[dev_id]*1000000000):
                    print("We have a match at EF with caps and" + divisor)
                    EF = nox_peaks[y].area / single_co2_peak.area
                    json =   {
                        'fields': {
                            'EF': EF
                            },
                        'time': single_co2_peak.start_time,
                        'tags': {
                            'co2_device': co2_device,
                            'nox_device': nox_device
                            },
                        'measurement': 'emission_factor'
                        }
                    self.influx_client.write_json(json)

    def EF_calc_bc(self,co2_peaks,dev_id,co2_device,start_window,end_window):
        print("The amount of co2 peaks for " + divisor + "is" + str(quot_len))
        peak_amt = len(self.co2_peaks)
        for x in range(peak_amt):
            bc_peak_match(self,self.co2_peaks[x],self.bc_peaks[0],'abcd',co2_device,0)
            bc_peak_match(self,self.co2_peaks[x],self.bc_peaks[1],'ae16',co2_device,1)
            bc_peak_match(self,self.co2_peaks[x],self.bc_peaks[2],'ae33',co2_device,2)
            bc_peak_match(self,self.co2_peaks[x],self.bc_peaks[3],'ma300',co2_device,3)


    def EF_calc_nox(self,co2_peaks,divisor,start_window,end_window):
        print("The amount of co2 peaks for " + divisor + "is" + str(quot_len))
        peak_amt = len(co2_peaks)
        for x in range(peak_amt):
            nox_peak_match(self,self.co2_peaks[x],self.nox_peaks[0],'caps',co2_device,0)
            nox_peak_match(self,self.co2_peaks[x],self.nox_peaks[1],'ucb',co2_device,1)

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


        self.EF_calc_bc(self.co2_peaks[0],self.li820_len,'li820',self.li820_bc_start,self.li820_bc_end)
        self.EF_calc_bc(self.co2_peaks[1],self.li7000_len,'li7000',self.li7000_bc_start,self.li7000_bc_end)
        self.EF_calc_bc(self.co2_peaks[2],self.sba5_len,'sba5',self.sba5_bc_start,self.sba5_bc_end)
        self.EF_calc_bc(self.co2_peaks[3],self.vco2_len,'vco2',self.vco2_bc_start,self.vco2_bc_end)

        self.EF_calc_nox(self.co2_peaks[0],self.li820_len,'li820',self.li820_nox_start,self.li820_nox_end)
        self.EF_calc_nox(self.co2_peaks[1],self.li7000_len,'li7000',self.li7000_nox_start,self.li7000_nox_end)
        self.EF_calc_nox(self.co2_peaks[2],self.sba5_len,'sba5',self.sba5_nox_start,self.sba5_nox_end)
        self.EF_calc_nox(self.co2_peaks[3],self.vco2_len,'vco2',self.vco2_nox_start,self.vco2_nox_end)

        # Removes elements from from beginning to the amount of elements that were
        # in the list before hand
        """
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
        """

# Measurement classes
class bc_sensor:
    def __init__(self,all_area,influx_client):
        self.sensor_name = sensor_name
        self.time_values = []
        self.bc_values = []
        self.avg_window = 20

        self.influx_client = influx_client

        self.bc_peaks = []
        # Timestamps for all data
        self.xs = []
        # All BC data
        self.ys = []
        # No pollution data
        self.ynp = [0 for i in range(self.N1)]
        # Timestamps for pollution data
        self.xp = []
        # Pollution data (temp, data held in memory to calculate area)
        # P=peak
        # 7% above mean
        self.yp = []
        # Pollution areas
        self.bc_areas = []
        # Means
        self.ym = []
        # Polluting state
        self.polluting = False
        # Area class variable
        self.area_temp = 0.0

        self.thresh_bc = 7
        #self.logfile1 = "abcd_readings.csv"
        self.peak_start = 0
        self.peak_end = 0

        self.influx_client = influx_client
        self.all_area = all_area


    def push_values(bc_measurement):
            try:
                json =   {
                    'fields': {
                        'bc': bc_measurement[0]
                        },
                    'tags': {
                        'sensor_name': self.sensor_name,
                        },
                    'measurement': 'bc'
                    }
                if (bc_values > 2):
                    json['fields']['atn'] = 'atn': bc_measurement[1]
                    if (bc_values > 3):
                        json['fields']['flow'] = 'atn': bc_measurement[2]
                        json['time'] = bc_values[3]
                    else:
                        json['time'] = bc_values[2]
                else:
                    json['time'] = bc_values[1]

                #print("The bc_abcd1 is: "+ str(bc_abcd1))
                self.influx_client.write_json(json)
            except:
                print("Influx push failure")

    def peak_area(bc_value,bc_peaks):
            run_avg = sum(self.ynp[-self.avg_window:])/float(self.avg_window)
            dif = abs(run_avg - bc_value)
            self.ym.append(run_avg)

            #self.xs_ae33.append(time_str3)
            self.ys.append(bc_value)

            if dif < self.thresh_bc:
                # No event
                if self.polluting_ae33[-1] == True:
                    # Just stopped polluting
                    # Caclulate the statistics
                    # Record ending timestamp
                    bc_area = np.trapz(self.yp, dx=1)
                    self.bc_areas.append(bc_area)
                    #self.xp.append(time_str3)
                    del self.yp[:]
                    self.peak_end = int(time.time()*1000000000)
                    new_time = area_time(bc_area,self.peak_start,self.peak_end)
                    self.bc_peaks.append(new_time)

                self.polluting = False
                self.ynp.append(bc_value)
            else:
                # Pollution event
                if self.polluting == False:
                    self.peak_start = int(time.time()*1000000000)
                    # Just started polluting
                    # Record starting timestamp
                    #self.xp.append(time_str3)
                self.polluting = True
                self.yp.append(bc_value)

class co2_sensor:
    def __init__(self,all_area,influx_client):
        self.sensor_name = sensor_name
        self.time_values = []
        self.co2_values = []
        self.avg_window = 10

        self.influx_client = influx_client
        self.co2_peaks = []

        # Timestamps for all data
        self.xs = []
        # All BC data
        self.ys = []
        # No pollution data
        self.ynp = [450 for m in range(self.N4)]
        # Timestamps for pollution data
        self.xp = []
        # Pollution data (temp, data held in memory to calculate area)
        # P=peak
        # 7% above mean
        self.yp = []
        # Pollution areas
        self.co2_areas = []
        # Means
        self.ym = []
        # Polluting state
        self.polluting= False
        self.thresh_li820 = 700
        self.temp_area = 0.0
        self.peak_start = 0
        self.peak_end = 0

        self.all_area = all_area

    def push_values(co2_measurement):
            try:
                json =   {
                    'fields': {
                        'co2': co2_measurement[0],
                        },
                    'tags': {
                        'sensor_name': self.sensor_name,
                        },
                    'measurement': 'co2'
                    }
                if (len(co2_values)>2):
                    json['fields']['press']: co2_measurement[1]
                    json['time']: co2_measurement[2]
                    if(len(co2_values==3)):
                        json['fields']['temp']: co2_measurement[2]
                        json['time']: co2_measurement[3]
                else:
                    json['time']: co2_measurement[1]
                self.influx_client.write_json(json)
            except:
                print("Influx push failure")

    def peak_area(co2_value):
            self.ys.append(co2_value)

            run_avg = sum(self.ynp[-self.avg_window:])/float(self.avg_window)
            dif = abs(run_avg - co2_value)
            self.thresh = 1.07* run_avg
            self.ym.append(run_avg)

            #self.xs.append(time_str8)
            self.ys.append(co2_value)


            if dif < self.thresh_co2:
                # No event
                if self.polluting == True:
                    # Just stopped polluting
                    # Caclulate the statistics
                    # Record ending timestamp
                    area_co2 = np.trapz(self.yp, dx=1)
                    self.areas.append(area_co2)
                    #self.xp_vco2.append(time_str8)

                    del self.yp[:]
                    new_time = area_time(area_co2,self.peak_start,self.peak_end)
                    #all_area.area_time.append(new_time)
                    self.co2_peaks.append(new_time)

                self.polluting = False
                self.ynp.append(co2_value)

            else:
                # Pollution event
                if self.polluting == False:
                    self.peak_start = int(time.time()*1000000000)
                    # Just started polluting
                    # Record starting timestamp
                    #self.xp.append(time_str8)

                self.polluting = True
                self.yp.append(co2_value)

class nox_sensor:
    def __init__(self,all_area,influx_client):
        self.sensor_name = sensor_name
        self.time_values = []
        self.nox_values = []
        self.nox_peaks = []

        self.influx_client = influx_client
        self.avg_window = 10

        # Timestamps for all data
        self.xs = []
        # All BC data
        self.ys = []
        # No pollution data
        self.ynp = [0 for r in range(self.avg_window)]
        # Timestamps for pollution data
        self.xp = []
        # Pollution data (temp, data held in memory to calculate area)
        # P=peak
        # 7% above mean
        self.yp = []
        # Pollution areas
        self.nox_areas = []
        # Means
        self.ym = []
        # Polluting state
        self.polluting = False
        self.thresh_nox = .1
        self.peak_start = 0
        self.peak_end = 0

        self.all_area = all_area

    def push_values(nox_measurement):
            try:
                json =   {
                    'fields': {
                        'nox': nox_measurement[0],
                        'area': nox_measurement[1]
                        },
                    'time': nox_measurement[2],
                    'tags': {
                        'sensor_name': self.sensor_name,
                        },
                    'measurement': 'nox'
                    }
                self.influx_client.write_json(json)
            except:
                print("Influx push failure")

    def peak_area(nox_value):
        self.ys.append(nox_value)
        run_avg = sum(self.ynp[-self.avg_window:])/float(self.avg_window)
        dif = abs(run_avg - nox_value)
        self.ym.append(run_avg)
        self.xs.append(time_str10)
        self.ys.append(nox_value)
        if dif < self.thresh_nox:
            # No event
            if self.polluting == True:
                # Just stopped polluting
                # Caclulate the statistics
                # Record ending timestamp
                area = np.trapz(self.yp, dx=1)
                base_line_y = [self.thresh_nox for s in range(len(self.yp))]
                base_area = np.trapz(base_line_y, dx=1)
                peak_area = area - base_area
                self.areas.append(peak_area)
                self.xp.append(time_str10)
                del self.yp[:]
                self.peak_end = int(time.time()*1000000000)
                new_time = area_time(peak_area,self.peak_start,self.peak_end)
                self.nox_peaks.append(new_time)
            self.polluting = False
            self.ynp.append(nox_value)

        else:
            # Pollution event
            if self.polluting == False:
                self.peak_start = int(time.time()*1000000000)

            self.polluting = True
            self.yp.append(nox_value)

# BC instruments
class abcd_instrument(bc_sensor):
    def __init__(self):
        self.sensor_name = 'abcd'
        self.serial=serialGeneric("/dev/ttyUSB_abcd",57600)  ##abcd
        self.bc_peaks = self.all_area.bc_peaks[0]

    def get_values(serial,bc_values):
        bc_values = []
        ser = self.ser.readline()
        values_abcd1 = ser.split('\n')[0].split(',')
        #print(values_abcd1)
        time_now=int(time.time()*1000000000)
        time_str1 = dt_object.strftime('%H:%M:%S')
        try:
            atn_abcd1 = float(values_abcd1[3])
            bc_abcd1 = float(values_abcd1[4])
            flow_abcd1 = float(values_abcd1[7])
            bc_values[0] = bc_abcd1
            bc_values[1] = atn_abcd1
            bc_values[2] = flow_abcd1
            bc_values[3] = time_now
            #print(bc_abcd1)

        except (ValueError,IndexError) as e:
            print("abcd index failure")
            continue
        return bc_values

class ae16_instrument(bc_sensor):
    def __init__(self):
        self.sensor_name = 'ae16'
        self.serial=serialGeneric("/dev/ttyUSB_ae16",9600)  ##ae16
        self.bc_peaks = self.all_area.bc_peaks[1]

    def get_values():
        bc_values = []
        ser = self.serial.readline()
        dt_object = datetime.now()
        time_str2 = dt_object.strftime('%H:%M:%S')
        values_ae16 = ser.split('\n')[0].split(',')
        time_now=int(time.time()*1000000000)

        try:
            bc1 = float(values_ae16[2])
            bc_ae16 = bc1/1000
            atn_ae16 = float(values_ae16[9])
            bc_values[0] = bc_ae16
            bc_values[1] = atn_ae16
            bc_values[3] = time_now

        except(ValueError,IndexError) as e:
            print("ae16 index error")
            continue
        return bc_values

class ae33_instrument(bc_sensor):
    def __init__(self):
        self.sensor_name = 'ae33'
        self.serial=serialGeneric("/dev/ttyUSB_ae33",9600)  ##ae33
        self.bc_peaks = self.all_area.bc_peaks[2]

    def get_values():
        bc_values = []
        ser = self.serial.readline()
        dt_object = datetime.now()
        time_str3 = dt_object.strftime('%H:%M:%S')
        values_ae33 = ser.split('\n')[0].split(',')
        time_now=int(time.time()*1000000000)
        try:
            bc2 = float(values_ae33[9])
            bc_ae33 = bc2/1000
            bc_values[0] = bc_ae33
            bc_values[1] = time_now
        except(ValueError,IndexError) as e:
            print("ae33 index failure")
            continue

class ma300_instrument(bc_sensor):
    def __init__(self):
        self.sensor_name = 'ma300'
        self.serial=serialGeneric("/dev/ttyUSB_ma300",1000000)  ##ma300
        self.bc_peaks = self.all_area.bc_peaks[3]

    def get_values():
        bc_values = []
        ser = self.serial.readline()
        dt_object = datetime.now()
        time_str7 = dt_object.strftime('%H:%M:%S')
        values_ma300 = ser.split('\n')[0].split(',')
        time_now=int(time.time()*1000000000)

        try:
            bc3 = float(values_ma300[44])
            bc_values[0] = bc3/1000
            bc_values[1] = time_now

        except (ValueError, IndexError) as e:
            print("ma300 index failure")
            continue

# CO2 instruments

class li820_instrument(co2_sensor):
    def __init__(self):
        self.sensor_name = 'li820'
        self.serial=serialGeneric("/dev/ttyUSB_li820",9600)  ##li820
        self.co2_peaks = self.all_area.co2_peaks[2]
    def get_values():
        co2_values = []
        ser = self.serial.readline()
        dt_object = datetime.now()
        time_str4 = dt_object.strftime('%H:%M:%S')
        time_now=int(time.time()*1000000000)
        try:
            values_li820 = re.split(r'[<>]', ser
            co2_values[0] = float(values_li820[14]) # CO2 value
            co2_values[1] = float(values_li820[6]) # Temperature
            co2_values[2] = float(values_li820[10]) # Pressue
            co2_values[3] = time_now

        except(ValueError,IndexError) as e:
            print("li820 index failure")
            continue
        return co2_values

class li7000_instrument(co2_sensor):
    def __init__(self):
        self.sensor_name = 'li7000'
        self.serial=serialGeneric("/dev/ttyUSB_li7000",9600)  ##li7000
        self.co2_peaks = self.all_area.co2_peaks[1]
    def get_values():
        co2_values = []
        ser = self.serial.readline()
        dt_object = datetime.now()
        time_str5 = dt_object.strftime('%H:%M:%S')
        time_now=int(time.time()*1000000000)
        try:
            values_li7000 = ser.split('\n')[0].split('\t')
            #print("The values for li700 are:")
            #print(values_li7000)
            co2_values[0] = float(values_li7000[2]) # CO2 value
            co2_values[1] = float(values_li7000[5]) # Temperature
            co2_values[2] = float(values_li7000[4]) # Pressue
            co2_values[3] = time_now # time
        except (ValueError,IndexError) as e:
            print("li7000 index failure")
            continue
        return co2_values

class sba5_instrument(co2_sensor):
    def __init__(self):
        self.sensor_name = 'sba5'
        self.serial=serialGeneric("/dev/ttyUSB_sba5",19200)  ##sba5
        self.co2_peaks = self.all_area.co2_peaks[2]
    def get_values():
        co2_values = []
        ser = serial.readline()
        dt_object = datetime.now()
        time_str6 = dt_object.strftime('%H:%M:%S')
        values_sba5 = ser.split('\n')[0].split(' ')
        time_now=int(time.time()*1000000000)

        try:
            co2_values[0] = float(values_sba5[3]) # CO2 value
            co2_values[1] = time_now # Time is always at end of list

        except (ValueError, IndexError) as e:
            print("sba5 index failure")
            continue
        return co2_values

class vco2_instrument(co2_sensor):
    def __init__(self):
        self.sensor_name = 'vco2'
        self.serial=serialGeneric("/dev/ttyUSB_vco2",19200)  ##vaisala
        self.serial.write("R\r\n")
        response=self.serial.readline()
        self.co2_peaks = self.all_area.co2_peaks[3]
    def get_values():
        co2_values = []
        ser = self.serial.readline()
        dt_object = datetime.now()
        time_str8 = dt_object.strftime('%H:%M:%S')
        values_vco2 = ser.split('\n')[0].split('\t')
        time_now=int(time.time()*1000000000)

        try:
            co2_values[0] = float(values_vco2[0])
            co2_values[1] = time_now

        except (ValueError, IndexError) as e:
            print("vco2 index failure")
            continue

# NOX instruments

class caps_instrument(nox_sensor):
    def __init__(self):
        self.sensor_name = 'caps'
        self.serial=serialGeneric("/dev/ttyUSB_nox_caps",9600)  ##caps
        self.nox_peaks = self.all_area.nox_peaks[0]

    def get_values():
        nox_values = []
        ser =  self.serial.readline()
        dt_object = datetime.now()
        time_str9 = dt_object.strftime('%H:%M:%S')
        values_caps = ser.split('\n')[0].split(',')
        time_now=int(time.time()*1000000000)

        try:
            nox1 = float(values_caps[1])
            nox_value[0] = nox1/1000
            nox_values[1] = time_now

        except (ValueError, IndexError) as e:
            print("caps index failure")
            continue
        return nox_values

class ucb_instrument(nox_sensor):
    def __init__(self):
    self.sensor_name = 'ucb'
    self.serial= serial.Serial (port='/dev/ttyUSB_nox_ucb',
            baudrate=9600,
            timeout = 1,
            bytesize=serial.SEVENBITS)
    self.nox_peaks = self.all_area.nox_peaks[1]
    def get_values():
        nox_values = []
        serial.write(b'\x0201RD0\x03\x26')
        ser = serial.readline()
        dt_object = datetime.now()
        time_str10 = dt_object.strftime('%H:%M:%S')
        time_now=int(time.time()*1000000000)

        try:
            output_ucb = ser.decode('ascii')
            values_ucb = output_ucb.split('\n')[0].split(',')
            if float(values_ucb[1])!=0:
                nox_values[0] = float(values_ucb[1])
                nox_values[1] = time_now


        except Exception as e:
            print("ucb index failure")
            print (e)
            continue

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

class sensor_thread(threading.Thread):

    def __init__(self, sensor):
        threading.Thread.__init__(self)
        self.sensor=sensor
        self.readings = []
        self.polluting = False
    def run(self):
        count = 0
        #self.readings[:20] = [0] * 20

        while not stop_requested:
            values = self.sensor.get_values()
            self.readings.append(values[0])
            self.sensor.push_values(values)
            self.sensor.peak_area(values[0])
            count+=1

def main():
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)

    # read arguments passed at .py file call
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="config file")
    args = parser.parse_args()
    config_file = args.config
    influx_client = Influx_Dataframe_Client(config_file,'DB_config')

    all_area=area_container(test_client)

    # Create all bc sensor objects
    abcd_sensor = abcd_instrument(influx_client)
    ae16_sensor = ae16_instrument(influx_client)
    ae33_sensor = ae33_instrument(influx_client)
    ma300_sensor = ma300_instrument(influx_client)
    # Create all co2 sensor objects
    li820_sensor = li820_instrument(influx_client)
    li7000_sensor = li7000_instrument(influx_client)
    sba5_sensor = sba5_instrument(influx_client)
    vco2_sensor = vco2_instrument(influx_client)
    # Create all nox sensor objects
    caps_sensor = caps_instrument(influx_client)
    ucb_sensor = ucb_instrument(influx_client)

    # Create threads for each sensor
    bc_abcd_thread=sensor_thread(abcd_sensor)
    bc_ae16_thread=sensor_thread(ae16_sensor)
    bc_ae33_thread=sensor_thread(ae33_sensor)
    bc_ma300_thread=sensor_thread(ma300_sensor)
    co2_li820_thread=sensor_thread(li820_sensor)
    co2_li7000_thread=sensor_thread(li7000)
    co2_sba5_thread=sensor_thread(sba5_sensor)
    co2_vco2_thread=sensor_thread(vco2_sensor)
    nox_caps_thread=sensor_thread(caps_sensor)
    nox_ucb_thread=sensor_thread(ucb_sensor)
    area_thread=areaThread(all_area)

    # Start all threads
    bc_abcd.start()
    bc_ae16.start()
    bc_ae33.start()
    bc_ma300.start()
    co2_li820.start()
    co2_li7000.start()
    co2_sba5.start()
    co2_vco2.start()
    nox_caps.start()
    nox_ucb.start()
    area_thread.start()

    while not stop_requested: # Should terminate loop on keyboard interrupt
        time.sleep(1)

    return

if __name__ == "__main__":
    main()
