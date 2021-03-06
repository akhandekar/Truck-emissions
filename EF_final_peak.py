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

class Peak_Event:
    #switch to lists so we don't have to save elements
    def __init__(self,area,start_time,end_time):
        # Create Peak_Event object
        self.area = area
        #self.time = time
        self.start_time = start_time
        self.end_time = end_time
        # Potentially may want to add in baseline for subtracting base rectangle

# Storage of peaks for each instrument as well function for calculating EF

class Peak_Container:
    def __init__(self,influx_client):
        # create all area lists
        self.influx_client = influx_client
        # CO2 peak information lists
        self.co2_peaks = {}
        self.co2_peaks['li820'] = []
        self.co2_peaks['li7000'] = [] #li7000 sensor
        self.co2_peaks['sba5'] = [] #sba5 sensor
        self.co2_peaks['vco2'] = [] #vco2 sensor
        # BC Area Values
        self.bc_peaks = {}
        self.bc_peaks['abcd'] = []#abcd sensor
        self.bc_peaks['ae16'] =[] #ae16 sensor
        self.bc_peaks['ae33'] = []#ae33 sensor
        self.bc_peaks['ma300'] = []#ma300 sensor
        # Nox areav values
        self.nox_peaks = {}
        self.nox_peaks['caps'] = [] # caps sensor
        self.nox_peaks['ucb'] = [] # ucb sensor

        # Windows for matching peaks between instruments
        self.start_window = {
            'li820':{
                'abcd':4,
                'ae16':1,
                'ae33':5,
                'ma300':5,
                'caps':2.5,
                'ucb':1
            },
            'li7000':{
                'abcd':5,
                'ae16':1.5,
                'ae33':6,
                'ma300':6,
                'caps':3,
                'ucb':1.5
            },
            'sba5':{
                'abcd':1.5,
                'ae16':3,
                'ae33':3,
                'ma300':3,
                'caps':1,
                'ucb':3
            },
            'vco2':{
                'abcd':3,
                'ae16':6,
                'ae33':3,
                'ma300':3,
                'caps':4.5,
                'ucb':6
            },

        }

        self.end_window = {
            'li820':{
                'abcd':5,
                'ae16':5,
                'ae33':9.5,
                'ma300':9.5,
                'caps':2.5,
                'ucb':1

            },
            'li7000':{
                'abcd':6,
                'ae16':6,
                'ae33':10,
                'ma300':10,
                'caps':3,
                'ucb':2
            },
            'sba5':{
                'abcd':2,
                'ae16':1.5,
                'ae33':4.5,
                'ma300':4.5,
                'caps':2.5,
                'ucb':4
            },
            'vco2':{
                'abcd':2,
                'ae16':2,
                'ae33':4,
                'ma300':4,
                'caps':3,
                'ucb':5
            },

        }
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


        # CO2 Peak_Event lengths
        self.co2_peaks_amt = {}
        self.co2_peaks_amt['li820'] = 0
        self.co2_peaks_amt['li7000'] = 0
        self.co2_peaks_amt['sba5'] = 0
        self.co2_peaks_amt['vco2'] = 0
        # BC Peak_Event lengths
        self.bc_peaks_amt = {}
        self.bc_peaks_amt['abcd'] = 0
        self.bc_peaks_amt['ae16'] = 0
        self.bc_peaks_amt['ae33'] = 0
        self.bc_peaks_amt['ma300'] = 0
        # NOx Peak_Event length
        self.nox_peaks_amt = {}
        self.nox_peaks_amt['caps'] = 0
        self.nox_peaks_amt['ucb'] = 0

        self.delta_window = 10


    # Go through each item in the list and check to see if the timestamps match,
    # if they do push to influx, if the member of the list doesn't match with anything
    # else...then remove it make sure to only check through the current members of the list
    #
    def bc_peak_match(self,single_co2_peak,bc_device,co2_device,dev_id,start_window,end_window):
            print("The co2 timestamp start is " + co2_device + "is" + str(single_co2_peak.start_time))
            for y in range(len(self.bc_peaks[bc_device])):
                difference = single_co2_peak.start_time - self.bc_peaks[bc_device][y].start_time
                end_difference = single_co2_peak.end_time - self.bc_peaks[bc_device][y].end_time
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
                        print("We have a match at EF with abcd and" + co2_device)
                        EF = self.bc_peaks[bc_device][y].area / single_co2_peak.area
                        json =   {
                            'fields': {
                                'EF': EF
                                },
                            'time': single_co2_peak.start_time,
                            'tags': {
                                'co2_device': co2_device,
                                'bc_device': bc_device
                                },
                            'measurement': 'emission_factor'
                            }
                        self.influx_client.write_json(json)

    def nox_peak_match(self,single_co2_peak,nox_device,co2_device,dev_id,start_window,end_window):
        for y in range(len(self.nox_peaks[nox_device])):
            difference = single_co2_peak.start_time - self.nox_peaks[nox_device][y].start_time
            end_difference = single_co2_peak.end_time - self.nox_peaks[nox_device][y].end_time
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
                    print("We have a match at EF with caps and" + nox_device)
                    EF = self.nox_peaks[nox_device][y].area / single_co2_peak.area
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

    def EF_calc_bc(self,co2_device,start_window,end_window):
        co2_peak_amt = self.co2_peaks_amt[co2_device]
        #print("The amount of co2 peaks for " + co2_device + "is" + str(co2_peak_amt))
        for x in range(co2_peak_amt):
            self.bc_peak_match(self.co2_peaks[co2_device][x],'abcd',co2_device,0,start_window,end_window)
            self.bc_peak_match(self.co2_peaks[co2_device][x],'ae16',co2_device,1,start_window,end_window)
            self.bc_peak_match(self.co2_peaks[co2_device][x],'ae33',co2_device,2,start_window,end_window)
            self.bc_peak_match(self.co2_peaks[co2_device][x],'ma300',co2_device,3,start_window,end_window)

    def EF_calc_nox(self,co2_device,start_window,end_window):
        co2_peak_amt = self.co2_peaks_amt[co2_device]
        #print("The amount of co2 peaks for " + co2_device + "is" + str(co2_peak_amt))
        for x in range(co2_peak_amt):
            self.nox_peak_match(self.co2_peaks[co2_device][x],'caps',co2_device,0,start_window,end_window)
            self.nox_peak_match(self.co2_peaks[co2_device][x],'ucb',co2_device,1,start_window,end_window)

    def EF_calc_all(self):
        print("Entered into EF_calc_all")
        # Retrieve lengths for all lists
        # Get amount of Peaks from all CO2 devices
        for instrument in self.co2_peaks_amt:
            self.co2_peaks_amt[instrument] = len(self.co2_peaks[instrument])
        # Get amount of Peaks from all BC devices
        for instrument in self.bc_peaks_amt:
            self.bc_peaks_amt[instrument] = len(self.bc_peaks[instrument])
        # Get amount of Peaks from all NOX devices
        for key in self.nox_peaks_amt:
            self.nox_peaks_amt[key] = len(self.nox_peaks[key])

        self.EF_calc_bc('li820',self.li820_bc_start,self.li820_bc_end)
        self.EF_calc_bc('li7000',self.li7000_bc_start,self.li7000_bc_end)
        self.EF_calc_bc('sba5',self.sba5_bc_start,self.sba5_bc_end)
        self.EF_calc_bc('vco2',self.vco2_bc_start,self.vco2_bc_end)

        self.EF_calc_nox('li820',self.li820_nox_start,self.li820_nox_end)
        self.EF_calc_nox('li7000',self.li7000_nox_start,self.li7000_nox_end)
        self.EF_calc_nox('sba5',self.sba5_nox_start,self.sba5_nox_end)
        self.EF_calc_nox('vco2',self.vco2_nox_start,self.vco2_nox_end)

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

