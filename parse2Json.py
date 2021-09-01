
from daydata import DayData

import re
import collections
import os
import string
import ItemId
from datetime import date
import json


def gen_tags(day: DayData):
    tags = []
    if day.year % 2 != 0:
        tags.append('#oddYear')
    if day.month % 2 != 0:
        tags.append('#oddMonth')
    if day.get_day_of_week() % 2 != 0:
        tags.append('#oddDayOfWeek')
    if day.day % 2 != 0:
        tags.append('#oddDay')
    return tags
    


def expand_day_to_items(day: DayData):
    indx = 0
    current_date_str = day.get_date_str()
    current_date_int = day.get_date_int()
    tags = gen_tags(day)
    for item in day.items:
        day_item = dict()
        day_item["ID"] = f'{current_date_str}_{str(indx)}'
        day_item["Date"] = current_date_str
        day_item["Seq"] = indx
        day_item["TotalSeq"] = current_date_int + indx
        day_item["Year"] = day.year
        day_item["Month"] = day.month
        day_item["Day"] = day.day
        day_item["DayOfWeek"] = day.get_day_of_week()
        day_item["DayOfWeekName"] = day.get_day_of_week_str()
        day_item["DayOfMonth"] = day.day
        day_item["WeekOfYear"] = day.get_week_of_year()
        if tags:
            day_item["Tags"] = tags

        if item.type == "TXT":
            day_item["Text"] = ". ".join(item.text_items)            
            if item.time:            
                day_item['Time'] = item.time
        
        if item.type == "KEY":
            if item.key == "B":
                day_item["Breakfast"] = item.key_val if item.key_val else ""
            elif item.key == "L":
                day_item["Lunch"] = item.key_val if item.key_val else ""
            elif item.key == "D":
                day_item["Dinner"] = item.key_val if item.key_val else ""
            elif item.key == "S":
                day_item["Snack"] = item.key_val if item.key_val else ""
            else:
                day_item["Key"] = item.key
                if item.key_val:
                    day_item["KeyValue"] = item.key_val
                if item.key_val_list:
                    day_item["KeyValueList"] = item.key_val_list

        else:
            continue
        yield day_item
        indx = indx + 1


if __name__ == '__main__':

    def journal_to_json(infile, outfile):
        jfile = infile
        with open(jfile, "r") as inf:
            day_list = DayData.parse_jrnl_data(inf)

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

    infile = "/Users/richk/GoogleDrive/me/ALL.txt"
    outfile = "/Users/richk/GoogleDrive/me/ALL2Y.json"
    journal_to_json(infile, outfile)
