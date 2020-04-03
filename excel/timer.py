#!/usr/bin/python3

import sys
from openpyxl import Workbook
import datetime

from openpyxl.chart import (LineChart, BarChart, PieChart, Reference,)
from openpyxl.chart.axis import DateAxis
from openpyxl.chart.series import DataPoint

def drawLineChart(ws, srow, erow, scol, ecol, position, onlyone=False):
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
    
    if not onlyone:
        s2 = c1.series[1]
        s2.graphicalProperties.line.solidFill = "990000"
        s2.smooth = True
    
    ws.add_chart(c1, position)

def drawBarChart(ws, srow, erow, scol, ecol, position):

    c1 = BarChart()
    c1.title = "Interval Statistics"
    c1.type = 'col'
    c1.style = 10
    c1.y_axis.majorGridlines = None
    c1.y_axis.title = "Number"
    c1.x_axis.title = "Timestame Delta Range"
    
    data1= Reference(ws,min_col=scol, min_row=srow, max_col=ecol, max_row=erow)
    cats = Reference(ws,min_col=1,min_row=srow+1,max_row=erow)
    c1.add_data(data1, titles_from_data=True)
    c1.set_categories(cats)
    c1.shape=4
    ws.add_chart(c1, position)

def drawPieChart(ws, srow, erow, scol, ecol, position):

    c1 = PieChart()
    
    data1 = Reference(ws,min_col=scol, min_row=srow, max_col=ecol, max_row=erow)
    labels = Reference(ws,min_col=1,min_row=srow+1,max_row=erow)
    c1.add_data(data1, titles_from_data=True)
    c1.set_categories(labels)
    c1.title = "Percent by absolute range"

    slice = DataPoint(idx=0, explosion=20)
    c1.series[0].data_points = [slice]

    ws.add_chart(c1, position)

wb = Workbook()
ws = wb.active
ws.title = "Timestamp Statistics"
file=open(sys.argv[1])
ws1 = wb.create_sheet("statistics")
ws2 = wb.create_sheet("statistics %")

sampleInterval=6000

title = ["Timestamp(ms)", "Timestamp(Str)", "Received Time(ms)", "Received Time(Str)",  "Delta Timestamp", "Rtime-Timestamp", "Timestamp Offset"]

data=[]
data.append(title)

stats={}
stats1={}

n=0
base=0
for line in file:
    tmpline=line.split()
    if n==0:
        base = int(tmpline[0])
        tmpline.append(n)
    else:
        tmpline.append(int(tmpline[0])-(base+(n*sampleInterval)))
    tmpline[4] = int(tmpline[4])
    tmpline[5] = abs(int(tmpline[5]))
    data.append(tmpline)
    i = tmpline[4]//500
    if stats.get((i+1)*500):
        stats[(i+1)*500] += 1
    else:
        stats[(i+1)*500] = 1
    if n>0:
        j = abs(tmpline[4]-sampleInterval)//500
        if stats1.get((j+1)*500):
            stats1[(j+1)*500] += 1
        else:
            stats1[(j+1)*500] = 1
    n += 1

for row in data:
    ws.append(row)

ws1.append(['Rang','Total'])

bardata=[]
for key in sorted(stats.keys()):
    tmpbarline=[]
    tmpbarline.append(key)
    tmpbarline.append(stats.get(key))
    bardata.append(tmpbarline)
    ws1.append(tmpbarline)
drawBarChart(ws1,1,len(bardata)+1,2,2,"D1")

ws2.append(['Abs Rang', 'Number', 'Percent'])
piedata=[]
for key in sorted(stats1.keys()):
    tmppieline=[]
    tmppieline.append(key)
    tmppieline.append(stats1.get(key))
    tmppieline.append(stats1.get(key)*100//n)
    piedata.append(tmppieline)
    ws2.append(tmppieline)
drawPieChart(ws2,1,len(piedata)+1,3,3,"E1")


drawLineChart(ws,1,len(data),5,6, "A"+str(len(data)+5))
drawLineChart(ws,1,len(data),7,7, "A"+str(len(data)+25),True)
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
        drawLineChart(ws,st,ed,5,6,"A"+str(len(data)+25*i))
        i=i+1

wb.save(sys.argv[1]+".telemetry.xlsx")
file.close()
