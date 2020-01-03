#!/usr/bin/python3

import sys
from openpyxl import Workbook
import datetime

from openpyxl.chart import (LineChart, Reference,)
from openpyxl.chart.axis import DateAxis

def draw(ws, srow, erow, scol, ecol, position):
    data1= Reference(ws,min_col=scol, min_row=srow, max_col=ecol, max_row=erow)

    c1 = LineChart()
    c1.title = "Time interval (" + str(srow) + " - " + str(erow) +")"
    c1.style = 13
    c1.y_axis.majorGridlines = None
    c1.y_axis.title = "Delta (ms)"
    c1.x_axis.title = "Timestamp"
    
    c1.add_data(data1, titles_from_data=True)
    
    s1 = c1.series[0]
    s1.graphicalProperties.line.solidFill = "FF0000"
    
    s2 = c1.series[1]
    s2.graphicalProperties.line.solidFill = "990000"
    s2.smooth = True
    
    ws.add_chart(c1, position)

wb = Workbook()
ws = wb.active
ws.title = "Timestamp Statistics"
file=open(sys.argv[1])

title = ["Timestamp(ms)", "Timestamp(Str)", "Received Time(ms)", "Received Time(Str)",  "Delta Timestamp", "Rtime-Timestamp"]
data=[]
data.append(title)

for line in file:
    tmpline=line.split()
    tmpline[4] = int(tmpline[4])
    tmpline[5] = int(tmpline[5])
    data.append(tmpline)
for row in data:
    ws.append(row)


draw(ws,1,len(data),5,6, "A"+str(len(data)+5))
if len(sys.argv) > 2:
    i = 2
    while i<len(sys.argv):
        srow=sys.argv[i]
        if '-' in srow:
            selist=srow.split('-')
            st=int(selist[0])
            ed=int(selist[1])
        else:
            st=int(srow)
            ed=len(data)
        draw(ws,st,ed,5,6,"A"+str(len(data)+25*(i-1)))
        i=i+1

#data1= Reference(ws,min_col=5, min_row=1, max_col=6, max_row=len(data))
#
#c1 = LineChart()
#c1.title = "Time interval"
#c1.style = 13
#c1.y_axis.majorGridlines = None
#c1.y_axis.title = "Delta (ms)"
#c1.x_axis.title = "Timestamp"
#
#c1.add_data(data1, titles_from_data=True)
#
#s1 = c1.series[0]
#s1.graphicalProperties.line.solidFill = "FF0000"
#
#s2 = c1.series[1]
#s2.graphicalProperties.line.solidFill = "990000"
#s2.smooth = True
#
#ws.add_chart(c1, "A"+str(len(data)+5))
#
wb.save(sys.argv[1]+".telemetry.xlsx")
file.close()
