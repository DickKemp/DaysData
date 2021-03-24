import re
import collections
import os
import string
import ItemId
from datetime import date
import json


class Day():
    """[summary]
    """
    def __init__(self, year, month, day):
        """[summary]

        Args:
            year ([type]): [description]
            month ([type]): [description]
            day ([type]): [description]
        """        
        self.day_date_str = f'{year}-{month:02d}-{day:02d}'
        self.year = year
        self.month = month
        self.day = day 
        self.items = []

    def get_date_str(self):
        return self.day_date_str

class DayItem():
    """[summary]
    """    
    def __init__(self):
        self.text_items = []
        self.time = None

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
            current_day = Day(year, month, day)
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
                    for (x,y) in splitVals:
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

def expand_day_to_items(day):
    indx = 0
    current_date_str = day.get_date_str()
    for item in day.items:
        day_item = dict()
        day_item["ID"] = f'{current_date_str}_{str(indx)}'
        day_item["Date"] = current_date_str
        day_item["Seq"] = indx
        day_item["Text"] = ""
        day_item["Time"] = ""
        day_item["Key"] = ""
        day_item["KeyValue"] = ""
        day_item["Breakfast"] = ""
        day_item["Lunch"] = ""
        day_item["Dinner"] = ""
        day_item["Snack"] = ""
        if item.type == "TXT":
            day_item["Text"] = ". ".join(item.text_items)            
            day_item['Time'] = item.time if item.time else ""
        elif item.type == "KEY":
            day_item["Key"] = item.key if item.key else ""
            if day_item["Key"] == "B":
                day_item["Breakfast"] = day_item["Breakfast"] + " " + item.key_val if item.key_val else ""
            elif day_item["Key"] == "L":
                day_item["Lunch"] = day_item["Lunch"] + " " + item.key_val if item.key_val else ""
            elif day_item["Key"] == "D":
                day_item["Dinner"] = day_item["Dinner"] + " " + item.key_val if item.key_val else ""
            elif day_item["Key"] == "S":
                day_item["Snack"] = day_item["Snack"] + " " + item.key_val if item.key_val else ""
            else:
                day_item["KeyValue"] = item.key_val if item.key_val else ""
        else:
            continue
        yield day_item
        indx = indx + 1

def journal_to_json(infile, outfile):
    jfile = infile
    with open(jfile, "r") as inf:
        day_list = parse_jrnl_data(inf)

    with open(outfile, "w") as fd:
        print('[', file=fd)
        print_delimeter = False
        for day in day_list:
            for dayitem in expand_day_to_items(day):
                if print_delimeter:
                    print(',', file=fd)
                else:
                    print_delimeter = True
                print(json.dumps(dayitem, indent=4, default=lambda x: x.__dict__), file=fd)
        print(']', file=fd)


if __name__ == '__main__':

    infile = "/Users/richk/GoogleDrive/me/ALL.txt"
    outfile = "/Users/richk/GoogleDrive/me/ALL2.json"
    journal_to_json(infile, outfile)

    """
    jfile = "/Users/richk/GoogleDrive/me/sample_journal.txt"
    with open(jfile, "r") as inf:
        day_list = parse_jrnl_data(inf)

    with open("/Users/richk/GoogleDrive/me/sample_journal_days.json", "w") as fd:
        for day in day_list:
            print(json.dumps(day, indent=4, default=lambda x: x.__dict__), file=fd)

    with open("/Users/richk/GoogleDrive/me/sample_journal_items.json", "w") as fd:
        print('[', file=fd)
        print_delimeter = False
        for day in day_list:
            for dayitem in expand_day_to_items(day):
                if print_delimeter:
                    print(',', file=fd)
                else:
                    print_delimeter = True
                print(json.dumps(dayitem, indent=4, default=lambda x: x.__dict__), file=fd)
        print(']', file=fd)
    """