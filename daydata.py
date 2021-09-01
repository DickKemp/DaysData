
import re
import collections
import os
import string
import ItemId
from datetime import date
import json

BASE_YEAR = 1900

class DayData():
    """[summary]
    """
    def __init__(self, year, month, day):
        """[summary]

        Args:
            year ([type]): [description]
            month ([type]): [description]
            day ([type]): [description]
        """        
        self.date = date(year, month, day)
        self.day_date_str = f'{year}-{month:02d}-{day:02d}'
        self.year = year
        self.month = month
        self.day = day 
        self.items = []
        (self.iso_year, self.iso_week_of_year, self.iso_weekday) = self.date.isocalendar()

    def get_date_str(self):
        return self.day_date_str
    def get_date_int(self):
        return (((self.month * 31) + self.day) * 1000) + (self.year - BASE_YEAR) * 1000000
    def get_day_of_week(self):
        return self.iso_weekday
    def get_day_of_week_str(self):
        if self.iso_weekday == 1:
            return "mon"
        elif self.iso_weekday == 2:
            return "tue"
        elif self.iso_weekday == 3:
            return "wed"
        elif self.iso_weekday == 4:
            return "thu"
        elif self.iso_weekday == 5:
            return "fri"
        elif self.iso_weekday == 6:
            return "sat"
        elif self.iso_weekday == 7:
            return "sun"
            
    def get_week_of_year(self):
        return self.iso_week_of_year
    
    @staticmethod
    def parse_jrnl_data(inf):
        """[summary]

        Args:
            inf ([type]): [description]

        Returns:
            [type]: [description]
        """    
        current_day = None
        all_days = []
        day_item_count = 0
        for line in inf:
            is_date, month, day, year = parseDate(line)
            if is_date:
                current_day = DayData(year, month, day)
                day_item_count = 0
                all_days.append(current_day)
            else:
                line_item = DayItem()
                day_item_count = line_item.set_item_num(day_item_count) + 1
                is_key_val, key, val, splitVals = parseKeyValue(line)
                if is_key_val and val != "":
                    line_item.setType("KEY")
                    line_item.setKey(myStrip(key))
                    line_item.setVal(myStrip(val))

                    if splitVals and len(splitVals) > 0:
                        line_item.setKeyValParam(splitVals)
                        #print
                        for (x,y) in splitVals:
                            #print("({x},{y})")
                            pass
                    current_day.items.append(line_item)
                else:
                    is_text_item, text_items, hour, minute, ap = parseTextItem(line)
                    if is_text_item:
                        line_item.setType("TXT")
                        for txt in text_items:
                            line_item.addText(myStrip(txt))
                        if hour:
                            line_item.setHour(hour)
                            line_item.setMin(minute)
                            line_item.setAmPm(ap)
                            line_item.setTime(f"{hour}:{minute}{ap}")
                        current_day.items.append(line_item)
                    else:
                        """[summary]
                        """
                        if line != "" and line != "\n":
                            line_item.setType("UNK")
                            line_item.addText(line)
                            current_day.items.append(line_item)
        return all_days

class DayItem():
    """[summary]
    """    
    def __init__(self):
        self.text_items = []
        self.time = None
        self.key = None
        self.key_val = None
        self.key_val_list = None

    def setTime(self, t):
        self.time = t
    def setType(self, t):
        self.type = t

    def addText(self, t):
        self.text_items.append(t)

    def set_item_num(self, n):
        self.item_offset = n
        return n

    def setKey(self, t):
        self.key = t
    def setVal(self, t):
        self.key_val = t
    def setKeyValParam(self, t):
        self.key_val_list = t

    def setHour(self, t):
        self.hour = t
    def setMin(self, t):
        self.min = t  
    def setAmPm(self, t):
        self.am_pm = t 

def myStrip(s):
    if s != None:
        return s.strip()
    else:
        return s

def parseKeyValue(s):
    k = re.match("^-(\\w+):(.*)", s)
    k0 = re.match("^-(\\w+):$", s)

    key = None
    val = None
    splitVals = None
    valQlist = []
    if k0:
        key = k.group(1)
        return k0, key, None, None
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
    is_text = re.match("^\(([^)]*)\)", s)
    tm = None
    txt = None
    hour = None
    minute = None
    ap = None
    text_items = None
    
    if is_text:
        txt = is_text.group(1)
        timeTxt = re.match("^(\d{1,2}[:;]\d{1,2}[aApP][mM]) - (.*)", txt)
        if timeTxt:
            txt = timeTxt.group(2)
            tm, hour, minute, ap = parseTime(timeTxt.group(1))
        if ";" in txt:
            text_items = re.compile(";").split(txt)
        else:
            text_items = [txt]

    return is_text, text_items, hour, minute, ap

def parseTime(s):
    is_time = re.match("^(\\d{1,2})[:;](\\d{1,2})([aApP][mM])", s)
    if is_time:
        hour = int(is_time.group(1))
        minute = int(is_time.group(2))
        a = re.match("[aA].*", is_time.group(3))
        if a:
            ap = "AM"
        else:
            ap = "PM"
        return is_time, hour, minute, ap
    return None, None, None, None
    
def parseDate(s):
    is_date = re.match("^(\\d+)/(\\d+)/(\\d+)", s)
    if is_date:
        month = int(is_date.group(1))
        day = int(is_date.group(2))
        year = int(is_date.group(3))
        if year < 99:
            if year < 90:
                year = year + 2000
            else:
                year = year + 1900
        return is_date, month, day, year
    return None, None, None, None

def splitStringIntoWords(s):
    r = re.compile("[\\W;&();,]+")
    splt = r.split(s)
    return splt


if __name__ == '__main__':

    print('nothing')
