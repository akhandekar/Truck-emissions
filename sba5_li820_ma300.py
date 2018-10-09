import os, sys, serial, time, csv, re

## ser0 = SBA 5
## ser1 = LI 820
## ser2 = MA 300

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
        baudrate=1000000,
        timeout = 1,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        xonxoff=False)

if not os.path.isfile("sensor_readings.csv"):
    with open("sensor_readings.csv", "w") as fp:
        fp.write("timestamp,CO2_SBA5,CO2_LI820,BC_MA300,\n")
##        fp.write("timestamp,BC,time\n")
        
while True:
  
    ser_output0 = ser0.readline()
    ser_output1 = ser1.readline()
    ser_output2 = ser2.readline()
    times = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))


    if ser_output0.count(' ') >= 4 :
        print(ser_output0)
        values0 = ser_output0.split('\n')[0].split(' ')

        CO2_sba5 = str(values0[3])
##        with open("sensor_readings.csv", "a") as fp:
##             fp.write("%s,%s\n"%(times,CO2_sba5))  
    else:
        CO2_sba5 =  float('nan')
        print("not the expected line\n")


    if ser_output1.count('<') >= 16 :
        print(ser_output1)
##        values1 = ser_output1.split('\n')[0].split('<')[0].split('>')
        values1 = re.split(r'[<>]', ser_output1)
##        print(values1)
        CO2_LI820 = str(values1[14])
        print(CO2_LI820)
##        with open("sensor_readings.csv", "a") as fp:
##             fp.write("%s,%s\n"%(times,CO2_SBA5,CO2_LI820))
    else:
        CO2_LI820 = float('nan')
        print("not the expected line\n")
        
            
    if ser_output2.count(",") >= 40 :
        print(ser_output2)
        values2 = ser_output2.split('\n')[0].split(',')
        if values2[44] == '':
            BC_ma300 = float('NaN')
        else:
            values = float(values2[44])/1000.0
            BC_ma300 = str(values)
        print(BC_ma300)
        ##BC_ma300 = str(values2[44])

##
##        with open("sensor_readings.csv", "a") as fp:
##             fp.write("%s,%s\n"%(times,BC_ma300))
    else:
        BC_ma300 = float('NaN')
        print("not the expected line\n")
##
    with open("sensor_readings.csv", "a") as fp:
        fp.write("%s,%s,%s,%s\n"%(times,CO2_sba5,CO2_LI820,BC_ma300))
