import os, sys, serial, time, csv
import plotly.plotly as py
from plotly.graph_objs import Scatter, Layout, Figure
import plotly.tools as tls

# PLOT info

username = 'rasugrue'
api_key = '1fAAmz0oXrOJngM2jK9w'
stream_tokens = ['tf2mzfghp3', '26whq592pa', '516hdmb7d9']

py.sign_in(username, api_key)

CO2_V = Scatter(
    x=[],
    y=[],
    name = 'CO2_V',
    xaxis='x1',
    yaxis='y1',
    stream=dict(
        token=stream_tokens[0],
        maxpoints=120
    )
)

BC_AE16 = Scatter(
    x=[],
    y=[],
    xaxis='x2',
    yaxis='y2',
    name = 'BC_AE16',
    stream=dict(
        token=stream_tokens[1],
        maxpoints=120
    )
)

NO2_CAPS = Scatter(
    x=[],
    y=[],
    name = 'NO2_CAPS',
    xaxis='x3',
    yaxis='y3',
    stream=dict(
        token=stream_tokens[2],
        maxpoints=120
    )
)

layout = Layout(
    title='Raspberry Pi Streaming Boxes'
)

#fig = Figure(data=[measured_temp, sample_est], layout=layout)

data = [CO2_V, BC_AE16, NO2_CAPS]
fig = tls.make_subplots(rows=3, cols=1)
fig.append_trace(CO2_V, 1, 1)
fig.append_trace(BC_AE16, 2, 1)
fig.append_trace(NO2_CAPS, 3, 1)
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

if not os.path.isfile("VCO2_AE16_CAPS_readings.csv"):
    with open("VCO2_AE16_CAPS_readings.csv", "w") as fp:
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

    with open("VCO2_AE16_CAPS_readings.csv", "a") as fp:
             fp.write("%s,%s,%s,%s\n"%(times,V_CO2,BC_ae16,NO2_CAPS))

##    stream1.write({'x': times, 'y': CO2_V})
    stream1.write(dict(x=times, y=CO2_V))
    stream2.write(dict(x=times, y=BC_AE16))
    stream3.write(dict(x=times, y=NO2_CAPS))
##    stream2.write({'x': times, 'y': BC_AE16})
##    stream3.write({'x': times, 'y': NO2_CAPS})
	
    # delay between stream posts
    # time.sleep(1)
