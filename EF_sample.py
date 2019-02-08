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

stop_requested = False # Condition flag for keyboard interrupt
bc_correction = 0.88 # going to place this in the config file

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

# Measurement classes these are extended with instrument classes for both
# serial and data retrieval

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
        self.polution_times = []

        self.all_peaks = all_peaks
        self.co2_peaks = self.all_peaks.co2_peaks[self.sensor_name]

    def push_values(self,co2_measurement):
            try:
                """
                Generate JSON specific to what information was contained in
                in co2_measurement array.
                co2_measurement[0]: CO2 measurement
                co2_measurement[1]: timestamp of measurement if all fields present
                co2_measurement[2]: Temperature (if present)
                co2_measurement[3]: Pressue (if present)
                """
                json =   {
                    'fields': {
                        'co2': co2_measurement[0]
                        },
                    'tags': {
                        'sensor_name': self.sensor_name
                        },
                    'time': co2_measurement[1],
                    'measurement': 'co2'
                    }
                if (len(co2_measurement)>2):
                    json['fields']['temp'] = co2_measurement[2]
                    if(len(co2_measurement)==4):
                        json['fields']['press'] = co2_measurement[3]

                self.influx_client.write_json(json)
            except:
                print("Influx push failure from: " + self.sensor_name)

    def peak_area(self,co2_value,time_stamp):
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
                    area = np.trapz(self.yp, dx=1)
                    yp_nd_array = np.asarray(self.yp)
                    peak_indexes = peakutils.peak.indexes(yp_nd_array, thres=.1)

                    # Print diagnostic information for peak centers
                    print("Ndarray for " + self.sensor_name)
                    print(yp_nd_array)
                    print("Peak amount for "+ self.sensor_name + "is: " +str(peak_indexes.size))

                    print("Polluting y values for " + self.sensor_name + "is: ")
                    print(self.yp)
                    print("Area is: " +str(area))

                    print("time array for " + self.sensor_name)
                    print(self.polution_times)
                    print("Peak amount for "+ self.sensor_name + "is: " +str(peak_indexes.size))

                    # Send all peak centers to influx
                    for x in peak_indexes:
                        time_sum = self.polution_times[x]
                        json_center =   {
                            'fields': {
                                'area': area,
                                'co2': yp_nd_array[x]
                                },
                            'time': self.polution_times[x],
                            'tags': {
                                'sensor': self.sensor_name,
                                'type': 'center'
                                },
                            'measurement': 'peak_event'
                            }
                        print("Time is " + str(self.polution_times[x]))
                        print("concentration is " + str(yp_nd_array[x]))
                        self.influx_client.write_json(json_center)

                    self.peak_end = self.polution_times[-1]
                    del self.yp[:]
                    del self.polution_times[:]

                    new_time = CO2_Peak_Event(area,self.peak_start,self.peak_end,
                        self.all_peaks.current_li7000_pressure,
                        self.all_peaks.current_li7000_temp)

                    self.co2_peaks.append(new_time)
                    json_start =   {
                        'fields': {
                            'area': new_time.area
                            },
                        'time': self.peak_start,
                        'tags': {
                            'sensor': self.sensor_name,
                            'type': 'start'
                            },
                        'measurement': 'peak_event'
                    }
                    json_end =   {
                        'fields': {
                            'area': new_time.area
                            },
                        'time': self.peak_end,
                        'tags': {
                            'sensor': self.sensor_name,
                            'type': 'end'
                            },
                        'measurement': 'peak_event'
                        }
                    self.influx_client.write_json(json_start)
                    self.influx_client.write_json(json_end)

                # Not currently polluting and not polluting during previous read
                self.polluting = False
                self.ynp.append(co2_value)

            else:
                # Pollution event
                if self.polluting == False:
                    self.peak_start = time_stamp
                    # Just started polluting
                    # Record starting timestamp
                    #self.xp.append(time_str8)

                self.polluting = True
                self.yp.append(co2_value)
                self.polution_times.append(time_stamp)

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
            co2_values.insert(1,time_now)
            co2_values.insert(2,float(values_li820[10])) # Temp
            co2_values.insert(3,float(values_li820[6])) # Pressure

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
            co2_values.insert(1,time_now)
            co2_values.insert(2,float(values_li7000[4])) # Temp
            co2_values.insert(3,float(values_li7000[5])) # Pressure
            # Save most recent temperature and pressure from Li7000 instrument
            self.all_peaks.current_li7000_temp = co2_values[1]
            self.all_peaks.current_li7000_pressure = co2_values[2]
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
            print(float(values_sba5[7]))
            co2_values.insert(0,float(values_sba5[3])) # CO2 value
            co2_values.insert(1,time_now)# Time
            co2_values.insert(2,float(values_sba5[4])) # CO2 temp
            co2_values.insert(3,float(values_sba5[7])) # CO2 pressure



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
            co2_values.insert(0,float(values_vco2[0])) # CO2
            co2_values.insert(1,time_now) # time
            co2_values.insert(2,float(values_vco2[1])) # temp
            #co2_values.insert(3,float(999)) #pressure


        except (ValueError, IndexError) as e:
            print("vco2 index failure")
            return co2_values
        return co2_values


# Thread classes

# Thread class which matches Peak Events and calculates the Emission Factors

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
            print("The measurement value for "+self.sensor.sensor_name + "is " + str(values[0]))
            self.readings.append(values[0])
            self.sensor.push_values(values)
            self.sensor.peak_area(values[0],values[1])
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

    # Create all co2 sensor objects
    li820_sensor = LI820_Instrument(all_peaks,influx_client)
    li7000_sensor = LI7000_Instrument(all_peaks,influx_client)
    sba5_sensor = SBA5_Instrument(all_peaks,influx_client)
    vco2_sensor = VCO2_Instrument(all_peaks,influx_client)

    co2_li820_thread=Sensor_Thread(li820_sensor)
    co2_li7000_thread=Sensor_Thread(li7000_sensor)
    co2_sba5_thread=Sensor_Thread(sba5_sensor)
    co2_vco2_thread=Sensor_Thread(vco2_sensor)

    co2_li820_thread.start()
    co2_li7000_thread.start()
    co2_sba5_thread.start()
    co2_vco2_thread.start()

    while not stop_requested: # Should terminate loop on keyboard interrupt
        time.sleep(1)

    return

if __name__ == "__main__":
    main()
