#!/usr/bin/python

import sys
from xml.dom.minidom import parse
import xml.dom.minidom as mndom

xmlTree = parse(sys.argv[1])
collection = xmlTree.documentElement

medias = collection.getElementsByTagName("MediaInfo")
for media in medias:
    name = media.getElementsByTagName("media")[0].getAttribute("ref")
    size = media.getElementsByTagName("FileSize")[0].childNodes[0].data;
    width = media.getElementsByTagName("Width")[0].childNodes[0].data;
    height = media.getElementsByTagName("Height")[0].childNodes[0].data;
    print("%s  size: %d MB  Width:%s  Height:%s" % (name, (int(size)/(1024*1024)), width, height))


