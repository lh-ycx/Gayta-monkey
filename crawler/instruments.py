# coding=utf-8

import os
import time
import requests
import subprocess as sub
import threading
import json
from Application import App
from Application import getPid
from Application import getHostPid
from settings import apk_dir
from settings import paladin_dir

class RunCmd(threading.Thread):
    def __init__(self, cmd):
        threading.Thread.__init__(self)
        self.cmd = cmd

    def run(self):
        self.p = sub.Popen(self.cmd, stdout=sub.DEVNULL, stderr=sub.DEVNULL)
        #self.p = sub.Popen(self.cmd)
        self.p.wait()

    def start_run(self):
        self.start()

    def stop_run(self):
        if self.is_alive():
            #self.p.terminate()      #use self.p.kill() if process needs a kill -9
            #self.join()
            self.p.kill()

class RunCmd_timeout(threading.Thread):
    def __init__(self, cmd, timeout):
        threading.Thread.__init__(self)
        self.cmd = cmd
        self.timeout = timeout

    def run(self):
        self.p = sub.Popen(self.cmd)
        self.p.wait()

    def Run(self):
        self.start()
        self.join(self.timeout)

        if self.is_alive():
            self.p.terminate()      #use self.p.kill() if process needs a kill -9
            self.join()

class BaseInstrument():
    # app是一个App类实例
    def __init__(self, app):
        self.app = app
        self.span = 3
        self.wait = 8

    def run(self):
        #子类实现
        pass

    def stop(self):
        #子类实现
        pass


class Paladin_s(BaseInstrument):
    def __init__(self, app, target):
        BaseInstrument.__init__(self, app)
        self.target_activity = target
        self.od = os.getcwd()
        # paladin所在目录
        self.wd = paladin_dir

    def run(self):
        # 读取json文件，改掉package和target_activity，然后运行
        os.chdir(self.wd)
        config_path = self.wd + 'config.json'
        from util import logger
        if(os.path.isfile(config_path)) :
            config = json.load(open(config_path))
            config["DEVICES"][0]["SERIAL"] = self.app.serial    #序列号
            config["PACKAGE"] = self.app.package                #package
            config["TARGET_ACTIVITY"] = self.target_activity
            json.dump(config, open(config_path,'w'), indent = 4)
            logger.info("paladin-s config complete, start testing...")
            self.instance = RunCmd(['java', '-jar', 'paladin-1.0.jar','-s'])
            self.instance.start_run()
        else:
            logger.error("error! can not find config.json in :" + config_path)
    
    def stop(self):
        self.clean()
        self.instance.stop_run()
    
    def is_alive(self):
        serial = self.app.serial
        result = os.popen("curl http://127.0.0.1:5700/finish?serial="+serial).read()
        #print('======================')
        #print("result:",result)
        #print('======================')
        return result == 'no'

    def save_graph(self):
        result = os.popen("curl http://127.0.0.1:5700/save").read()
        package = self.app.package
        old_dir = paladin_dir + "graph-" + package + ".json"
        new_dir = paladin_dir + "output/" + package + "/graph-" + package + ".json"
        time.sleep(3)
        result = os.popen("mv " + old_dir + " " + new_dir).read()
        print("save graph")

    def clean(self):
        # stop()会调用clean()
        # print("clean!!")
        package = self.app.package
        graph_dir = paladin_dir + "graph-" + package + ".json"
        stacks_dir = paladin_dir + "stacks-" + package + ".json"
        result = os.popen("rm -f " + graph_dir).read()
        result = os.popen("rm -f " + stacks_dir).read()
        

