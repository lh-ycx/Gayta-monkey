# coding=utf-8

import os
import sys
import getopt
import json
import logging
import timeout_decorator
import time
import requests

from util import error_msg
from util import logger
from util import usage
from util import Check_app
from settings import paladin_dir, apk_dir
from settings import defaultsuit
from settings import is_open_source
from Application import App
from instruments import Paladin_s

spider_mode = False


suit = defaultsuit
serial = ''



@timeout_decorator.timeout(10800)
def test_coverage(subject, suit):
    os.system('adb -s ' + subject.serial + ' install ' + subject.apkpath)
    Check_app.calculate_coverage(subject, suit)     #subject = App(apk, serial, suit)


def crawl(subject, target): #subject = App(apk, serial, suit)
    os.system('adb -s ' + subject.serial + ' install ' + subject.apkpath)
    paladin_s = Paladin_s(subject, target)
    paladin_s.run()
    time.sleep(paladin_s.wait)
    while(True):
        time.sleep(30)
        if not paladin_s.is_alive():
            logger.info("check if is alive")
            paladin_s.stop()


if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv[1:], "s:t:hc")
    for op, value in opts:
        if op == "-c":
            spider_mode = True
            suit = 'paladin-s'
            logger.info('spider mode open')
        elif op == '-s':
            serial = value
            logger.info('read serial setting: ' + serial)
        elif op == '-t':
            suit = value
            logger.info('read suit setting: ' + suit)
        elif op == "-h":
            usage()
            sys.exit()
        else:
            usage()
            sys.exit()

    tasks = []
    finished = []
    if spider_mode:
        # build task
        if (os.path.isfile(apk_dir + '/tasks.json')):
            f = open(apk_dir + '/tasks.json')
            tasks = json.load(f)
            f.close()
            tasks = tasks['TASKS']
            if not tasks:
                error_msg(
                    '[spider mode] open tasks.json error, please check tasks.json!')
        else:
            error_msg('[spider mode] no such file: ' + apk_dir + '/tasks.json')

        # build finished
        if (os.path.isfile(apk_dir + '/finished-s.json')):
            f = open(apk_dir + '/finished-s.json')
            finished = json.load(f)
            f.close()
            finished = finished['FINISHED']

        # run
        for task in tasks:
            if task in finished:
                logger.info(
                    "[spider mode] skip finished task:(PACKAGE:"+task['PACKAGE']+",TARGET_ACTIVITY:"+task['TARGET_ACTIVITY'] + ')')
                continue
            logger.info(
                "[spider mode] start task:(PACKAGE:"+task['PACKAGE']+",TARGET_ACTIVITY:"+task['TARGET_ACTIVITY'] + ')')
            subject = App(task['PACKAGE']+'.apk', serial, suit)
            crawl(subject, task['TARGET_ACTIVITY'])

    else:
        # build task
        output = os.popen('ls ' + apk_dir + ' -Sr').readlines()
        tasks = [i.strip() for i in output]
        if not tasks:
            error_msg('can not find apk files in dir: ' + apk_dir)

        # build finished
        if (os.path.isfile(apk_dir + '/finished_' + suit + '.txt')):
            f = open(apk_dir + '/finished_' + suit + '.txt', 'r')
            content = f.read()
            finished = content.split('\n')
            f.close()

        # run
        for apk in tasks:
            if apk[-3:] != 'apk':
                continue

            if apk in finished:
                logger.info('skip finished task: ' + apk)
                continue

            logger.info('start testing ' + apk + ' using ' + suit)
            subject = App(apk, serial, suit)
            try:
                test_coverage(subject, suit)
            except timeout_decorator.timeout_decorator.TimeoutError as e:
                if not is_open_source:
                    fout = open(subject.dir + '/' +
                                subject.package + '_coverage.txt', 'w+')
                    fout.write(subject.package + ' ' + str(subject.activity_tot) +
                               ' ' + str(subject.method_tot) + '\n')
                    fout.close()
                logger.info('task ' + apk + ' time out')

            os.system('adb -s ' + subject.serial +
                      ' uninstall ' + subject.package)
            f = open(apk_dir + '/finished_' + suit + '.txt', 'a+')
            f.write(subject.package + '\n')
            f.close()


