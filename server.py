from flask import Flask, render_template
import os


from setting import src_dir
app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('homepage.html')


@app.route('/app/<app_name>')
def show_app_data(app_name):
    print(app_name)
    filelist = []   # 形式为[ (app_name,filename) ]
    for dirpath, dirnames, filenames in os.walk(src_dir + app_name):
        for filename in filenames:
            if(filename[-3:] == 'png'):
                filelist.append((app_name , filename[:-4]))    # 去掉后缀
    #print(filelist)
    if(filelist):
        return render_template('app.html', filelist = filelist, src_dir = src_dir)
    else:
        return render_template('error.html')

@app.route('/app/<app_name>/<act_name>')
def show_page_date(app_name, act_name):
    filepath1 = src_dir + app_name + "/" + act_name + ".png"
    filepath2 = src_dir + app_name + "/" + act_name + ".json"
    if(os.path.exists(filepath1) and os.path.exists(filepath2)):
        return render_template("detail.html", app_name=app_name, act_name=act_name, src_dir=src_dir)
    else :
        return render_template('error.html')

if __name__ == "__main__":
    app.run()