# Measurement classes these are extended with instrument classes for both
# serial and data retrieval
class BC_Sensor:
    def __init__(self,sensor_name,all_peaks,influx_client):
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
        self.ynp = [0 for i in range(self.avg_window)]
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
        self.all_peaks = all_peaks
        self.bc_peaks = self.all_peaks.bc_peaks[self.sensor_name]


    def push_values(self,bc_measurement):
            try:
                """
                Generate JSON specific to what information was contained in
                in bc_measurement array. Timestamp is always the last element of
                the array.
                bc_measurement[0]: Black Carbon measurement
                bc_measurement[1]: ATN (if present)
                bc_measurement[2]: FLOW (if present)
                bc_measurement[3]: timestamp of measurement if all fields present
                """

                json =   {
                    'fields': {
                        'bc': bc_measurement[0]
                        },
                    'tags': {
                        'sensor_name': self.sensor_name,
                        },
                    'measurement': 'bc'
                    }
                if (len(bc_measurement) > 2):
                    json['fields']['atn'] = bc_measurement[1]
                    if (len(bc_measurement) > 3):
                        json['fields']['flow'] = bc_measurement[2]
                        json['time'] = bc_measurement[3]
                    else:
                        json['time'] = bc_measurement[2]
                else:
                    json['time'] = bc_measurement[1]

                self.influx_client.write_json(json)
            except:
                print("Influx push failure from: " + self.sensor_name)

    def peak_area(self,bc_value):
            run_avg = sum(self.ynp[-self.avg_window:])/float(self.avg_window)
            dif = abs(run_avg - bc_value)
            self.ym.append(run_avg)

            #self.xs_ae33.append(time_str3)
            self.ys.append(bc_value)

            if dif < self.thresh_bc:
                # No event
                if self.polluting == True:
                    # Just stopped polluting
                    # Caclulate the statistics
                    # Record ending timestamp
                    bc_area = np.trapz(self.yp, dx=1)
                    #self.bc_areas.append(bc_area)
                    #self.xp.append(time_str3)
                    del self.yp[:]
                    self.peak_end = int(time.time()*1000000000)
                    new_time = Peak_Event(bc_area,self.peak_start,self.peak_end)
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

