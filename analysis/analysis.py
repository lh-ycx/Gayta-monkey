# -*- coding: utf-8 -*-

'''
--- ver 1.0 ---
1. 下载app，获取application-label
2. 使用SearchEngineScrapy爬取google/baidu搜索label的结果的前10条
3. 打开爬到的url，保存html文件
4. 对比html文件与viewtree文件
'''
import os
import locale
import transport_util
import subprocess
import json

from settings import apk_dir, apk_source
from logger import logger
from baidu import originalURL

if __name__ == "__main__":

    finished = []
    while(True):
        # 1.1 download app
        transport_util.download_old_app()

        # build task
        output = os.popen('ls ' + apk_dir + ' -Sr').readlines()
        tasks = [i.strip() for i in output]
        
        if not tasks:
            print('can not find apk files in dir: ' + apk_dir)
        if (os.path.isfile(apk_dir + '/finished' + '.json')):
            f = open(apk_dir + '/finished' + '.json', 'r')
            finished = json.load(f)
            f.close()

        for apk in tasks:
            if apk[-3:] != 'apk':
                continue

            if apk in finished:
                logger.info('skip finished task: ' + apk)
                continue

            # 1.2 get application-label
            logger.info('start task: ' + apk)
            cmd = 'aapt d badging ' + apk_dir + '/' + apk + ' | grep application-label:'
            info = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, shell=False).stdout.readlines()
            for line in info:
                line = line.decode()
                # print(line)
                if line[:len('application-label:')] == 'application-label:':
                    label = line[len('application-label:'):]
                    label = label.strip().replace('\n', '').replace('\'', '')

            app_name = apk[:-4]
            logger.info('start analysing app: ' + label)

            # 2.1 使用SearchEngineScrapy爬取google/baidu搜索label的结果的前10条
            os.chdir('./SearchEngineScrapy/SearchEngineScrapy/')
            if apk_source == 'Google':
                cmd = 'scrapy crawl SearchEngineScrapy -a searchQuery=\"' + \
                    label + '\" -a searchEngine=\"Bing\" -o result.json'
            if apk_source == 'WDJ':
                cmd = 'scrapy crawl SearchEngineScrapy -a searchQuery=\"' + \
                    label + '\" -a searchEngine=\"Baidu\" -o result.json'
            p = subprocess.Popen(cmd, stdout=None, shell=False)
            p.wait()
            p.kill()

            os.chdir('../../')
            if not os.path.isdir('web_output/' + app_name):
                os.mkdir('web_output/' + app_name)
            # if not os.path.isdir('output/' + app_name):
                # os.mkdir('output/' + app_name)
            os.system('mv ./SearchEngineScrapy/SearchEngineScrapy/result.json ./web_output/' +
                      app_name + '/searchResult.json')
            
            # 2.2 对于百度爬到的url
            if apk_source == 'WDJ' :
                f = './web_output/' + app_name + '/searchResult.json'
                logger.info('proccessing app: ' + f + '...')
                try :
                    fp = open(f, 'r')
                    urls = json.load(fp)
                    fp.close()
                    for i in range(len(urls)):
                            tmpurl = urls[i]['url']
                            urls[i]['url'] = originalURL(tmpurl)
                    fp = open(f,'w')
                    json.dump(urls, fp)
                except :
                    logger.error('error app: ' + f)
            
            # 3.1 打开每一个url保存html文件
            '''
            fp = open('./web_output/' + app_name + '/searchResult.json', 'r')
            searchResult = json.load(fp)[:10]
            fp.close()
            print('------------------')
            print(searchResult)
            print('------------------')
            cnt = 0
            for url in searchResult:
                content = os.popen("curl " + url)
                fp = open('output/' + app_name + '/' + str(cnt) + ".html", "w+b")  # 打开一个文本文件
                fp.write(content)  # 写入数据
                fp.close()  # 关闭文件
                cnt += 1
            '''
            # 4.1 对比html文件


            # 5.1 收尾
            os.system('rm ' + apk_dir + apk)
            finished.append(apk)
            fp = open(apk_dir + '/finished' + '.txt', 'w')
            json.dump(finished, fp)
            fp.close()
            

