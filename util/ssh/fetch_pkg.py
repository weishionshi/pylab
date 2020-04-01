from util.file import file_util
from util.ssh.ssh_client import SSHClient
import logging
import paramiko
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

# get remote package path based on service
def get_remote_dir():
    # 1.find the latest folder

    # 2.find the latest package


def download_pkg(service_name):
    sftp = init(service_name)
    remote_dir = get_remote_dir()
    try:
        # sftp.get('/提交测试目录/销售系统/脚本/标准库脚本/oracle/02_基金行业/FS5.0-FINFSS-LCS-STDLIB-ORACLE-02-5.1.2.0.sql','/tmp/test.sql')
        sftp.get(remote_dir, 'D:\\test.sql')
    except Exception as e:
        logger.error('download exception:' + e.__str__())
    sftp.close()


# @func: init sftp client of code server
def init():
    # get env info of code server
    items = sections_map['code_server_182']

    # get trasnsport
    transport = paramiko.Transport((items['host'], items['ftp_port']))
    # connect
    transport.connect(username=items['user'], password=items['password'])

    return paramiko.SFTPClient.from_transport(transport)


if __name__ == '__main__':
    if sys.argv[1] == '':
        logger.error('请指定环境信息，例如fetch_pkg fintcs')
    else:
        download_pkg(sys.argv[1])