class Paladin(BaseInstrument):
    def __init__(self, app):
        BaseInstrument.__init__(self, app)
        self.od = os.getcwd()
        # paladin所在目录
        self.wd = paladin_dir
        self.span = 10
        self.wait = 4

    def run(self):
        # 这里请改成启动paladin的方式
        # 即读取json文件，改掉package，然后运行
        os.chdir(self.wd)
        config_path = self.wd + 'config.json'
        if(os.path.isfile(config_path)) :
            config = json.load(open(config_path))
            config["DEVICES"][0]["SERIAL"] = self.app.serial   #序列号
            config["PACKAGE"] = self.app.package        #package
            json.dump(config, open(config_path,'w'), indent = 4)
            print("paladin config complete, start testing...")
            self.instance = RunCmd(['java', '-jar', 'paladin.jar', '-m'])
            self.instance.start_run()
        else:
            print("error! can not find config.json in :" + config_path)
        
        # self.instance = RunCmd(['java', '-jar', 'paladin.jar'])
        # self.instance.start_run()

    def stop(self):
        self.clean()
        self.instance.stop_run()

    def is_alive(self):
        serial = self.app.serial
        result = os.popen("curl http://127.0.0.1:5700/finish?serial="+serial).read()
        return result == 'no'
        # 以前的设计
        #rp = requests.get(self.ip + '/finish')
        #if 'Run' in rp.content.decode():
        #    return True
        #else:
        #    return False

        # 这里可参考以前的设计判断程序是否还在运行
        # 增加一个接口提供询问服务

    def save_graph(self):
        result = os.popen("curl http://127.0.0.1:5700/save").read()
        package = self.app.package
        old_dir = paladin_dir + "graph-" + package + ".json"
        new_dir = paladin_dir + "output/" + package + "/graph-" + package + ".json"
        time.sleep(3)
        result = os.popen("mv " + old_dir + " " + new_dir).read()
        print("save graph")

    def clean(self):
        #stop()会调用clean()
        print("clean!!")
        package = self.app.package
        graph_dir = paladin_dir + "graph-" + package + ".json"
        stacks_dir = paladin_dir + "stacks-" + package + ".json"
        result = os.popen("rm -f " + graph_dir).read()
        result = os.popen("rm -f " + stacks_dir).read()


class Monkey(BaseInstrument):
    def run(self):
        os.system('adb -s ' + self.app.serial + ' shell monkey -p ' + self.app.package + ' --throttle 1000 -v 10000 --ignore-crashes --ignore-timeouts --ignore-security-exceptions >/dev/null &')

    def stop(self):
        query_monkey = os.popen('adb -s ' + self.app.serial + ' shell ps | grep monkey').read().strip().split()
        if len(query_monkey) > 2:
            app_pid = query_monkey[1]
            os.system('adb -s ' + self.app.serial + ' shell kill ' + app_pid)
            time.sleep(3)

    def is_alive(self):
        re = os.popen('adb -s ' + self.app.serial + ' shell ps | grep monkey').readlines()
        if len(re) > 0:
            return True
        else:
            return False

class PUMA(BaseInstrument):
    def __init__(self, app):
        BaseInstrument.__init__(self, app)
        self.od = os.getcwd()
        self.span = 5
        self.wait = 15
        self.wd = '/home/ubuntu-123456/Desktop/testAndroid/box/tools/PUMA'
        self.applabel = os.popen("aapt d badging " + self.app.apkpath + "| grep application-label: | awk -F: '{print $2}'").read().strip()
        os.system('echo ' + self.app.package + ' > ' + self.wd + '/app.info')
        if self.app.package == 'com.iconology.comics':
            os.system('echo comiXology >> ' + self.wd + '/app.info')
        else:
            os.system('echo ' + self.applabel + ' >> ' + self.wd + '/app.info')

    def run(self):
        os.chdir(self.wd)
        os.system('./setup-phone.sh')
        self.p = sub.Popen('./run.sh', shell=True, stdout=sub.DEVNULL, stderr=sub.DEVNULL)

    def stop(self):
        self.p.kill()
        os.chdir(self.od)
        #os.system("for pid in $(ps aux| grep 'adb shell' | awk '{print $1}'); do kill -9 $pid; done")
        pid = getHostPid('"adb shell"')
        if pid != 0:
            print('kill ' + pid)
            os.system('kill -9 ' + pid)

    def is_alive(self):
        re = os.popen('ps aux | grep haos | grep adb').readlines()
        print(re)
        if len(re) > 1:
            return True
        else:
            return False

    
