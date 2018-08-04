# coding=utf-8

import os
import time
import requests
import sys
import timeout_decorator
from Application import App
from util import Check_app
from settings import is_open_source
from settings import apk_dir

def preprocess(package):
    os.system('adb shell monkey -p ' + package + ' --throttle 300 --pct-touch 100 10')
    #scroll left for 5 times
    for i in range(5):
        os.system('adb shell input swipe 600 500 200 500')
        time.sleep(2)
    os.system('adb shell monkey -p ' + package + ' --throttle 300 --pct-touch 100 70')
    os.system('adb shell am force-stop ' + package + ' >/dev/null')

suit = sys.argv[1]
serial = sys.argv[2]  
apkdir = apk_dir     

output = os.popen('ls ' + apkdir + ' -Sr').readlines()
apks = [i.strip() for i in output]


@timeout_decorator.timeout(10800)
def test_coverage(subject, suit):
    os.system('adb -s ' + subject.serial + ' install ' + subject.apkpath)
    Check_app.calculate_coverage(subject, suit)     #subject = App(apk, serial, suit)
            
if __name__ == '__main__':
    checked_apks = []
    if (os.path.isfile(apkdir + '/finished_' + suit + '.txt')):
        f = open(apkdir + '/finished_' + suit + '.txt', 'r')
        content = f.read()
        checked_apks = content.split('\n')
        f.close()

    apks_num = len(apks)
    checked_apks_num = len(checked_apks)
    print('total apks num:',apks_num)
    print('finished:',checked_apks_num)
    now = 1

    for apk in apks:
        if apk[-3:] != 'apk':
            continue

        if apk in checked_apks:
            continue

        print('===========================testing No.',now,'===========================')
        now += 1
        subject = App(apk, serial, suit)    
        try:
            test_coverage(subject, suit)
        except timeout_decorator.timeout_decorator.TimeoutError as e:
            if not is_open_source:
                fout = open(subject.dir + '/' + subject.package + '_coverage.txt', 'w+')
                fout.write(subject.package + ' ' + str(subject.activity_tot) + ' ' + str(subject.method_tot) + '\n')
                fout.close()
            print('timeout')

        os.system('adb -s ' + subject.serial + ' uninstall ' + subject.package)
        f = open(apkdir + '/finished_' + suit + '.txt', 'a+')
        f.write(subject.package + '\n')
        f.close()
    