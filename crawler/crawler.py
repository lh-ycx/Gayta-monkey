# coding=utf-8

import os
import sys
import getopt
import json
import logging
import timeout_decorator
import time
import requests

from settings import paladin_dir, apk_dir
from settings import defaultsuit
from settings import is_open_source
from util import error_msg
from Application import App
from util import Check_app

spider_mode = False

# logger
logger = logging.getLogger("crawler logger")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("spam.log")
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter(
    '[%(asctime)s] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
logger.addHandler(ch)
logger.addHandler(fh)


def usage():
    return


suit = defaultsuit
serial = ''

if __name__ == "__main__":

    opts, args = getopt.getopt(sys.argv[1:], "s:t:hc")
    for op, value in opts:
        if op == "-c":
            spider_mode = True
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
                    "[spider mode] skip finished task:("+task['PACKAGE']+","+task['TARGET_ACTIVITY'] + ')')
                continue
            logger.info(
                "[spider mode] start task:("+task['PACKAGE']+","+task['TARGET_ACTIVITY'] + ')')

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

            logger.info('start task:')
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


@timeout_decorator.timeout(10800)
def test_coverage(subject, suit):
    os.system('adb -s ' + subject.serial + ' install ' + subject.apkpath)
    Check_app.calculate_coverage(subject, suit)     #subject = App(apk, serial, suit)