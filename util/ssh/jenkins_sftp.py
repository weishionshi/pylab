from util.file import file_util
from util.ssh.ssh_client import SSHClient
import logging
# import paramiko
import os
import sys
import ftplib
import time

CFG_FILE = 'local_config_puyin.ini'

# init logger
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# read config
# sections_map = ReadConfig.get_config_parser("local_config_ht.ini")
sections_map = file_util.LoadConfig.get_config_parser(CFG_FILE)


# def download_pkg(service_name):
#     sftp = init(service_name)
#     try:
#         sftp.get('/提交测试目录/销售系统/脚本/标准库脚本/oracle/02_基金行业/FS5.0-FINFSS-LCS-STDLIB-ORACLE-02-5.1.2.0.sql',
#                  '/tmp/test.sql')
#     except Exception as e:
#         logger.error('download exception:', e)
#     sftp.close()
#
#
# def init(service_name):
#     # get connfig based on service_name
#     items = sections_map[service_name]
#
#     transport = paramiko.Transport((items['host'], 22))  # 获取Transport实例
#     transport.connect(items['user'], items['password'])  # 建立连接
#
#     # 创建sftp对象，SFTPClient是定义怎么传输文件、怎么交互文件
#     return paramiko.SFTPClient.from_transport(transport)


class Ftp:
    ftp = ftplib.FTP()
    ftp.set_pasv(False)

    def __init__(self, host, port=21):
        self.ftp.connect(host, port)

    def login(self, user, passwd):
        self.ftp.login(user, passwd)
        print(self.ftp.welcome)

    def download_file(self, local_file, remote_file):  # 下载指定目录下的指定文件
        file_handler = open(local_file, 'wb')
        print(file_handler)
        # self.ftp.retrbinary("RETR %s" % (remote_file), file_handler.write)#接收服务器上文件并写入本地文件
        self.ftp.retrbinary('RETR ' + remote_file, file_handler.write)
        file_handler.close()
        return True

    def download_dir(self, local_dir, remote_dir):  # 下载整个目录下的文件
        print("remoteDir:", remote_dir)
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)
        self.ftp.cwd(remote_dir)
        remote_names = self.ftp.nlst()
        print("remote_names", remote_names)
        for file in remote_names:
            local = os.path.join(local_dir, file)
            print(self.ftp.nlst(file))
            if file.find(".") == -1:
                if not os.path.exists(local):
                    os.makedirs(local)
                self.download_dir(local, file)
            else:
                self.download_file(local, file)
        self.ftp.cwd("..")
        return True

    # 从本地上传文件到ftp
    # def uploadfile(self, remotepath, localpath):
    #     bufsize = 1024
    #     fp = open(localpath, 'rb')
    #     ftp.storbinary('STOR ' + remotepath, fp, bufsize)
    #     ftp.set_debuglevel(0)
    #     fp.close()

    def close(self):
        self.ftp.quit()


def download_pkg(service_name):
    items = sections_map[service_name]
    ftp = Ftp(items['host'], 1111)
    ftp.login(items['user'], items['password'])
    # ftp.download_file('/tmp/test.sql', '/提交测试目录/销售系统/脚本/标准库脚本/oracle/02_基金行业/FS5.0-FINFSS-LCS-STDLIB-ORACLE-02-5.1.2.0.sql')
    ftp.download_file('/tmp/test.sql', '/tmp/finpss-omms-app/finoss.log')
    ftp.close()


if __name__ == '__main__':
    # download_pkg('fintcs-query-service-181')
    download_pkg('code_server_182')
