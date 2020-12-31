import re
import collections
import os
import string
import ItemId
from datetime import date
import json


class Day():

    def __init__(self, year, month, day):
        # self.day_date = date(year, month, day)
        self.day_date = f'{year}-{month:02d}-{day:02d}'
        """
        self.day_year = year
        self.day_month = month
        self.day_day = day 
        """
        self.day_items = []
    #def addI

class DayItem():
    def __init__(self):
        self.item_subitems = []
    
    def setTime(self, t):
        self.item_time = t
    def setType(self, t):
        self.item_type = t
    def setKey(self, t):
        self.item_key = t
    def setVal(self, t):
        self.item_key_val = t
    def setKeyValParam(self, t):
        self.item_key_val_list = t
    def setTime(self, t):
        self.item_time = t
    def setHour(self, t):
        self.item_hour = t
    def setMin(self, t):
        self.item_min = t  
    def setAmPm(self, t):
        self.item_am_pm = t 

def myStrip(s):
    if s != None:
        return s.strip()
    else:
        return s

def parseKeyValue(s):
    k = re.match("^-(\\w+):(.*)", s)
    key = None
    val = None
    splitVals = None
    valQlist = []
    if k:
        key = k.group(1)
        val = k.group(2)
    else:
        k = re.match("^(\\w+):(.*)", s)
        if k:
            key = k.group(1)
            val = k.group(2)
    if val != None:
        splitVals = re.compile(",|w/").split(val)
        for sp in splitVals:
            sp1 = re.match("(.*)-([^-]*)", sp)
            if sp1:
                x= sp1.group(1)
                y= sp1.group(2)
                valQlist.append((x,y))
    return k, key, val, valQlist

def parseTextItem(s):
    t = re.match("^\(([^)]*)\)", s)
    tm = None
    txt = None
    hour = None
    minute = None
    ap = None
    splitTxt = None
    
    if t:
        txt = t.group(1)
        timeTxt = re.match("^(\d{1,2}[:;]\d{1,2}[aApP][mM]) - (.*)", txt)
        if timeTxt:
            txt = timeTxt.group(2)
            tm, hour, minute, ap = parseTime(timeTxt.group(1))
        splitTxt = re.compile(";").split(txt)
        #for ts in splitTxt: print "<" + ts + ">";             
    return t, txt, splitTxt, hour, minute, ap

def parseTime(s):
    t = re.match("^(\\d{1,2})[:;](\\d{1,2})([aApP][mM])", s)
    if t:
        hour = int(t.group(1))
        minute = int(t.group(2))
        a = re.match("[aA].*", t.group(3))
        if a:
            ap = "AM"
        else:
            ap = "PM"
        return t, hour, minute, ap
    return None, None, None, None
    
def parseDate(s):
    m = re.match("^(\\d+)/(\\d+)/(\\d+)", s)
    if m:
        month = int(m.group(1))
        day = int(m.group(2))
        year = int(m.group(3))
        if year < 99:
            if year < 90:
                year = year + 2000
            else:
                year = year + 1900
        return m, month, day, year
    return None, None, None, None

def splitStringIntoWords(s):
    r = re.compile("[\\W;&();,]+")
    splt = r.split(s)
    return splt
              

def parsefile(inputFile):
    print("parsing file " + inputFile)

    current_item = 0
    current_subitem = 0
    current_hour = 0
    current_min = 0
    current_ampm = 0
    current_day = None
    all_days = []

    f = open(inputFile, 'r')
    tracefile = open("/Users/richk/parse_trace.txt", "w")

    for line in f:
        isDate, month, day, year = parseDate(line)
        if isDate:
            pass
            print("DATE:" + str(month) + " " + str(day) + " " + str(year), file=tracefile)

            current_day = Day(year, month, day)
            all_days.append(current_day)

        else:
            isKeyVal, key, val, splitVals = parseKeyValue(line)
            if isKeyVal:
                if val != "":
                    next_item = DayItem()
                    next_item.setKey(myStrip(key))
                    next_item.setVal(myStrip(val))
                    print("KEY: " + myStrip(key) + " and val: " + myStrip(val), file=tracefile)
                    if len(splitVals) > 0:
                        next_item.setKeyValParam(splitVals)
                        for (x,y) in splitVals:
                            print("KEY Item x: " + str(myStrip(x)) + ", y:" + str(myStrip(y)), file=tracefile)
                    current_day.day_items.append(next_item)

            else:
                isTextItem, txt, splitTxt, hour, minute, ap = parseTextItem(line)
                next_item = DayItem()
                if hour:
                    print("TIME: " + str(hour) + ":" + str(minute) + ap, file=tracefile)
                    next_item.setHour(hour)
                    next_item.setMin(minute)
                    next_item.setAmPm(ap)
                if isTextItem:
                    if txt != "":
                        print("TEXT: " + myStrip(txt))
                        next_item.item_subitems.append(myStrip(txt))
                    if len(splitTxt) > 1:
                        for spl in splitTxt:
                            print("TEXT Item:" + myStrip(spl), file=tracefile)
                    current_day.day_items.append(next_item)
                else:
                    pass
                    if line != "" and line != "\n":
                        print("NO MATCH: <" + line + ">" , file=tracefile)
    return all_days


if __name__ == '__main__':
    print("starting main")
    jfile = "/Users/richk/GoogleDrive/me/sample_journal.txt"
    result = parsefile(jfile)
    for d in result:
        print(json.dumps(d, indent=4, default=lambda x: x.__dict__))
    print("done")

