#!/usr/bin/env python3
import time

def log(stringarg):
    now = time.localtime()
    year = str(now.tm_year)
    month = str(now.tm_mon)
    day = str(now.tm_mday)
    hour = str(now.tm_hour)
    min = str(now.tm_min)
    sec = str(now.tm_sec)
    timeStr = year + "/" + month + "/" + day + "_" + hour + ":" + min + ":" + sec
    printstr = str(timeStr) + " : " + stringarg
    print(printstr)