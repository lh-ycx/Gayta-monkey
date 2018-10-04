from flask import Flask
import os
import json
import re
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/GooglePlayApk/unfinished')
def Google_unfinished():
    file_list = os.listdir('GooglePlayApk')
    finished_list = []
    apk_list = []
    
    if os.path.getsize('Google_finished.txt'):
        fp = open('Google_finished.txt', 'r')
        finished_list = json.load(fp)
        fp.close()
    
    for f in file_list:
        if re.search('.*\.apk$',f) and f not in finished_list:
            apk_list.append(f)
    return json.dumps(apk_list)


@app.route('/GooglePlayApk/finished')
def Google_finished():
    finished_list = []
    
    if os.path.getsize('Google_finished.txt'):
        fp = open('Google_finished.txt', 'r')
        finished_list = json.load(fp)
        fp.close()

    return json.dumps(finished_list)


@app.route('/GooglePlayApk/unfinish/<apk_name>')
def Google_unfinish(apk_name):
    finished_list = []
    
    if os.path.getsize('Google_finished.txt'):
        fp = open('Google_finished.txt', 'r')
        finished_list = json.load(fp)
        fp.close()
    
    if apk_name in finished_list:
        finished_list.remove(apk_name)
        fp = open('Google_finished.txt', 'w')
        json.dump(finished_list, fp)
        fp.close()
        return 'success'
    else:
        return 'error! no such file: ' + apk_name


@app.route('/GooglePlayApk/finish/<apk_name>')
def Google_finish(apk_name):
    finished_list = []
    
    if os.path.getsize('Google_finished.txt'):
        fp = open('Google_finished.txt', 'r')
        finished_list = json.load(fp)
        fp.close()
    
    if apk_name in finished_list:
        return apk_name + 'already finished!'
    else:
        finished_list.append(apk_name)
        fp = open('Google_finished.txt', 'w')
        json.dump(finished_list, fp)
        fp.close()
        return 'success'


@app.route('/WDJApk/unfinished')
def WDJ_unfinished():
    file_list = os.listdir('WDJApk')
    finished_list = []
    apk_list = []
    
    if os.path.getsize('WDJ_finished.txt'):
        fp = open('WDJ_finished.txt', 'r')
        finished_list = json.load(fp)
        fp.close()
    
    for f in file_list:
        if re.search('.*\.apk$',f) and f not in finished_list:
            apk_list.append(f)
    return json.dumps(apk_list)


@app.route('/WDJApk/finished')
def WDJ_finished():
    finished_list = []
    
    if os.path.getsize('WDJ_finished.txt'):
        fp = open('WDJ_finished.txt', 'r')
        finished_list = json.load(fp)
        fp.close()

    return json.dumps(finished_list)


@app.route('/WDJApk/unfinish/<apk_name>')
def WDJ_unfinish(apk_name):
    finished_list = []
    
    if os.path.getsize('WDJ_finished.txt'):
        fp = open('WDJ_finished.txt', 'r')
        finished_list = json.load(fp)
        fp.close()
    
    if apk_name in finished_list:
        finished_list.remove(apk_name)
        fp = open('WDJ_finished.txt', 'w')
        json.dump(finished_list, fp)
        fp.close()
        return 'success'
    else:
        return 'error! no such file: ' + apk_name


@app.route('/WDJApk/finish/<apk_name>')
def WDJ_finish(apk_name):
    finished_list = []
    
    if os.path.getsize('WDJ_finished.txt'):
        fp = open('WDJ_finished.txt', 'r')
        finished_list = json.load(fp)
        fp.close()
    
    if apk_name in finished_list:
        return apk_name + 'already finished!'
    else:
        finished_list.append(apk_name)
        fp = open('WDJ_finished.txt', 'w')
        json.dump(finished_list, fp)
        fp.close()
        return 'success'


if __name__ == '__main__':
    app.run(host='162.105.175.241')

    if not os.path.isfile('Google_finished.txt'):
        fp = open('Google_finished.txt', 'w')
        fp.close()
    
    if not os.path.isfile('WDJ_finished.txt'):
        fp = open('WDJ_finished.txt', 'w')
        fp.close()