class CO2_Sensor:
    def __init__(self,sensor_name,all_peaks,influx_client):
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
        self.ynp = [450 for m in range(self.avg_window)]
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
        self.thresh_co2 = 700
        self.temp_area = 0.0
        self.peak_start = 0
        self.peak_end = 0

        self.all_peaks = all_peaks
        self.co2_peaks = self.all_peaks.co2_peaks[self.sensor_name]

    def push_values(self,co2_measurement):
            try:
                """
                Generate JSON specific to what information was contained in
                in co2_measurement array. Timestamp is always the last element of
                the array.
                co2_measurement[0]: CO2 measurement
                co2_measurement[1]: Pressue (if present)
                co2_measurement[2]: Temperature (if present)
                co2_measurement[3]: timestamp of measurement if all fields present
                """
                json =   {
                    'fields': {
                        'co2': co2_measurement[0]
                        },
                    'tags': {
                        'sensor_name': self.sensor_name
                        },
                    'measurement': 'co2'
                    }
                if (len(co2_measurement)>2):
                    json['fields']['press'] = co2_measurement[1]
                    if(len(co2_measurement)==4):
                        json['fields']['temp'] = co2_measurement[2]
                        json['time'] = co2_measurement[3]
                    else:
                        json['time'] = co2_measurement[2]
                else:
                    json['time'] = co2_measurement[1]
                self.influx_client.write_json(json)
            except:
                print("Influx push failure from: " + self.sensor_name)

    def peak_area(self,co2_value):
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
                    #self.areas.append(area_co2)
                    #self.xp_vco2.append(time_str8)

                    del self.yp[:]
                    new_time = Peak_Event(area_co2,self.peak_start,self.peak_end)
                    #all_peaks.Peak_Event.append(new_time)
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

