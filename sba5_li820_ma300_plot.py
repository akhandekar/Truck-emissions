import os, sys, serial, time, csv, re
import plotly.plotly as py
from plotly.graph_objs import Scatter, Layout, Figure
import plotly.tools as tls

# PLOT info

username = 'rasugrue'
api_key = '1fAAmz0oXrOJngM2jK9w'
stream_tokens = ['9svqiut5n4', 't9mq7ag1jt', '9wtkud7vqx']

py.sign_in(username, api_key)

CO2_SBA5 = Scatter(
    x=[],
    y=[],
    xaxis='x1',
    yaxis='y1',
    name = 'CO2_SBA5',
    stream=dict(
        token=stream_tokens[0],
        maxpoints=120
    )
)

CO2_LI820 = Scatter(
    x=[],
    y=[],
    xaxis='x1', 
    yaxis='y1', 
    name = 'CO2_LI820',
    stream=dict(
        token=stream_tokens[1],
        maxpoints=120
    )
)

BC_MA300 = Scatter(
    x=[],
    y=[],
    name = 'BC_MA300',
    xaxis='x2',
    yaxis='y2',
    stream=dict(
        token=stream_tokens[2],
        maxpoints=120
    )
)

layout = Layout(
    title='Raspberry Pi EF Instruments'
)

#fig = Figure(data=[measured_temp, sample_est], layout=layout)

data = [CO2_SBA5, CO2_LI820, BC_MA300]
fig = tls.make_subplots(rows=3, cols=1)
fig.append_trace(CO2_SBA5, 1, 1)
fig.append_trace(CO2_LI820, 1, 1)
fig.append_trace(BC_MA300, 2, 1)
##fig['data'] = data
fig['layout'].update(title='Raspberry Pi EF Instruments')
fig['layout'].update(showlegend=True)

print py.plot(fig, filename='Raspberry Pi Streaming Box 1 Values')

stream1 = py.Stream(stream_tokens[0])
stream1.open()
stream2 = py.Stream(stream_tokens[1])
stream2.open()
stream3 = py.Stream(stream_tokens[2])
stream3.open()

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

if not os.path.isfile("SBA5_LI820_MA300_readings.csv"):
    with open("SBA5_LI820_MA300_readings.csv", "w") as fp:
        fp.write("timestamp,CO2_SBA5,CO2_LI820,BC_MA300,\n")
##        fp.write("timestamp,BC,time\n")
        
while True:
  
    ser_output0 = ser0.readline()
    ser_output1 = ser1.readline()
    ser_output2 = ser2.readline()
    times = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))


    if ser_output0.count(' ') >= 4 :
##        print(ser_output0)
        values0 = ser_output0.split('\n')[0].split(' ')

        CO2_sba5 = str(values0[3])
##        with open("sensor_readings.csv", "a") as fp:
##             fp.write("%s,%s\n"%(times,CO2_sba5))  
    else:
        CO2_sba5 =  float('nan')
        print("not the expected line\n")



    if ser_output1.count('<') >= 16 :
##        print(ser_output1)
##        values1 = ser_output1.split('\n')[0].split('<')[0].split('>')
        values1 = re.split(r'[<>]', ser_output1)
##        print(values1)
        CO2_LI820 = str(values1[14])
##        print(CO2_LI820)
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

    else:
        BC_ma300 = float('NaN')
        print("not the expected line\n")
##
    with open("SBA5_LI820_MA300_readings.csv", "a") as fp:
        fp.write("%s,%s,%s,%s\n"%(times,CO2_sba5,CO2_LI820,BC_ma300))

##    stream1.write({'x': times, 'y': CO2_SBA5})
    stream1.write(dict(x=times, y=CO2_sba5))
    stream2.write(dict(x=times, y=CO2_LI820))
    stream3.write(dict(x=times, y=BC_ma300))
##    stream2.write({'x': times, 'y': CO2_SBA5})
##    stream3.write({'x': times, 'y': BC_MA300})
	
    # delay between stream posts
    # time.sleep(1)
