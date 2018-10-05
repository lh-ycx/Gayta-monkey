# coding=utf-8

import os
import sys
import getopt
import json
import logging
import timeout_decorator
import time
import requests
import transport_util

from util import error_msg
from util import logger
from util import usage
from util import Check_app
from util import handle_page
from settings import paladin_dir, apk_dir
from settings import defaultsuit
from settings import is_open_source
from settings import web_retriever_port
from Application import App
from instruments import Paladin_s
from instruments import RunCmd


spider_mode = False
with_server = False

suit = defaultsuit
serial = ''


@timeout_decorator.timeout(300)
def test_coverage(subject, suit):
    os.system('adb -s ' + subject.serial + ' install ' + subject.apkpath)
    # subject = App(apk, serial, suit)
    Check_app.calculate_coverage(subject, suit)


def crawl(subject, target):  # subject = App(apk, serial, suit)
    os.system('adb -s ' + subject.serial + ' install ' + subject.apkpath)
    paladin_s = Paladin_s(subject, target)
    paladin_s.run()
    time.sleep(paladin_s.wait)
    count = 0
    while(True):
        time.sleep(60)
        count += 1
        logger.info("[spider mode] handling pages...")
        handle_page(subject.getPackage())
        
        # if count % 6 == 0 and not paladin_s.is_alive():
        if count == 10:
            logger.info("task is over")
            paladin_s.stop()
            finished = {}
            if os.path.isfile(apk_dir + '/finished-s.json') :
                f = open(apk_dir + '/finished-s.json')
                content = f.read()
                f.close()
                if content:
                    finished = json.loads(content)
                else :
                    finished = {"FINISHED":[]}
            else:
                finished = {"FINISHED":[]}
            finished['FINISHED'].append({"PACKAGE": subject.getPackage(),
                                            "TARGET_ACTIVITY": target})
            f = open(apk_dir + '/finished-s.json', 'w')
            json.dump(finished,f)
            f.close()
            break


if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv[1:], "s:t:hcw")
    for op, value in opts:
        if op == "-c":
            spider_mode = True
            suit = 'paladin-s'
            logger.info('spider mode open')
        elif op == '-w':
            with_server = True
            logger.info('start working with server')
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

    # start web retriever
    logger.info("start web retriever, lestining on port: " + web_retriever_port)
    web_retriever_log = open("web_log","a")
    self.web_retriever = RunCmd(['node','web\ retriever/ui/main.js','--serial',serial,'--server-port',web_retriever_port,'--output','./output/'])
    self.web_retriever.set_stdout(web_retriever_log)
    self.web_retriever.set_stderr(web_retriever_log)
    self.web_retriever.start_run()

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
            content = f.read()
            if(content):
                finished = json.loads(content)
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
        if with_server:
            while(True):
                # download apks
                transport_util.download_app()

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
                    os.system('rm ' + apk_dir + apk)
                    transport_util.upload_app(subject.package)
                    os.system('rm -r output/' + subject.package + '/')
                    f = open(apk_dir + '/finished_' + suit + '.txt', 'a+')
                    f.write(subject.package + '\n')
                    f.close()
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