class NOX_Sensor:
    def __init__(self,sensor_name,all_peaks,influx_client):
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

        self.all_peaks = all_peaks
        self.nox_peaks = self.all_peaks.nox_peaks[self.sensor_name]

    def push_values(self,nox_measurement):
            try:
                """
                Generate JSON specific to what information was contained in
                in nox_measurement array. Timestamp is always the last element of
                the array.
                nox_measurement[0]: NOX measurement
                nox_measurement[1]: timestamp of measurement
                """
                json =   {
                    'fields': {
                        'nox': nox_measurement[0]
                        },
                    'time': nox_measurement[1],
                    'tags': {
                        'sensor_name': self.sensor_name,
                        },
                    'measurement': 'nox'
                    }
                self.influx_client.write_json(json)
            except:
                print("Influx push failure from: " + self.sensor_name)

    def peak_area(self,nox_value):
        self.ys.append(nox_value)
        run_avg = sum(self.ynp[-self.avg_window:])/float(self.avg_window)
        dif = abs(run_avg - nox_value)
        self.ym.append(run_avg)
        #self.xs.append(time_str10)
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
                #self.areas.append(peak_area)
                #self.xp.append(time_str10)
                del self.yp[:]
                self.peak_end = int(time.time()*1000000000)
                new_time = Peak_Event(peak_area,self.peak_start,self.peak_end)
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
class ABCD_instrument(BC_Sensor):
    def __init__(self,all_peaks,influx_client):
        BC_Sensor.__init__(self,'abcd',all_peaks,influx_client)
        self.serial=serialGeneric("/dev/ttyUSB_abcd",57600)  ##abcd

    def get_values(self):
        bc_values = []
        ser = self.serial.readline()
        values_abcd1 = ser.split('\n')[0].split(',')
        #print(values_abcd1)
        time_now=int(time.time()*1000000000)
        #time_str1 = dt_object.strftime('%H:%M:%S')
        try:
            #print(values_abcd1)
            atn_abcd1 = float(values_abcd1[3])
            bc_abcd1 = float(values_abcd1[4])
            flow_abcd1 = float(values_abcd1[7])
            bc_values.insert(0,bc_abcd1)
            bc_values.insert(1,atn_abcd1)
            bc_values.insert(2,flow_abcd1)
            bc_values.insert(3,time_now)
            #print(bc_abcd1)

        except (ValueError,IndexError) as e:
            print("abcd index failure")
            return bc_values
        return bc_values

class AE16_Instrument(BC_Sensor):
    def __init__(self,all_peaks,influx_client):
        BC_Sensor.__init__(self,'ae16',all_peaks,influx_client)
        self.serial=serialGeneric("/dev/ttyUSB_ae16",9600)  ##ae16

    def get_values(self):
        bc_values = []
        ser = self.serial.readline()
        dt_object = datetime.now()
        time_str2 = dt_object.strftime('%H:%M:%S')
        values_ae16 = ser.split('\n')[0].split(',')
        time_now=int(time.time()*1000000000)

        try:
            #print(values_ae16)
            bc1 = float(values_ae16[2])
            bc_ae16 = bc1/1000
            atn_ae16 = float(values_ae16[9])
            bc_values.insert(0,bc_ae16)
            bc_values.insert(1,atn_ae16)
            bc_values.insert(2,time_now)

        except(ValueError,IndexError) as e:
            print("ae16 index error")
            return bc_values
        return bc_values

class AE33_Instrument(BC_Sensor):
    def __init__(self,all_peaks,influx_client):
        BC_Sensor.__init__(self,'ae33',all_peaks,influx_client)
        self.serial=serialGeneric("/dev/ttyUSB_ae33",9600)  ##ae33

    def get_values(self):
        bc_values = []
        ser = self.serial.readline()
        dt_object = datetime.now()
        time_str3 = dt_object.strftime('%H:%M:%S')
        values_ae33 = ser.split('\n')[0].split(',')
        time_now=int(time.time()*1000000000)
        try:
            #print(values_ae33)
            bc2 = float(values_ae33[9])
            bc_ae33 = bc2/1000
            bc_values.insert(0,bc_ae33)
            bc_values.insert(1,time_now)
        except(ValueError,IndexError) as e:
            print("ae33 index failure")
            return bc_values
        return bc_values

class MA300_Instrument(BC_Sensor):
    def __init__(self,all_peaks,influx_client):
        BC_Sensor.__init__(self,'ma300',all_peaks,influx_client)
        self.serial=serialGeneric("/dev/ttyUSB_ma300",1000000)  ##ma300

    def get_values(self):
        bc_values = []
        ser = self.serial.readline()
        dt_object = datetime.now()
        time_str7 = dt_object.strftime('%H:%M:%S')
        values_ma300 = ser.split('\n')[0].split(',')
        time_now=int(time.time()*1000000000)

        try:
            #print(values_ma300)
            bc3 = float(values_ma300[44])
            bc_values.insert(0,(bc3/1000))
            bc_values.insert(1,time_now)

        except (ValueError, IndexError) as e:
            print("ma300 index failure")
            return bc_values
        return bc_values

# CO2 instruments

