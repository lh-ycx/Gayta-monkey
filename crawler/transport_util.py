import paramiko
import os
import requests
import json

from settings import apk_source


host = '162.105.175.241'
port = 22
username = 'pku'
password = 'pku2018!))$'
remote_dir = './Documents/data/' + apk_source + '/'
local_dir = './output/'
remote_apk_dir = './Documents/apk/data/'
if apk_source == 'Google':
    remote_apk_dir += 'GooglePlayApk/'
elif apk_source == 'WDJ':
    remote_apk_dir += 'WDJApk/' 



# 上传单个文件
def upload_file(local, remote = ''):
    transport = paramiko.Transport((host,port))
    transport.connect(username=username,password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    if remote == '':
        remote = local
    sftp.put(local, remote)
    sftp.close()


# 下载单个文件
def download_file(remote, local = ''):
    transport = paramiko.Transport((host,port))
    transport.connect(username=username,password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    if local == '':
        local = remote
    sftp.get(remote, local)
    sftp.close()


# 上传文件夹
def upload_dir(local, remote):
    try:
        transport = paramiko.Transport((host,port))
        transport.connect(username=username,password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        for root, dirs, files in os.walk(local_dir):
            for filespath in files:
                local_file = os.path.join(root,filespath)
                a = local_file.replace(local_dir,'')
                remote_file = os.path.join(remote_dir,a)
                try:
                    sftp.put(local_file,remote_file)
                except Exception as e:
                    sftp.mkdir(os.path.split(remote_file)[0])
                    sftp.put(local_file,remote_file)
                print(local_file + ' uploaded!')
            for name in dirs:
                local_path = os.path.join(root,name)
                a = local_path.replace(local_dir,'')
                remote_path = os.path.join(remote_dir,a)
                try:
                    sftp.mkdir(remote_path)
                    print("mkdir path %s" % remote_path)
                except Exception as e:
                    print(e)
        print('upload finish!')
        sftp.close()
    except Exception as e:
        print(e)
            

# 上传某个app的数据
def upload_app(package_name):
    upload_dir(local_dir + package_name, remote_dir)


# 下载app
def download_app():
    if apk_source == 'Google':
        response = requests.get('http://162.105.175.241:5000/GooglePlayApk/unfinished')
        # print(response.content.decode())
        file_list = json.loads(response.content.decode())[:10]
        # print(file_list)
        for f in file_list:
            try:
                download_file(remote_apk_dir+f,f)
                print("download finish with file: " + f)
                # 在服务器端设置该app为finish状态
                response = requests.get('http://162.105.175.241:5000/GooglePlayApk/finish/'+f)
            except Exception as e:
                print(e)
        
        


if __name__ == "__main__" :
    #upload_file('spam.log', remote_dir+'spam.log')
    #upload_app('com.douban.movie')
    download_app()