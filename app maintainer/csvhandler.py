# -*- coding: utf-8 -*-

from operator import itemgetter
import csv
import json

if __name__ == "__main__":
    filename = 'WDJApps.csv'
    fp = open(filename,'r')
    table = []
    lines = fp.readlines()
    fp.close()
    for line in lines:
        row = line.split(',')
        if row[2] == 'rank':
            continue

        row[2] = int(row[2])
        table.append(row)      # table = [[package_name,category,rank],...]
    
    table = sorted(table, key=itemgetter(2))
    result = []
    for item in table:
        apk = item[0]+'.apk'
        result.append(apk)

    fp = open('WDJRanked.txt','w')
    json.dump(result, fp)