class LI820_Instrument(CO2_Sensor):
    def __init__(self,all_peaks,influx_client):
        CO2_Sensor.__init__(self,'li820',all_peaks,influx_client)
        self.serial=serialGeneric("/dev/ttyUSB_li820",9600)  ##li820
    def get_values(self):
        co2_values = []
        ser = self.serial.readline()
        dt_object = datetime.now()
        time_str4 = dt_object.strftime('%H:%M:%S')
        time_now=int(time.time()*1000000000)
        try:
            values_li820 = re.split(r'[<>]', ser)
            #print(values_1820)
            co2_values.insert(0,float(values_li820[14])) # CO2 value
            co2_values.insert(1,float(values_li820[6])) # Temperature
            co2_values.insert(2,float(values_li820[10])) # Pressue
            co2_values.insert(3,time_now)

        except(ValueError,IndexError) as e:
            print("li820 index failure")
            return co2_values
        return co2_values

class LI7000_Instrument(CO2_Sensor):
    def __init__(self,all_peaks,influx_client):
        CO2_Sensor.__init__(self,'li7000',all_peaks,influx_client)
        self.serial=serialGeneric("/dev/ttyUSB_li7000",9600)

    def get_values(self):
        co2_values = []
        ser = self.serial.readline()
        dt_object = datetime.now()
        time_str5 = dt_object.strftime('%H:%M:%S')
        time_now=int(time.time()*1000000000)
        try:
            values_li7000 = ser.split('\n')[0].split('\t')
            #print("The values for li700 are:")
            #print(values_li7000)
            co2_values.insert(0,float(values_li7000[2])) # CO2 value
            co2_values.insert(1,float(values_li7000[5])) # Temperature
            co2_values.insert(2,float(values_li7000[4])) # Pressue
            co2_values.insert(3,time_now)
            #print(co2_values)
        except (ValueError,IndexError) as e:
            print("li7000 index failure")
            return co2_values
        return co2_values

class SBA5_Instrument(CO2_Sensor):
    def __init__(self,all_peaks,influx_client):
        CO2_Sensor.__init__(self,'sba5',all_peaks,influx_client)
        self.serial=serialGeneric("/dev/ttyUSB_sba5",19200)  ##sba5
    def get_values(self):
        co2_values = []
        ser = self.serial.readline()
        dt_object = datetime.now()
        time_str6 = dt_object.strftime('%H:%M:%S')
        values_sba5 = ser.split('\n')[0].split(' ')
        time_now=int(time.time()*1000000000)

        try:
            #print(values_sba5)
            co2_values.insert(0,float(values_sba5[3])) # CO2 value
            co2_values.insert(1,time_now)# Time is always at end of list

        except (ValueError, IndexError) as e:
            print("sba5 index failure")
            return co2_values
        return co2_values

class VCO2_Instrument(CO2_Sensor):
    def __init__(self,all_peaks,influx_client):
        CO2_Sensor.__init__(self,'vco2',all_peaks,influx_client)
        self.serial=serialGeneric("/dev/ttyUSB_vco2",19200)  ##vaisala
        self.serial.write("R\r\n")
        response=self.serial.readline()
    def get_values(self):
        co2_values = []
        ser = self.serial.readline()
        dt_object = datetime.now()
        time_str8 = dt_object.strftime('%H:%M:%S')
        values_vco2 = ser.split('\n')[0].split('\t')
        time_now=int(time.time()*1000000000)

        try:
            #print(values_vco2)
            co2_values.insert(0,float(values_vco2[0]))
            co2_values.insert(1,time_now)
        except (ValueError, IndexError) as e:
            print("vco2 index failure")
            return co2_values
        return co2_values

# NOX instruments

class CAPS_Instrument(NOX_Sensor):
    def __init__(self,all_peaks,influx_client):
        NOX_Sensor.__init__(self,'caps',all_peaks,influx_client)
        self.serial=serialGeneric("/dev/ttyUSB_nox_caps",9600)  ##caps

    def get_values(self):
        nox_values = []
        ser =  self.serial.readline()
        dt_object = datetime.now()
        time_str9 = dt_object.strftime('%H:%M:%S')
        values_caps = ser.split('\n')[0].split(',')
        time_now=int(time.time()*1000000000)

        try:
            #print(values_caps)
            nox1 = float(values_caps[1])
            nox_values.insert(0,(nox1/1000))
            nox_values.insert(1,time_now)

        except (ValueError, IndexError) as e:
            print("caps index failure")
            return nox_values
        return nox_values

