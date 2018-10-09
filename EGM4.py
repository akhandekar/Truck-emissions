import os, sys, serial, time, csv
import os, sys, serial, time, csv
import plotly.plotly as py
from plotly.graph_objs import Scatter, Layout, Figure
import plotly.tools as tls

# PLOT info

username = 'rasugrue'
api_key = '1fAAmz0oXrOJngM2jK9w'
stream_tokens = ['w5vx0wi6kz']

py.sign_in(username, api_key)

CO2_EGM4 = Scatter(
    x=[],
    y=[],
    name = "CO2_EGM4",
    xaxis='x1',
    yaxis='y1',
    stream=dict(
        token=stream_tokens[0],
        maxpoints=120
    )
)

layout = Layout(
    title='Raspberry Pi EF Instruments'
)

#fig = Figure(data=[measured_temp, sample_est], layout=layout)

data = [CO2_EGM4]
fig = tls.make_subplots(rows=1, cols=2)
fig.append_trace(CO2_EGM4, 1, 1)

##fig['data'] = data
fig['layout'].update(title='Raspberry Pi EF Instruments')
fig['layout'].update(showlegend=True)

print py.plot(fig, filename='Raspberry Pi Streaming Box 1 Values')

stream1 = py.Stream(stream_tokens[0])
stream1.open()

## ser0 = EGM 4


ser0 = serial.Serial (port='/dev/ttyUSB0',
        baudrate=9600,
        timeout = 1,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        xonxoff=False)


if not os.path.isfile("EGM4_readings.csv"):
    with open("EGM4_readings.csv", "w") as fp:
        fp.write("timestamp,CO2_EGM4\n")
##        fp.write("timestamp,BC,time\n")

ser0.write("R\r\n")
response = ser0.readline()
print response

while True:
  
    ser_output0 = ser0.readline()
    times = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))


    if len(ser_output0) >= 20 :
        print(ser_output0)
        values0 = int(ser_output0[16:20])
        CO2_EGM4 = float(values0)

##        with open("sensor_readings.csv", "a") as fp:
##             fp.write("%s,%s\n"%(times,CO2_V))
    else:
        CO2_EGM4 = float('NaN')
        print("not the expected line\n")


    with open("EGM4_readings.csv", "a") as fp:
             fp.write("%s,%s\n"%(times,CO2_EGM4))

##    stream1.write({'x': times, 'y': CO2_EGM4})
    stream1.write(dict(x=times, y=CO2_EGM4))

    # delay between stream posts
    # time.sleep(1)
