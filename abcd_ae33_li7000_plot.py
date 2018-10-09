import os, sys, serial, time, csv
import plotly.plotly as py
from plotly.graph_objs import Scatter, Layout, Figure
import plotly.tools as tls

# PLOT info

username = 'rasugrue'
api_key = '1fAAmz0oXrOJngM2jK9w'
stream_tokens = ['u0q5bvimts', '9xpm7e5leq', 'pu6f4na0l9']

py.sign_in(username, api_key)

CO2_LI7000 = Scatter(
    x=[],
    y=[],
    name = "CO2_LI7000",
    xaxis='x1',
    yaxis='y1',
    stream=dict(
        token=stream_tokens[0],
        maxpoints=20
    )
)

BC_ABCD = Scatter(
    x=[],
    y=[],
    xaxis='x2',
    yaxis='y2',
    name = "BC_ABCD",
    stream=dict(
        token=stream_tokens[1],
        maxpoints=200
    )
)

BC_AE33 = Scatter(
    x=[],
    y=[],
    name = "BC_AE33",
    xaxis='x2',
    yaxis='y2',
    stream=dict(
        token=stream_tokens[2],
        maxpoints=200
    )
)

layout = Layout(
    title='Raspberry Pi Streaming Boxes'
)

#fig = Figure(data=[measured_temp, sample_est], layout=layout)

data = [CO2_LI7000, BC_ABCD, BC_AE33]
fig = tls.make_subplots(rows=1, cols=2)
fig.append_trace(CO2_LI7000, 1, 1)
fig.append_trace(BC_ABCD, 1, 2)
fig.append_trace(BC_AE33, 1, 2)
##fig['data'] = data
fig['layout'].update(title='Raspberry Pi Streaming Boxes')
fig['layout'].update(showlegend=True)

print py.plot(fig, filename='Raspberry Pi Streaming Box 1 Values')

stream1 = py.Stream(stream_tokens[0])
stream1.open()
stream2 = py.Stream(stream_tokens[1])
stream2.open()
stream3 = py.Stream(stream_tokens[2])
stream3.open()


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

if not os.path.isfile("sensor_readings.csv"):
    with open("sensor_readings.csv", "w") as fp:
        fp.write("timestamp,CO2_LI7000,BC_ABCD,ATN_ABCD,BC_AE33,\n")
##        fp.write("timestamp,BC,time\n")
        
while True:
  
    ser_output0 = ser0.readline()
    ser_output1 = ser1.readline()
    ser_output2 = ser2.readline()
    times = time.strftime("%Y-%m-%d%H:%M:%S", time.localtime(time.time()))

    if ser_output0.count('\t') >= 8 :
        print(ser_output0)
        values2 = ser_output0.split('\n')[0].split('\t')
        CO2_li7000 = str(values2[7])

##        with open("sensor_readings.csv", "a") as fp:
##             fp.write("%s,%s\n"%(times,CO2_li7000))
    else:
        CO2_li7000 = float('NaN')
        print("not the expected line\n")

    if ser_output1.count(',') >= 8 :
        print(ser_output1)
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

##    with open("sensor_readings.csv", "a") as fp:
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

##    stream1.write({'x': times, 'y': CO2_li7000})
    stream1.write(dict(x=times, y=CO2_li7000))
    stream2.write(dict(x=times, y=BC_ABCD))
    stream3.write(dict(x=times, y=BC_AE33))
##    stream2.write({'x': times, 'y': BC_ABCD})
##    stream3.write({'x': times, 'y': BC_AE33})
	
    # delay between stream posts
    # time.sleep(1)
