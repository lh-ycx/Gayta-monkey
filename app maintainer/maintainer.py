'''

--- ver 1.1 ---
update in 2018/11/19
增加两个文件：
Google(WDJ)_unanalysis.txt: 还没有被分析的app
Google(WDJ)_analysis.txt:   分析过的app

--- ver 1.2 ---
update in 2018/12/1
现在会按照排名顺序返回apk名
'''


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
    # file_list = os.listdir('GooglePlayApk')
    # f = open("GooglePlayWebview.json",'r')
    f = open("GooglePlayRanked.txt",'r')
    file_list = json.load(f)
    f.close()

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
    # file_list = os.listdir('WDJApk')
    # f = open("WDJWebview.json",'r')
    f = open("WDJRanked.txt",'r')
    file_list = json.load(f)
    f.close()
    
    finished_list = []
    apk_list = []
    
    if os.path.getsize('WDJ_finished.txt'):
        fp = open('WDJ_finished.txt', 'r')
        finished_list = json.load(fp)
        fp.close()
    
    for f in file_list:
        # if re.search('.*\.apk$',f) and f not in finished_list:
        if f not in finished_list:
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


@app.route('/GooglePlayApk/unanalysised')
def Google_unanalysised():
    f = open("Google_unanalysis.txt",'r')
    file_list = json.load(f)
    f.close()
    return json.dumps(file_list)


@app.route('/GooglePlayApk/analysised')
def Google_analysised():
    analysis_list = []
    
    if os.path.getsize('Google_analysis.txt'):
        fp = open('Google_analysis.txt', 'r')
        analysis_list = json.load(fp)
        fp.close()

    return json.dumps(analysis_list)


@app.route('/GooglePlayApk/analysis/<app_name>')
def Google_analysis(app_name):
    analysis_list = []
    unanalysis_list = []
    
    if os.path.getsize('Google_analysis.txt'):
        fp = open('Google_analysis.txt', 'r')
        analysis_list = json.load(fp)
        fp.close()
    
    if app_name in analysis_list:
        return app_name + ' already analysised'
    else:
        # unanalysis 列表不存在
        if os.path.getsize('Google_unanalysis.txt') == 0:
            return 'error! ' + app_name + ' not in unanalysis list'
        else:
            fp = open('Google_unanalysis.txt', 'r')
            unanalysis_list = json.load(fp)
            fp.close()
            # 不在 unanalysis 列表中
            if app_name not in unanalysis_list:
                return 'error! ' + app_name + ' not in unanalysis list'
            # 在的话移除并加入到analysis列表中，返回success
            else:
                analysis_list.append(app_name)
                unanalysis_list.remove(app_name)
                fp_1 = open('Google_analysis.txt', 'w')
                fp_2 = open('Google_unanalysis.txt', 'w')
                json.dump(analysis_list, fp_1)
                json.dump(unanalysis_list, fp_2)
                fp_1.close()
                fp_2.close()
                return 'success'


@app.route('/WDJApk/unanalysised')
def WDJ_unanalysised():
    f = open("WDJ_unanalysis.txt",'r')
    file_list = json.load(f)
    f.close()
    return json.dumps(file_list)


@app.route('/WDJApk/analysised')
def WDJ_analysised():
    analysis_list = []
    
    if os.path.getsize('WDJ_analysis.txt'):
        fp = open('WDJ_analysis.txt', 'r')
        analysis_list = json.load(fp)
        fp.close()

    return json.dumps(analysis_list)


@app.route('/WDJApk/analysis/<app_name>')
def WDJ_analysis(app_name):
    analysis_list = []
    unanalysis_list = []
    
    if os.path.getsize('WDJ_analysis.txt'):
        fp = open('WDJ_analysis.txt', 'r')
        analysis_list = json.load(fp)
        fp.close()
    
    if app_name in analysis_list:
        return app_name + ' already analysised'
    else:
        # unanalysis 列表不存在
        if os.path.getsize('WDJ_unanalysis.txt') == 0:
            return 'error! ' + app_name + ' not in unanalysis list'
        else:
            fp = open('WDJ_unanalysis.txt', 'r')
            unanalysis_list = json.load(fp)
            fp.close()
            # 不在 unanalysis 列表中
            if app_name not in unanalysis_list:
                return 'error! ' + app_name + ' not in unanalysis list'
            # 在的话移除并加入到analysis列表中，返回success
            else:
                analysis_list.append(app_name)
                unanalysis_list.remove(app_name)
                fp_1 = open('WDJ_analysis.txt', 'w')
                fp_2 = open('WDJ_unanalysis.txt', 'w')
                json.dump(analysis_list, fp_1)
                json.dump(unanalysis_list, fp_2)
                fp_1.close()
                fp_2.close()
                return 'success'

    



if __name__ == '__main__':
    app.run(host='162.105.175.241')

    if not os.path.isfile('Google_finished.txt'):
        fp = open('Google_finished.txt', 'w')
        fp.close()
    
    if not os.path.isfile('WDJ_finished.txt'):
        fp = open('WDJ_finished.txt', 'w')
        fp.close()
    
    if not os.path.isfile('Google_unanalysis.txt'):
        os.popen('cp Google_finished.txt Google_unanalysis.txt')

    if not os.path.isfile('WDJ_unanalysis.txt'):
        os.popen('cp WDJ_finished.txt WDJ_unanalysis.txt')
    
    if not os.path.isfile('Google_analysis.txt'):
        fp = open('Google_analysis.txt', 'w')
        fp.close()
    
    if not os.path.isfile('WDJ_analysis.txt'):
        fp = open('WDJ_analysis.txt', 'w')
        fp.close()