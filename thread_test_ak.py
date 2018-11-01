import serial
from time import time
import threading
import datetime as dt
import numpy as np
#import matplotlib.pyplot as plt
#import matplotlib.animation as animation
import os, sys, csv, re



def serialGeneric(device,baudrate):
    ser = serial.Serial (port=device,
    baudrate=baudrate,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
    )
    return ser


with open("abcd_readings.csv", "w") as fp:
    # fp.write("timestamp,Vref,Vsig,ATN,BC,RH,Temp,FR,Batt\n")
    fp.write("timestamp,BC\n")

with open("ae16_readings.csv", "w") as fp:
    # fp.write("timestamp,Vref,Vsig,ATN,BC,RH,Temp,FR,Batt\n")
    fp.write("timestamp,BC\n")

with open("li820_readings.csv", "w") as fp:
    # fp.write("timestamp,Vref,Vsig,ATN,BC,RH,Temp,FR,Batt\n")
    fp.write("timestamp,CO2\n")

serial1=serialGeneric("/dev/ttyUSB0",57600)  ##abcd
##serial2=serialGeneric("/dev/ttyUSB0",9600)  ##ae16
##serial3=serialGeneric("/dev/ttyUSB1",9600)  ##ae33
##serial4=serialGeneric("/dev/ttyUSB2",9600)  ##li820
##serial5=serialGeneric("/dev/ttyUSB3",9600)  ##li7000
##serial6=serialGeneric("/dev/ttyUSB2",9600)  ##sba5
##serial7=serialGeneric("/dev/ttyUSB2",9600)  ##ma300
##serial8=serialGeneric("/dev/ttyUSB2",9600)  ##caps
##serial9=serialGeneric("/dev/ttyUSB2",9600)  ##nox

#fig1 = plt.figure()
#ax1 = fig1.add_subplot(6, 1, 2)
#ax2 = fig1.add_subplot(6, 1, 6)
#ax3 = fig1.add_subplot(6, 1, 4)

##fig2 = plt.figure()
##ax1 = fig2.add_subplot(1, 1, 1)



class myThread1(threading.Thread):

    def __init__(self, ser):
        threading.Thread.__init__(self)
        self.ser = ser
        self.N1 = 30

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

        self.thresh_abcd = 30
        self.logfile1 = "abcd_readings.csv"

    def run(self):
        i = 0
        #while i < 240:
       while True:
            ser1 = self.ser.readline()
            time_str = dt.datetime.now().strftime('%H:%M:%S')
            # print ser1

            values_abcd1 = ser1.split('\n')[0].split(',')

            try:
                bc_abcd1 = float(values_abcd1[4])
            except IndexError:
                continue

            print(bc_abcd1)
            self.peak_abcd(time_str,bc_abcd1)
            i += 1

            with open(self.logfile1, "a") as fp:
                fp.write("%s,%s\n"%(time_str,bc_abcd1))


    def peak_abcd(self,time_str, bc_abcd1):

        run_avg1 = sum(self.ynp_abcd1[-self.N1:])/float(self.N1)
        self.ym_abcd1.append(run_avg1)

        self.xs_abcd1.append(time_str)
        self.ys_abcd1.append(bc_abcd1)

        if abs(run_avg1 - bc_abcd1) < self.thresh_abcd:
            # No event
            if self.polluting_abcd[-1] == True:
                # Just stopped polluting
                # Caclulate the statistics
                # Record ending timestamp
                area_abcd = np.trapz(self.yp_abcd1, dx=1)
                self.abcd_areas.append(area_abcd)
                self.xp_abcd1.append(time_str)
                del self.yp_abcd1[:]
                print("Pollution period finished")

            self.polluting_abcd.append(False)
            self.ynp_abcd1.append(bc_abcd1)
        else:
            # Pollution event
            if self.polluting_abcd[-1] == False:
                # Just started polluting
                # Record starting timestamp
                self.xp_abcd1.append(time_str)

            self.polluting_abcd.append(True)
            self.yp_abcd1.append(bc_abcd1)