class Droidbot(BaseInstrument):
    def __init__(self, app):
        BaseInstrument.__init__(self, app)
        self.wait = 10
        self.instance = RunCmd(["droidbot", "-a", self.app.apkpath, "-d", self.app.serial, "-o", "output/", "-keep_env", "-keep_app"])
    def run(self):
        #droidbot -a /home/mike/togithub/testAndroid/Stoat/Stoat/apks/akai.floatView.op.luffy.apk -o output/ -keep_env
        self.instance.start_run()

    def stop(self):
        self.instance.stop_run()        
        os.system("for pid in $(ps | grep adb | awk '{print $1}'); do kill -9 $pid; done")
        time.sleep(3)

    def is_alive(self):
        re = os.popen('ps aux | grep droidbot').readlines()
        print(re)
        if len(re) > 2:
            return True
        else:
            return False



class Stoat(BaseInstrument):
    def __init__(self, app):
        BaseInstrument.__init__(self, app)
        #ruby run_stoat_testing.rb --app_dir /home/mike/togithub/testAndroid/Stoat/Stoat/apks/com.blizzard.wtcg.hearthstone.apk --avd_name mike --avd_port 5554 --stoat_port 2000
        #script_path = '/home/mike/togithub/testAndroid/Stoat/Stoat/bin/run_stoat_testing.rb'
        #script_path = '/home/internetware/test/instruments/Stoat/Stoat/bin/run_stoat_testing.rb'
        #ruby run_stoat_testing.rb --app_dir /home/ubuntu-123456/Desktop/testAndroid/box/subjects/com.evancharlton.mileage_3110_src/ --real_device_serial ZX1G22NNM6 --stoat_port 2000 --project_type ant
        script_path = '/home/ubuntu-123456/Desktop/testAndroid/Stoat/Stoat/bin/run_stoat_testing.rb'
        #self.ant = '/home/ubuntu-123456/Desktop/testAndroid/androtest/subjects/' + self.app.package
        serial = self.app.serial
        self.instance = RunCmd(['ruby', script_path, '--app_dir', self.app.apkpath, '--real_device_serial', serial, '--stoat_port', '2000'])
        #self.instance = RunCmd(['ruby', script_path, '--app_dir', self.ant, '--real_device_serial', serial, '--stoat_port', '2000', '--project_type', 'ant'])
        self.wait = 20

    def run(self):
        self.instance.start_run()

    def stop(self):
        self.instance.stop_run()
        
    def is_alive(self):
        re = os.popen('ps aux | grep ruby').readlines()
        #print(re)
        if len(re) > 2:
            return True
        else:
            return False

class Sapienz(BaseInstrument):
    def __init__(self, app):
        BaseInstrument.__init__(self, app)
        self.od = os.getcwd()
        self.span = 2
        self.wait = 15
        self.wd = '/home/internetware/test/instruments/sapienz/'
        os.chdir(self.wd)
        self.instance = RunCmd(['python2', 'main.py', self.app.apkpath])

    def run(self):
        self.instance.start_run()

    def stop(self):
        self.instance.stop_run()
        hpid = getHostPid('main.py')
        if hpid != '0':
            os.system('kill -9 ' + hpid)

        hpid = getHostPid('main.py')
        if hpid != 0:
            os.system('kill -9 ' + hpid)

        time.sleep(2)
        pid = getPid('com.android.commands.motifcore', self.app.serial)
        if pid != '0':
            os.system('adb shell kill ' + pid)
        os.chdir(self.od)

    def is_alive(self):
        re = os.popen('ps aux | grep main.py | grep python').readlines()
        #print(re)
        if len(re) > 1:
            return True
        else:
            return False

#instruments = {'monkey' : monkey, 'sapienz' : sapienz, 
               #'droidbot' : droidbot, 'stoat' : stoat}

instruments = {'monkey' : Monkey, 'droidbot' : Droidbot, 'stoat' : Stoat, 'sapienz' : Sapienz, 'puma' : PUMA, 'paladin' : Paladin, 'paladin-s': Paladin_s } 



if __name__ == '__main__':
    # monkey = Monkey('akai.floatView.op.luffy')
    # monkey.run()
    # time.sleep(5)
    # monkey.stop()
    pass