class UCB_Instrument(NOX_Sensor):
    def __init__(self,all_peaks,influx_client):
        NOX_Sensor.__init__(self,'ucb',all_peaks,influx_client)
        self.serial= serial.Serial (port='/dev/ttyUSB_nox_ucb',
                baudrate=9600,
                timeout = 1,
                bytesize=serial.SEVENBITS)

    def get_values(self):
        nox_values = []
        self.serial.write(b'\x0201RD0\x03\x26')
        ser = self.serial.readline()
        dt_object = datetime.now()
        time_str10 = dt_object.strftime('%H:%M:%S')
        time_now=int(time.time()*1000000000)

        try:
            output_ucb = ser.decode('ascii')
            values_ucb = output_ucb.split('\n')[0].split(',')
            #print(values_ucb)
            if float(values_ucb[1])!=0:
                nox_values.insert(0,float(values_ucb[1]))
                nox_values.insert(1,time_now)

        except Exception as e:
            print("ucb index failure")
            print (e)
            return nox_values
        return nox_values

# Thread classes

# Thread class which matches Peak Events and calculates the Emission Factors
class EF_Thread(threading.Thread):
    def __init__(self,all_peaks):
        threading.Thread.__init__(self)
        self.all_peaks = all_peaks
        print("Started influx thread")

    def run(self):
        i = 0
        while not stop_requested:
            time.sleep(5)
            self.all_peaks.EF_calc_all()
            i+=1

# Thread class which retrieves the measurement from the device and pushes it to
# influx database. Peak Events are found if present
class Sensor_Thread(threading.Thread):

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
            if(len(values) == 0):
                continue
            #print("The measurement value for "+self.sensor.sensor_name + "is " + str(values[0]))
            self.readings.append(values[0])
            self.sensor.push_values(values)
            self.sensor.peak_area(values[0])
            count+=1

# Main function will be called when file is executed

def main():

    # Setup signal handler to allow for exiting on Keyboard Interrupt (Ctrl +C)
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)

    # read arguments passed at .py file call
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="config file")
    args = parser.parse_args()
    config_file = args.config

    # Influx client with credentials obtained from command line argument
    influx_client = Influx_Dataframe_Client(config_file,'DB_config')

    # Peak thread object
    all_peaks=Peak_Container(influx_client)

    # Create all bc sensor objects
    abcd_sensor = ABCD_instrument(all_peaks,influx_client)
    ae16_sensor = AE16_Instrument(all_peaks,influx_client)
    ae33_sensor = AE33_Instrument(all_peaks,influx_client)
    ma300_sensor = MA300_Instrument(all_peaks,influx_client)
    # Create all co2 sensor objects
    li820_sensor = LI820_Instrument(all_peaks,influx_client)
    li7000_sensor = LI7000_Instrument(all_peaks,influx_client)
    sba5_sensor = SBA5_Instrument(all_peaks,influx_client)
    vco2_sensor = VCO2_Instrument(all_peaks,influx_client)
    # Create all nox sensor objects
    caps_sensor = CAPS_Instrument(all_peaks,influx_client)
    ucb_sensor = UCB_Instrument(all_peaks,influx_client)

    # Create threads for each sensor
    bc_abcd_thread=Sensor_Thread(abcd_sensor)
    bc_ae16_thread=Sensor_Thread(ae16_sensor)
    bc_ae33_thread=Sensor_Thread(ae33_sensor)
    bc_ma300_thread=Sensor_Thread(ma300_sensor)
    co2_li820_thread=Sensor_Thread(li820_sensor)
    co2_li7000_thread=Sensor_Thread(li7000_sensor)
    co2_sba5_thread=Sensor_Thread(sba5_sensor)
    co2_vco2_thread=Sensor_Thread(vco2_sensor)
    nox_caps_thread=Sensor_Thread(caps_sensor)
    nox_ucb_thread=Sensor_Thread(ucb_sensor)

    # Create peak thread
    ef_thread=EF_Thread(all_peaks)

    # Start all threads
    bc_abcd_thread.start()
    bc_ae16_thread.start()
    bc_ae33_thread.start()
    bc_ma300_thread.start()
    co2_li820_thread.start()
    co2_li7000_thread.start()
    co2_sba5_thread.start()
    co2_vco2_thread.start()
    nox_caps_thread.start()
    nox_ucb_thread.start()
    ef_thread.start()

    while not stop_requested: # Should terminate loop on keyboard interrupt
        time.sleep(1)

    return

if __name__ == "__main__":
    main()
