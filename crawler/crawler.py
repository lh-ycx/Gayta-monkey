# coding=utf-8

import os
import sys
import getopt
import json
import logging

from setting import paladin_dir, apk_dir,defaultsuit
from util import error_msg

spider_mode = False

#logger
logger = logging.getLogger("crawler logger")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("spam.log")
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
logger.addHandler(ch)
logger.addHandler(fh)

def usage():
    return

suit = defaultsuit
serial = ''

if __name__ == "__main__":

    opts, args = getopt.getopt(sys.argv[1:], "s:hc")
    for op, value in opts:
        #print(op,value)
        if op == "-c":
            spider_mode = True
            logger.info('spider mode open')
        elif op == '-s':
            serial = value
            logger.info('read serial setting: ' + serial)
        elif op == "-h":
            usage()
            sys.exit()
        else:
            usage()
            sys.exit()
    
    tasks = []
    finished = []
    if spider_mode:
        if (os.path.isfile(apk_dir + '/tasks.json')):
            f = open(apk_dir + '/tasks.json')
            tasks = json.load(f)
            f.close()
            tasks = tasks['TASKS']
            if not tasks:
                error_msg('open tasks.json error, please check tasks.json!')
        else:
            error_msg('no such file: '+ apk_dir + '/tasks.json')
        
        if (os.path.isfile(apk_dir + '/finished-s.json')):
            f = open(apk_dir + '/finished-s.json')
            finished = json.load(f)
            f.close()
            finished = finished['FINISHED']
        
        for task in tasks:
            if task in finished:
                logger.info("skip finished task:("+task['PACKAGE']+","+task['TARGET_ACTIVITY'] + ')')
                continue
            logger.info("start task:("+task['PACKAGE']+","+task['TARGET_ACTIVITY'] + ')')
            

