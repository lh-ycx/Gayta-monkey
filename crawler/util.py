# coding=utf-8

from settings import is_open_source
from settings import apk_dir
from settings import elastic_url
from settings import paladin_dir
from Application import App

import os
import re
import time
import requests
import hashlib
import subprocess as sub
import threading
import instruments
import datetime
import timeout_decorator
import logging
import re
import json

# logger
logger = logging.getLogger("ycx")
logger.setLevel(logging.INFO)
fh = logging.FileHandler("spam.log")
fh.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '[%(asctime)s] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
logger.addHandler(ch)
logger.addHandler(fh)

# error message
def error_msg(msg):
    print("================= error =================")
    print(msg)
    print("================= ===== =================")


def usage():
    return

class Method_handler():
    collecting = False
    @staticmethod
    def start(subject):
        package = subject.package
        Method_handler.collecting = True
        os.system('adb -s ' + subject.serial + ' shell am profile start ' + package + ' sdcard/' + 'tmp' + subject.serial + '.trace')
        print('start collecting')



    @staticmethod
    def stop(subject):
        if Method_handler.collecting:
            #os.system('adb shell am profile ' + pid + ' stop')
            pkg = subject.package
            launch = subject.launch
            os.system('adb -s ' + subject.serial + ' shell am profile stop')
            print('stop collecting')
            Method_handler.collecting = False
            time.sleep(1)
            t = pkg.split('.')
            if len(t) > 2:
                search_text1 = t[0] + '/' + t[1]
            else:
                search_text1 = pkg
            
            if launch != None:
                b = launch.split('.')
                if len(b) > 2:
                    search_text2 = b[0] + '/' + b[1]
                else:
                    search_text2 = launch
            else:
                search_text2 = " "

            os.system('adb -s ' + subject.serial + ' pull sdcard/tmp' + subject.serial + '.trace '  + './')
            cmd = "dmtracedump -o tmp" + subject.serial + ".trace " + " | grep '" + search_text1 + "\|" + search_text2 + "' |grep [^a-zA-Z]ent[^a-zA-Z] > " + "tmp" + subject.serial + ".txt"
            print('dmtrace command ' + cmd)
            os.system(cmd)
            os.system('adb -s ' + subject.serial +  ' shell rm sdcard/' + 'tmp' + subject.serial + '.trace')

    @staticmethod
    def handle_method(subject):
        if not os.path.isfile('tmp' + subject.serial + '.txt'):
            print('No available method collection file!')
            return

        f = open('tmp' + subject.serial + '.txt', 'r')
        text = ""
        method_collec = {}
        method_tot = 0

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
            if method_collec.get(m.hexdigest()) == None:
                method_tot += 1
                text = text + method
                method_collec[m.hexdigest()] = 1
            else:
                continue
        f.close()
        print(text, method_tot)
        return method_tot


def matchForeground(package):
    content = os.popen('adb shell dumpsys activity activities').read()
    match = re.findall("(ProcessRecord\{)(.*:)(.*)(/.*)", content)
    # 安卓自带模拟器里匹配的是最后一个出现的record

    if (match != None):
        #print('package: ' + package)
        for m in match:
            #print('compared: ', m)
            if (m[2] == package):
                return True
        return False
    else:
        return False

def handle_activity(package_name):
    activity = []
    lines = os.popen('adb shell logcat -d ActivityManager:I ' + package_name + '| grep "Displayed ' + package_name + '"').readlines()
    
    for line in lines:
        # line:  I/ActivityManager(  425): Displayed com.fitbit.FitbitMobile/com.fitbit.home.ui.HomeActivity_: +1s144ms
        act = line.split('/')[2].split(':')[0]
        #print(activity)
        activity.append(act)
    
    return activity
                

class Check_app():
    @staticmethod
    def calculate_coverage(subject, ins_name):
        os.system('adb -s ' + subject.serial + ' shell logcat -c')
        current_instrument = instruments.instruments[ins_name](subject)
        current_instrument.run()
        time.sleep(current_instrument.wait)
        count = 0
        try:
            while(True):
                count += 1
                if not is_open_source:
                    time.sleep(current_instrument.span)
                    subject.handle_activity()
                else:
                    subject.get_coverage()
                    time.sleep(15)

                if count == 12:
                    if not is_open_source:
                        fk = open(subject.dir + '/' + subject.package + '_' + subject.suit + '_time_coverage.txt', 'a+')
                        record_time = datetime.datetime.now().strftime('%m/%d-%H:%M:%S')
                        fk.write(record_time + ' ' + str(subject.activity_tot) + '\n')
                        fk.close()
                    if ins_name == 'paladin' :
                        #执行'http://127.0.0.1:5700/save'
                        current_instrument.save_graph()
                    if not current_instrument.is_alive():
                        #print('instrument stop')
                        if ins_name == 'monkey' :
                            # 记录crash
                            fk = open(subject.dir + '/' + subject.package + '_' + subject.suit + '_time_coverage.txt', 'a+')
                            record_time = datetime.datetime.now().strftime('%m/%d-%H:%M:%S')
                            fk.write(record_time + ' ' + 'crash!' + '\n')
                            fk.close()
                            # 重新启动monkey
                            current_instrument.run()
                        else :
                            raise timeout_decorator.timeout_decorator.TimeoutError('timeout')
                    count = 0
        except timeout_decorator.timeout_decorator.TimeoutError as e:
            current_instrument.stop()
            raise timeout_decorator.timeout_decorator.TimeoutError('timeout')


def handle_page(package):
    uploaded = []
    toupload = []
    output_dir = paladin_dir + 'output/' + package + '/'
    if (os.path.isfile(output_dir+"uploaded.txt")):
        f = open((output_dir + "uploaded.txt") ,'r')
        content = f.read()
        uploaded = content.split('\n')
        f.close()
    
    if(os.path.isdir(output_dir)):
        output = os.popen('ls ' + output_dir).readlines()
        for i in output :
            i = i.strip()
            if re.match('^-?[0-9]*.json$', i):
                toupload.append(i)
    else :
        os.mkdir(output_dir)
    
    for i in toupload:
        if i not in uploaded:
            f = open((output_dir + i) ,'r')
            data = f.read()
            f.close()
            logger.info("before request")
            response = requests.post(elastic_url, json=json.loads(data))
            logger.info("after request")
            jresponse = json.loads(response.text)
            if 'result' in jresponse and jresponse['result'] == 'created':
                logger.info('succeed in uploading '+ i)
                uploaded.append(i)
            else: 
                logger.error('failed in uploading ' + i)
                error_msg('failed in uploading ' + i)
                raise RuntimeError('uploading error')

    f = open((output_dir + "uploaded.txt") ,'w')
    for i in uploaded:
        f.write(i)
        if(i):
            f.write('\n')
    f.close()
    logger.info('finish handling pages')
    return
            

        

if __name__ == '__main__':
    subject = App('com.evancharlton.mileage.apk', 'ZX1G223KRJ', 'monkey')
    os.system('adb install ' + apk_dir + '/com.evancharlton.mileage.apk')
    #Check_app.check_app_running('akai.floatView.op.luffy.apk', 'monkey')
    #Check_app.check_app_running(subject, 'droidbot')
    #Check_app.check_app_running(subject, 'stoat')
    #Check_app.check_app_running(subject, 'sapienz')
    #App.getLaunchActivity('akai.floatView.op.luffy.apk')
    Check_app.calculate_coverage(subject, 'monkey')
    pass

