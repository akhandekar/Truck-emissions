import os, sys, serial, time, csv, re

import math

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

ser3 = serial.Serial (port='XXXXX',
        baudrate=9600,
        timeout = 1,
        bytesize=serial.SEVENBITS)

ser4 = serial.Serial (port='XXXXX',
        baudrate=500000,
        timeout = 1)


BC = 0
ATN = 0
ATNold = 0

if not os.path.isfile("sensor_readings.csv"):
    with open("sensor_readings.csv", "w") as fp:
        fp.write("timestamp,CO2_SBA5,CO2_LI820,BC_MA300,\n")
##        fp.write("timestamp,BC,time\n")
        
while True:
  
    ser_output0 = ser0.readline()
    ser_output1 = ser1.readline()
    ser_output2 = ser2.readline()

    #need to poll CLD60
    ser3.write(b'\x0201RD0\x03\x26') #STX + ASCII + ETX+ + BCC ::: this assumes unit has ID == 1
    ser_output3 = ser3.readline()

    #Read AE51
    ser_output4 = ser4.read(41)


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
        
    with open("sensor_readings.csv", "a") as fp:
        fp.write("%s,%s,%s\n"%(times,CO2_sba5,CO2_LI820))
            
    if ser_output2.count(",") >= 40 :
        print(ser_output2)
        values2 = ser_output2.split('\n')[0].split(',')
        BC_ma300 = float(values2[44])

##
##        with open("sensor_readings.csv", "a") as fp:
##             fp.write("%s,%s\n"%(times,BC_ma300))
    else:
        BC_ma300 = float('NaN')
        print("not the expected line\n")
##
    with open("sensor_readings.csv", "a") as fp:
        fp.write("%s,%s,%s,%s\n"%(times,CO2_sba5,CO2_LI820,BC_ma300))


    try:
        msg = ser_output3.decode('ascii')
        msg = msg.split(',')
        if float(msg[1]) != 0:
            CLD_NOx = float(msg[1])

        ###Insert logging logic here

    except Exception as e:
        print(e)
        pass
    
    try:
        refbyte = ch[8:11]
        refbyte.reverse()
        reference = int.from_bytes(refbyte,byteorder='big')

        sensbyte = ch[11:14]
        sensbyte.reverse()
        sensor = int.from_bytes(sensbyte,byteorder='big')

        flowrate = ch[17]
        if flowrate == 0:
            flowrate = 50   
        
        if sensor == 0:
            #Should insert logic here to reconnect
            BC = 0
            ATN = 0
        
        else:
            ATN = 100 * math.log(reference/sensor)
            deltaATN = ATN -ATNold
            ATNold = ATN
            dB = deltaATN/12.5
            volume = flowrate(1/60)/1000
            BC = dB * 0.07065/volume*1000000

            ###Insert logging logic here
        
        except Exception as e:
            print (e)
            pass

