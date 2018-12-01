import re
import requests
import os
import json

from pyquery import PyQuery as Pq


class BaiduSearchSpider(object):
    
    def __init__(self, searchText):
        self.url = "http://www.baidu.com/baidu?wd=%s&tn=monline_4_dg" % searchText
        self.headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/600.5.17 (KHTML, like Gecko) Version/8.0.5 Safari/600.5.17"}
        self._page = None
    
    @property 
    def page(self):
        if not self._page:
            r = requests.get(self.url, headers=self.headers)
            r.encoding = 'utf-8'
            self._page = Pq(r.text)
        return self._page
    
    @property
    def baiduURLs(self):
        return [(site.attr('href'), site.text().encode('utf-8')) for site in self.page('div.result.c-container  h3.t  a').items()]
    
    @property    
    def originalURLs(self):
        tmpURLs = self.baiduURLs
        print(tmpURLs)
        originalURLs = []
        for tmpurl in tmpURLs:
            tmpPage = requests.get(tmpurl[0], allow_redirects=False)
            if tmpPage.status_code == 200:
                urlMatch = re.search(r'URL=\'(.*?)\'', tmpPage.text.encode('utf-8'), re.S)
                originalURLs.append((urlMatch.group(1), tmpurl[1]))
            elif tmpPage.status_code == 302:
                originalURLs.append((tmpPage.headers.get('location'), tmpurl[1]))
            else:
                print('No URL found!!')
 
        return originalURLs


def originalURL(tmpURL): 
    originalURL = ''
    
    tmpPage = requests.get(tmpURL, allow_redirects=False)
    if tmpPage.status_code == 200:
        urlMatch = re.search(r'URL=\'(.*?)\'', tmpPage.text.encode('utf-8'), re.S)
        originalURL = urlMatch.group(1)
    elif tmpPage.status_code == 302:
        originalURL = tmpPage.headers.get('location')
    else :
        print('====================')
        print('failed: ' + tmpURL)
        print('====================')
        return ''
    return originalURL

if __name__ == "__main__":
    Root = './web_output/WDJ'

    for (root, dirs, files) in os.walk(Root):
        for f in files :
            if f == 'searchResult.json' :
                f = os.path.join(root, f)
                print('proccessing app: ' + f + '...')
                try :
                    fp = open(f, 'r')
                    urls = json.load(fp)
                    fp.close()
                    for i in range(len(urls)):
                        tmpurl = urls[i]['url']
                        if not isinstance(tmpurl, str) :
                            continue
                        urls[i]['url'] = originalURL(tmpurl)
                    fp = open(f,'w')
                    json.dump(urls, fp)
                except :
                    print('error app: ' + f)
                    
                
    