class myThread2(threading.Thread):
    def __init__(self, ser):
        threading.Thread.__init__(self)
        self.ser = ser
        self.N2 = 30

        # Timestamps for all data
        self.xs_ae16 = []
        # All BC data
        self.ys_ae16 = []
        # No pollution data
        self.ynp_ae16 = [0 for i in range(self.N2)]
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

        self.thresh_ae16 = 30
        self.logfile2 = "ae16_readings.csv"

    def run(self):
        j=0
        while True:
            ser2 = self.ser.readline()
            times = dt.datetime.now().strftime('%H:%M:%S')

            try:
##                print(ser2)
                values_ae16 = ser2.split('\n')[0].split(',')
                bc_ae16 = float(values_ae16[2])

                xs_ae16.append(dt.datetime.now().strftime('%H:%M:%S'))
##                print xs_ae16

                ys_ae16.append(bc_ae16)
##                print ys_ae16

                self.peak_ae16(time_str,bc_ae16)
                j+= 1

            with open(self.logfile2, "a") as fp:
                fp.write("%s,%s\n"%(time_str,bc_ae16))


            except:
                print "Not an expected line"

    def peak_ae16(self,time_str, bc_ae16):

        run_avg2 = sum(self.ynp_ae16[-self.N2:])/float(self.N2)
        self.ym_ae16.append(run_avg2)

        self.xs_ae16.append(time_str)
        self.ys_ae16.append(bc_ae16)

        if abs(run_avg2 - bc_ae16) < self.thresh_ae16:
            # No event
            if self.polluting_ae16[-1] == True:
                # Just stopped polluting
                # Caclulate the statistics
                # Record ending timestamp
                area_ae16 = np.trapz(self.yp_ae16, dx=1)
                self.ae16_areas.append(area_ae16)
                self.xp_ae16.append(time_str)
                del self.yp_ae16[:]
                print("Pollution period finished")

            self.polluting_ae16.append(False)
            self.ynp_ae16.append(bc_ae16)
        else:
            # Pollution event
            if self.polluting_ae16[-1] == False:
                # Just started polluting
                # Record starting timestamp
                self.xp_ae16.append(time_str)

            self.polluting_ae16.append(True)
            self.yp_ae16.append(bc_ae16)

####
##class myThread3(threading.Thread):
##    def __init__(self, ser):
##        threading.Thread.__init__(self)
##        self.ser = ser

##    def run(self):
##        while True:
##            ser4 = self.ser.readline()
##            times = dt.datetime.now().strftime('%H:%M:%S')
##
##            try:
####                print(ser4)
##                values_ae33 = ser4.split('\n')[0].split(',')
##                bc_ae33 = float(values_ae33[9])
##
##                xs_ae33.append(dt.datetime.now().strftime('%H:%M:%S'))
####                print xs_ae33
##
##                ys_ae33.append(bc_ae33)
####                print ys_ae33
##
##            except:
##                print "Not an expected line"
##

class myThread4(threading.Thread):
    def __init__(self, ser):
        threading.Thread.__init__(self)
        self.ser = ser
        self.N4 = 30

        # Timestamps for all data
        self.xs_li820 = []
        # All BC data
        self.ys_li820 = []
        # No pollution data
        self.ynp_li820 = [0 for l in range(self.N4)]
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

        self.thresh_li820 = 30
        self.logfile4 = "li820_readings.csv"


    def run(self):
        l = 0
        while True:
            ser5 = self.ser.readline()
            times = dt.datetime.now().strftime('%H:%M:%S')

            try:
##                print(ser5)
                values_li820 = re.split(r'[<>]', ser5)
                co2_li820 = float(values_li820[14])

                xs_li820.append(dt.datetime.now().strftime('%H:%M:%S'))
##                print xs_li820

                ys_li820.append(co2_li820)
