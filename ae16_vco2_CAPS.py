import os, sys, serial, time, csv

## ser0 = V_CO2
## ser1 = AE 16
## ser2 = CAPS NO2


ser0 = serial.Serial (port='/dev/ttyUSB0',
        baudrate=19200,
        timeout = 1,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        xonxoff=False)

ser1 = serial.Serial (port='/dev/ttyUSB1',
        baudrate=9600,
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

if not os.path.isfile("sensor_readings.csv"):
    with open("sensor_readings.csv", "w") as fp:
        fp.write("timestamp,V_CO2,BC_AE16,NO2_CAPS\n")
##        fp.write("timestamp,BC,time\n")

ser0.write("R\r\n")
response = ser0.readline()
print response

while True:
  
    ser_output0 = ser0.readline()
    ser_output1 = ser1.readline()
    ser_output2 = ser2.readline()
    times = time.strftime("%Y-%m-%d%H:%M:%S", time.localtime(time.time()))


    if ser_output0.count('\t') >= 1 :
        print(ser_output0)
        values0 = ser_output0.split('\n')[0].split('\t')
        V_CO2 = float(values0[0])

##        with open("sensor_readings.csv", "a") as fp:
##             fp.write("%s,%s\n"%(times,CO2_V))
    else:
        V_CO2 = float('NaN')
        print("not the expected line\n")

    if ser_output1.count(",") >= 0 :
        print(ser_output1)
        values1 = ser_output1.split('\n')[0].split(',')
        BC_ae16 = str(values1[0])

##        with open("sensor_readings.csv", "a") as fp:
##             fp.write("%s,%s\n"%(times,BC_ae16))
    else:
        BC_ae16 = float('NaN')
        print("not the expected line\n")
    
    if ser_output2.count(',') >= 5 :
        print(ser_output2)
        values2 = ser_output2.split('\n')[0].split(',')
        NO2_CAPS = str(values2[1])
        print(NO2_CAPS)

##        with open("sensor_readings.csv", "a") as fp:
##             fp.write("%s,%s\n"%(times,CO2_li7000))
    else:
        NO2_CAPS = float('NaN')
        print("not the expected line\n")

    with open("sensor_readings.csv", "a") as fp:
             fp.write("%s,%s,%s,%s\n"%(times,V_CO2,BC_ae16,NO2_CAPS))

