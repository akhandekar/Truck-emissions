import os, sys, serial, time, csv
import matplotlib
matplotlib.use("tkAgg")
import matplotlib.pyplot as plt
import numpy as np


## ser0 = Li 7000
## ser1 = ABCD
## ser2 = AE 33

ser0 = serial.Serial (port='/dev/ttyUSB0',
        baudrate=9600,
        timeout = 1,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        xonxoff=False)

ser1 = serial.Serial (port='/dev/ttyUSB1',
        baudrate=57600,
        timeout = 1,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        xonxoff=False)

ser2 = serial.Serial (port='/dev/ttyUSB2',
        baudrate=9600,
        timeout = 1,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        xonxoff=False)

plot_window = 20
y_var = np.array(np.zeros([plot_window]))

plt.ion()
fig, ax = plt.subplots()
line, = ax.plot(y_var)


if not os.path.isfile("sensor_readings.csv"):
    with open("sensor_readings.csv", "w") as fp:
        fp.write("timestamp,CO2_LI7000,BC_ABCD,ATN_ABCD,BC_AE33,\n")
##        fp.write("timestamp,BC,time\n")
        
while True:
  
    ser_output0 = ser0.readline()
    ser_output1 = ser1.readline()
    ser_output2 = ser2.readline()
    times = time.strftime("%Y-%m-%d%H:%M:%S", time.localtime(time.time()))

    if ser_output0.count('\t') >= 5 :
        ## print(ser_output0)
        values2 = ser_output0.split('\n')[0].split('\t')
        CO2_li7000 = str(values2[7])

##        with open("sensor_readings.csv", "a") as fp:
##             fp.write("%s,%s\n"%(times,CO2_li7000))
    else:
        CO2_li7000 = float('NaN')
        print("not the expected line\n")

    if ser_output1.count(',') >= 8 :
        ## print(ser_output1)
        values1 = ser_output1.split('\n')[0].split(',')
##        epoch_time = int(values[0])
##        time_string = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(epoch_time))
##        Vref = float(values1[1])
##        Vsig = float(values1[2])
        ATN_ABCD = float(values1[3])
        BC_ABCD = float(values1[4])
##        RH = float(values1[5])
##        Temp = float(values1[6])
##        FR = float(values1[7])
##        Batt = float(values1[8])

##        with open("sensor_readings.csv", "a") as fp:
##             fp.write("%s,%s,%s\n"%(times,ATN_ABCD, BC_ABCD))
        ## print(ATN_ABCD)
        ## print(BC_ABCD)
    else:
        ATN_ABCD = float('NaN')
        BC_ABCD = float('NaN')
        print("not the expected line\n")

##    with open("sensor_readings.csv", "Sa") as fp:
##         fp.write("%s,%s,%s,%s\n"%(times,CO2_li7000,BC_ABCD,ATN_ABCD))


    if ser_output2.count(",") >= 10 :
        ## print(ser_output2)
        values0 = ser_output2.split('\n')[0].split(',')
        BC_ae33 = float(values2[9])

##        with open("sensor_readings.csv", "a") as fp:
##             fp.write("%s,%s\n"%(times,BC_ae33))
    else:
        BC_AE33 = float('NaN')
        print("not the expected line\n")


    with open("sensor_readings.csv", "a") as fp:
        fp.write("%s,%s,%s,%s,%s\n"%(times,CO2_li7000,BC_ABCD,ATN_ABCD,BC_AE33))

    y_var = np.append(y_var, CO2_li7000)
    y_var = y_var[1:plot_window]
    line.set_ydata(y_var)
    ## ax.relim()
##    ax.autoscale_view()
    fig.canvas.draw()
##    fig.canvas.flush_events()
    
