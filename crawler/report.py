# coding=utf-8

import os
import sys
import time
import json
import codecs
import requests
import threading
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from datetime import timedelta
import matplotlib.pyplot as plt


item = 0
ec_list = []
prev_ec = []
dir = sys.argv[1]
address = sys.argv[2]
rpd = dir + '/report'
#emmajar = "~/togithub/emma.jar"
emmajar = sys.argv[3]
#url = "http://23.105.211.254:5000/uploadc"
url = 'http://' + address + '/uploadc'
record_time = timedelta(seconds=0)
timespan = timedelta(seconds=10)
os.system('rm -r ' + dir + '/report')
os.system("adb shell rm /mnt/sdcard/coverage.ec")
os.system("mkdir " + rpd)

def fetch_data(html):
    soup = BeautifulSoup(html)
    t = soup.find_all('table')
    trs = t[-2].findAll('tr')
    l = []
    for i in trs:
        tds = i.find_all('td')
        if (len(tds) == 5):
            name = tds[0].getText()
            data = tds[1:]
            tmp = []
            if ("EmmaInstrument" not in name) and name !="name":
                for i in data:
                    div = i.getText().split(u'\xa0(')[1][:-1].split('/')
                    tmp.append([float(div[0]), float(div[1])])
                l.append(tmp)
    sumtuple = []
    for ftuple in l:
        if len(sumtuple) == 0:
            sumtuple = ftuple
        else:
            for i in range(4):
                sumtuple[i][0] = sumtuple[i][0] + ftuple[i][0]
                sumtuple[i][1] = sumtuple[i][1] + ftuple[i][1]
    sumcoverage = [t[0]/t[1] for t in sumtuple]
    return sumcoverage


def animate():
    global item
    global record_time
    global timespan
    html_file = './html_report/all_' + str(item) + '.html'
    ll = []
    if os.path.exists(html_file):
        a = codecs.open(html_file, 'r', 'iso-8859-1').read()
        ll = [fetch_data(a)]
    else:
        print("No all_" + str(item) + '.html????')
    if item == 0:
        f = open('coverage.csv','w+')
        f.write('order,time,class,method,block,line\n')
    else:
        f = open('coverage.csv', 'a+')
    for element in ll:
        f.write(str(item) + ',' + str(record_time) + ',' + ','.join([str(round(i,3)) for i in element]) + '\n')
    record_time = record_time + timespan
    f.close()

    narray = pd.read_csv('coverage.csv')
    timestamp = narray['time'].values.tolist()
    cl = narray['class'].values.tolist()
    cl = [round(i, 3) for i in cl]
    method = narray['method'].values.tolist()
    method = [round(i, 3) for i in method]
    block = narray['block'].values.tolist()
    block = [round(i, 3) for i in block]
    lines = narray['line'].values.tolist()
    lines = [round(i,3) for i in lines]
    transp = {}

    transp['timestamp'] = timestamp
    transp['class'] = cl
    transp['method'] = method
    transp['block'] = block
    transp['lines'] = lines
    try:
        r = requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(transp))
    except requests.exceptions.RequestException as e:
        print(e)
        print("fail upload coverage")
    
    narray = narray.as_matrix()
    ll = narray[:,2:]
    fig, axarr = plt.subplots(2,2)
    # add a big axes, hide frame
    fig.add_subplot(111, frameon=False)
    # hide tick and tick label of the big axes
    plt.tick_params(labelcolor='none', top='off', bottom='off',left='off',right='off')
    plt.xlabel('time(min)')
    plt.ylabel('coverage rate')

    axarr[0,0].plot(ll[:,0])
    axarr[0,0].set_title('class')
    
    axarr[0,1].plot(ll[:,1])
    axarr[0,1].set_title('method')
    
    axarr[1,0].plot(ll[:,2])
    axarr[1,0].set_title('block')
    
    axarr[1,1].plot(ll[:,3])
    axarr[1,1].set_title('line')

    tick = int(len(ll) / 18) * 6
    if tick == 0:
        tick = 3
    plt.setp(axarr, xticks=[x for x in range(len(ll)) if x % tick == 0], xticklabels=[x/6 for x in range(len(ll)) if x % tick == 0])
    plt.setp([a.get_xticklabels() for a in axarr[0,:]], visible=False)
    plt.savefig("./html_report/coverage.png")
    plt.close(fig)


def get_coverage():
    global item
    os.system("adb shell am broadcast -a edu.gatech.m3.emma.COLLECT_COVERAGE")
    os.system("adb pull /mnt/sdcard/coverage.ec " + rpd + '/' + str(item) + '.ec')
    merge_string = rpd + '/' + str(item) + '.ec,' + rpd + '/' + 'merge_report/all_' + str(item-1) + '.ec'
    html_string = dir + '/coverage.em,'+ rpd + '/merge_report/all_'+ str(item) + '.ec'
    html_dir = rpd + '/html_report/'
    if item == 0:
        if not os.path.isdir(rpd + '/merge_report'):
            os.mkdir(rpd + '/merge_report')
        else:
            os.system("rm " + rpd + '/merge_report/*.ec')
        os.system('cp ' + rpd + '/0.ec ' + rpd + '/merge_report/all_0.ec' )
        os.system('rm ' + rpd + '/0.ec')
        os.system('java -cp ' + emmajar + ' emma report -r html -in ' + html_string + ' -Dreport.html.out.file=' + html_dir + 'all_' + str(item) + '.html')
    else:
        if not os.path.isfile(rpd + '/' + str(item) +'.ec'):
            return
        os.system('java -cp ' + emmajar + ' emma merge -input ' + merge_string + ' -out ' + rpd + '/merge_report/all_' + str(item) + '.ec')
        # merge完上一个ec后直接删除
        os.system('rm ' + rpd + '/' + str(item) + '.ec')
        # 以html格式产生报告
        os.system('java -cp ' + emmajar + ' emma report -r html -in ' + html_string + ' -Dreport.html.out.file=' + html_dir + 'all_' + str(item) + '.html')

    os.chdir(rpd)
    animate()
    os.chdir('../../../')
    item += 1

if __name__ == "__main__":
    while True:
        get_coverage()
        time.sleep(10)