#!/usr/bin/python3

import sys

fileOld = open(sys.argv[1],'r')
fileNew = open(sys.argv[1]+".cvt","w")
heapValue = 0
addHeap = False
heapString = ""
for line in fileOld:
    newLine = line.strip()
    if newLine.strip().endswith("[heap]"):
        columns = newLine.split(" ")
        heapRang = columns[0]
        heapValues = heapRang.split("-")
        heapString += (heapRang+":")
        heapValue += int(heapValues[1],16)-int(heapValues[0],16)
        addHeap = True
    else:
        if addHeap:
            fileNew.write("heap: "+ str(heapValue//1024) + "\n")
            fileNew.write("[heap] "+heapString + "\n")
            addHeap = False
            heapString = ""
            heapValue = 0
        else:
            fileNew.write(newLine + "\n")

fileOld.close()
fileNew.close()
