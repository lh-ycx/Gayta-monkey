# coding=utf-8
'''
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

if __name__ == "__main__":
    package = 'com.douban.movie'
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
    
    for i in toupload:
        if i not in uploaded:
            print('uploading '+ i)
            f = open((output_dir + i) ,'r')
            data = f.read()
            f.close()
            response = requests.post(elastic_url, json=json.loads(data))
            jresponse = json.loads(response.text)
            if 'result' in jresponse and jresponse['result'] == 'created':
                print('succeed in uploading '+ i)
                uploaded.append(i)
            else: 
                print('failed in uploading ' + i)

    f = open((output_dir + "uploaded.txt") ,'w')
    for i in uploaded:
        f.write(i+'\n')
    f.close()
'''


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
from util import handle_page
from settings import paladin_dir, apk_dir
from settings import defaultsuit
from settings import is_open_source
from Application import App
from instruments import Paladin_s


f = open(apk_dir + '/finished-s.json')
content = f.read()
print(content)
finished = json.loads(content)
finished['FINISHED'].append({"PACKAGE": "com.douban.movie",
                            "TARGET_ACTIVITY": "LegacySubjectActivity"})
f.close()
f = open(apk_dir + '/finished-s.json', 'w')
json.dump(finished,f)
f.close()

