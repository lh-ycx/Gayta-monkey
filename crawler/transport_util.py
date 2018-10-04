import paramiko
import os


host = '162.105.175.241'
port = 22
username = 'pku'
password = 'pku2018!))$'
remote_dir = './Documents/data/'
local_dir = './output/'


transport = paramiko.Transport((host,port))
transport.connect(username=username,password=password)
sftp = paramiko.SFTPClient.from_transport(transport)


# 上传单个文件
def upload_file(local, remote = ''):
    if remote == '':
        remote = local
    sftp.put(local, remote)


# 下载单个文件
def download_file(remote, local = ''):
    if local == '':
        local = remote
    sftp.get(remote, local)


# 上传文件夹
def upload_dir(local, remote):
    try:
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
    except Exception as e:
        print(e)
            

# 上传某个app的数据
def upload_app(package_name):
    upload_dir(local_dir + package_name, remote_dir)


if __name__ == "__main__" :
    upload_file('spam.log', remote_dir+'spam.log')
    upload_app('com.douban.movie')