# coding=utf-8

import os
import re
import hashlib
import datetime
import codecs
from bs4 import BeautifulSoup
from settings import apk_dir
from settings import emma_dir

class App():
    def __init__(self, apk, serial, suit):
        self.path = apk_dir
        #count emma file
        self.item = 0
        self.apkpath = self.path + '/' + apk
        self.package = self.getPackage()
        self.launch = self.getLaunchActivity()
        self.serial = serial
        self.suit = suit
        self.dir = self.path + '/' + self.suit
        if not os.path.isdir(self.dir):
            os.system('mkdir ' + self.dir)
        self.dir = self.path + '/' + self.suit + '/' + self.package
        if not os.path.isdir(self.dir):
            os.system('mkdir ' + self.dir)
        else:
            os.system('rm ' + self.dir + '/*.txt')
        self.method_collec = {}
        self.activity_collec = []
        self.method_tot = 0
        self.activity_tot = 0
    
    def getPackage(self):
        info = os.popen('aapt d badging ' + self.apkpath + ' | grep package').read()
        #print(self.apkpath, info)
        package = info.split()[1][6:-1]
        return package
    
    def getLaunchActivity(self):
        info = os.popen('aapt d badging ' + self.apkpath + ' | grep launchable').read()
        match = re.search("(launchable-activity: name=')(.*)", info)
        if (match != None):
            launch = match.group(2).split()[0][:-1]
            return launch

    def handle_method(self):
        f = open('tmp' + self.serial + '.txt', 'r')
        text = ""
        for line in f:
            if not line.strip():
                continue
            aft = line.strip().split('/')
            prev_string = aft[0]
            if '.' in prev_string:
                prev = prev_string.split('.')[-1]
            elif '-' in prev_string:
                prev = prev_string.split('-')[-1]
            elif ' ' in prev_string:
                prev = prev_string.split(' ')[-1]
            else:
                print("waited to be check: " + line)
                continue
            aft[0] = prev
            method = '/'.join(aft) + '\n'
            m = hashlib.md5()
            m.update(method.encode())
            #if m.hexdigest() not in method_collec:
            if self.method_collec.get(m.hexdigest()) == None:
                self.method_tot += 1
                text = text + method
                self.method_collec[m.hexdigest()] = 1
            else:
                continue
        f.close()
        if text != "":
            method_text = open(self.dir + '/' + self.package + '_' + self.suit + '_method.txt', 'a+')
            method_text.write(text)
            method_text.close()

    def handle_activity(self):
        text = ""
        lines = os.popen('adb -s ' + self.serial + ' shell logcat -d ActivityManager:I ' + self.package + '| grep "Displayed ' + self.package + '"').readlines()
        
        for line in lines:
            # line:  I/ActivityManager(  425): Displayed com.fitbit.FitbitMobile/com.fitbit.home.ui.HomeActivity_: +1s144ms
            activity = line.split('/')[1].split(':')[0]
            print("get activity:"+activity)
            #print(activity)
            if activity not in self.activity_collec:
                if "ads" not in activity:
                    self.activity_tot += 1
                    text = text +  activity + '\n'
                else:
                    text = text + '*' + activity + '\n'
                self.activity_collec.append(activity)
        os.system('adb -s ' +  self.serial + ' shell logcat -c')
        if text != "":
            activity_text = open(self.dir + '/' + self.package + '_' + self.suit + '_activity.txt', 'a+')
            activity_text.write(text)
            activity_text.close()

    def get_coverage(self):
        self.get_html_coverage()
         #datetime.datetime.now().strftime('%m/%d-%H:%M:%S')
        html_file = self.dir + '/merge_report/all_' + str(self.item-1) + '.html'
        if os.path.exists(html_file):
            a = codecs.open(html_file, 'r', 'iso-8859-1').read()
            ll = self.fetch_data(a)
        else:
            print('No all_' + str(self.item-1) + '.html')
            return

        if self.item == 1:
            f = open(self.dir + '/coverage.csv','w+')
            f.write('time,class,method,block,line\n')
        else:
            f = open(self.dir + '/coverage.csv', 'a+')
        record_time = datetime.datetime.now().strftime('%m/%d-%H:%M:%S')
        f.write(record_time + ',' + ','.join([str(round(i, 3)) for i in ll]) + '\n')
        f.close()

    def get_html_coverage(self):
        os.system("adb -s " + self.serial + " shell am broadcast -a edu.gatech.m3.emma.COLLECT_COVERAGE")
        os.system("adb -s " + self.serial + " pull /mnt/sdcard/coverage.ec " + self.dir + '/' + str(self.item) + '.ec')
        merge_string = self.dir + '/' + str(self.item) + '.ec,' + self.dir + '/' + 'merge_report/all_' + str(self.item-1) + '.ec'
        html_string = self.dir + '/coverage2.em,'+ self.dir + '/merge_report/all_'+ str(self.item) + '.ec'
        if self.item == 0:
            if not os.path.isdir(self.dir + '/merge_report'):
                os.mkdir(self.dir + '/merge_report')
            else:
                os.system("rm " + self.dir + '/merge_report/*.ec')
            os.system('cp ' + self.dir + '/0.ec ' + self.dir + '/merge_report/all_0.ec' )
            os.system('rm ' + self.dir + '/0.ec')
            os.system('java -cp ' + emma_dir + ' emma report -r html -in ' + html_string + ' -Dreport.html.out.file=' + self.dir + '/merge_report/all_' + str(self.item) + '.html')
        else:
            if not os.path.isfile(self.dir + '/' + str(self.item) + '.ec'):
                return
            os.system('java -cp ' + emma_dir + ' emma merge -input ' + merge_string + ' -out ' + self.dir + '/merge_report/all_' + str(self.item) + '.ec')            
            # 以html格式产生报告
            os.system('java -cp ' + emma_dir + ' emma report -r html -in ' + html_string + ' -Dreport.html.out.file=' + self.dir + '/merge_report/all_' + str(self.item) + '.html')
            # merge完上一个ec后直接删除
            os.system('rm ' + self.dir + '/' + str(self.item) + '.ec')
            os.system('rm ' + self.dir + '/merge_report/all_' + str(self.item-1) + '.ec')
        self.item += 1


    def fetch_data(self, html):
        soup = BeautifulSoup(html, 'lxml')
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


def getPid(package_name, serial):
    options = os.popen('adb -s ' + serial + ' shell ps | grep ' + package_name).readlines()
    query = []
    for option in options:
        if option.strip().split()[-1] == package_name:
            query = option.strip().split()
            break
    if len(query) > 2:
        app_pid = query[1]
    else:
        app_pid = '0'

    return app_pid

def getHostPid(key_word):
    options = os.popen('ps aux | grep ' + key_word).readlines()
    query = []
    if len(options) > 0:
        option = options[0]
        query = option.strip().split()

        if len(query) > 2:
            pid = query[1]
        else:
            pid = '0'
    else:
        pid = '0'

    return pid

if __name__ == '__main__':
    pass