##                print ys_li820
                self.peak_li820(time_str,co2_li820)
                l+= 1

            with open(self.logfile4, "a") as fp:
                fp.write("%s,%s\n"%(time_str,co2_li820))
                
            except:
                print "Not an expected line"

    def peak_li820(self,time_str, co2_li820):

        run_avg4 = sum(self.ynp_li820[-self.N4:])/float(self.N4)
        self.ym_li820.append(run_avg4)

        self.xs_li820.append(time_str)
        self.ys_li820.append(co2_li820)

        if abs(run_avg4 - co2_li820) < self.threshco2_li820:
            # No event
            if self.polluting_li820[-1] == True:
                # Just stopped polluting
                # Caclulate the statistics
                # Record ending timestamp
                area_li820 = np.trapz(self.yp_li820, dx=1)
                self.li820_areas.append(area_li820)
                self.xp_li820.append(time_str)
                del self.yp_li820[:]
                print("Pollution period finished")

            self.polluting_li820.append(False)
            self.ynp_li820.append(co2_li820)
        else:
            # Pollution event
            if self.polluting_li820[-1] == False:
                # Just started polluting
                # Record starting timestamp
                self.xp_li820.append(time_str)

            self.polluting_li820.append(True)
            self.yp_li820.append(co2_li820)


##class myThread6(threading.Thread):
##    def __init__(self, ser):
##        threading.Thread.__init__(self)
##        self.ser = ser
##
##
##
##    def run(self):
##        while True:
##            ser6 = self.ser.readline()
##            times = dt.datetime.now().strftime('%H:%M:%S')
##
##            try:
####                print(ser6)
##                values_li7000 = ser6.split('\n')[0].split('\t')
##                co2_li7000 = float(values_li7000[2])
##
##                xs_li7000.append(dt.datetime.now().strftime('%H:%M:%S'))
####                print xs_li7000
##
##                ys_li7000.append(co2_li7000)
####                print ys_li7000
##
##            except:
##                print "Not an expected line"
##
##
##
##class myThread13(threading.Thread):
##    def __init__(self):
##        threading.Thread.__init__(self)
##
##
##    def run(self):
##
##            ani = animation.FuncAnimation(fig1, animate, fargs =(xs_li820, ys_li820, xs_ae16, ys_ae16, xs_ae33, ys_ae33), interval=1000)
##            plt.show()
##
##class myThread14(threading.Thread):
##    def __init__(self):
##        threading.Thread.__init__(self)
####
####
####    def run(self):
####        calc_em_f()
####
####
####
##def animate(i, xs_li820, ys_li820, xs_ae16, ys_ae16, xs_ae33, ys_ae33):
##
##
##    xs_li820 = xs_li820[-20: ]
##    ys_li820 = ys_li820[-20: ]
##    xs_ae16 = xs_ae16[-20: ]
##    ys_ae16 = ys_ae16[-20: ]
##    xs_ae33 = xs_ae33[-20: ]
##    ys_ae33 = ys_ae33[-20: ]
##
##    ax1.clear()
##    ax1.plot(xs_li820,ys_li820)
##
##    ax2.clear()
##    ax2.plot(xs_ae16,ys_ae16)
##
##    ax3.clear()
##    ax3.plot(xs_ae33,ys_ae33)
##
##    ax2.clear()
##    ax2.plot(xs_ae16,ys_ae16)
##
##
##    # Format plot
##    ax1.tick_params(axis='x', rotation=45)
##    #plt.subplots_adjust(bottom=0.30)
##    ax1.set_title(' ABCD BC concentration over Time')
####    ax1.ylabel('BC conc(ug/m3)')
##    ax2.tick_params(axis='x', rotation=45)
##    ax3.tick_params(axis='x', rotation=45)
####    ax4.tick_params(axis='x', rotation=45)
####    ax5.tick_params(axis='x', rotation=45)
##

thread1=myThread1(serial1)
##thread2=myThread2(serial2)
##thread3=myThread3(serial3)
##thread4=myThread4(serial4)
##thread5=myThread5(serial5)
##thread6=myThread6(serial6)

##thread13=myThread13()


thread1.start()
##thread2.start()
##thread3.start()
##thread4.start()
##thread5.start()
##thread6.start()
##thread13.start()
