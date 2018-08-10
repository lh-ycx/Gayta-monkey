from flask import Flask, render_template
import os
import requests
import json
import re

from settings import src_dir
from settings import elastic_url
app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('homepage.html')


@app.route('/app/<app_name>')
def show_app_data(app_name):
    # print(app_name)
    filelist = []   # 形式为[ (app_name,filename) ]
    for dirpath, dirnames, filenames in os.walk(src_dir + app_name):
        for filename in filenames:
            if(filename[-3:] == 'png'):
                filelist.append((app_name, filename[:-4]))    # 去掉后缀
    # print(filelist)
    if(filelist):
        return render_template('app.html', filelist=filelist, src_dir=src_dir)
    else:
        return render_template('error.html')


'''
here act_name is actually page_name
page_name = act_name + "_" + structure_content + "_" + content_hash
'''
@app.route('/app/<app_name>/<act_name>')
def show_page_date(app_name, act_name):
    filepath1 = src_dir + app_name + "/" + act_name + ".png"
    filepath2 = src_dir + app_name + "/" + act_name + ".json"
    content_hash = re.findall("-?[0-9]*$", act_name)[0]
    filepath3 = src_dir + app_name + "/" + content_hash + ".json"
    print("filepath:" + filepath3)
    if(os.path.exists(filepath1) and os.path.exists(filepath2) and os.path.exists(filepath3)):
        simple_tree = open(filepath3).read()
        print("simple tree: ")
        print(simple_tree)
        return render_template("detail.html", app_name=app_name, act_name=act_name, src_dir=src_dir, simple_tree = simple_tree)
    else:
        return render_template('error.html')


@app.route('/search/<searchq>')
def search(searchq):
    json_obj = {
        "query": {"match": {"CONTENT": searchq}}
    }
    response = requests.post(elastic_url,json = json_obj)
    response = json.loads(response.text)
    print(response)
    if response['hits']['total'] == 0:
        return render_template('error.html')
    else :
        results = []
        for hit in  response['hits']['hits']:
            result = {}
            result["score"] = hit['_score']
            result["source"] = hit["_source"]
            results.append(result)
        print(results)
        return render_template("result.html", results = results, src_dir = src_dir, searchq = searchq)


if __name__ == "__main__":
    app.run()
