# _*_coding:utf-8_*_
# from django.conf import settings
from util.logging.logger_manager import LoggerFactory
import time
import logging

from util.ssh import ssh_client
from util.os import os_util
from util.db.conn_builder import PyMysqlFactory
from util.file import file_util
import telnetlib
import zipfile
import os
import shutil
from ftplib import FTP
import paramiko

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger1 = logging.getLogger(__name__)

def test_sftp():
    # host = '192.168.76.200'
    # port = 22
    host = '192.168.102.182'
    port = 1111
    transport = paramiko.Transport((host, port))
    username = 'lcfstest'
    password = '831K9FWD'

    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    print(sftp.listdir('/'))
    print(sftp.listdir_attr('/提交测试目录'))


def test_ftplib():
    ftp = FTP()
    ftp.connect(host='192.168.76.200', port=21,timeout=15)  # 连接
    ftp.login(user='root',passwd='caifu@123')  # 登录，如果匿名登录则用空串代替即可
    print(ftp.getwelcome())  # 打印欢迎信息




'''  
    options = cf.options("fintcs-query-service")  # 获取某个section名为fintcs-query-service所对应的键
    print("options:")
    print(options)

    items = cf.items("fintcs-query-service")  # 获取section名为fintcs-query-service所对应的全部键值对
    print("items:")
    print(items)

    host = cf.get("fintcs-query-service", "host")  # 获取[fintcs-query-service]中host对应的值
    print("host:\n" + host)
'''


def test_fetch_pkg():
    local_dir = 'D:/swx/1_hundsun/tmp'
    remote_dir = '/提交测试目录/销售系统/交易/V2020XX'
    client = ssh_client.SSHClient('192.1.1.1', 'username', 'pwd', 22)
    remote_latest_dir = client.find_latest_dir(remote_dir)
    if remote_latest_dir:
        print('result:' + remote_latest_dir)

    remote_latest_file_name = client.find_latest_file(remote_dir + '/' + remote_latest_dir)

    if remote_latest_file_name:
        remote_latest_file_path = remote_dir + '/' + remote_latest_dir + '/' + remote_latest_file_name
        print('remote latest file path:' + remote_latest_file_path)
        # download zip pkg from remote code server
        local_zip_path = local_dir + '/' + remote_latest_file_name
        print('local_zip_path:%s' % local_zip_path)
        client.sftp_get(remote_latest_file_path, local_zip_path)

        # unzip pkg
        unzip(local_zip_path,local_zip_path.replace(r'.zip',''))

        # deploy jar and start shell to remote

def unzip(zip_file_path,extract_dir):
    zf = zipfile.ZipFile(zip_file_path,'r')
    # zf.extract(file_path,extract_dir)
    zf.extractall(extract_dir)
    zf.close()

def test_os():
    files = os.listdir(r'D:/logs')
    logger1.info('files:'+ files[0] + ',' + os.listdir(r'D:/logs')[1])
    join_path = os.path.join("D:/swx/1_hundsun/sftp","application") # TypeError: not all arguments converted during string formatting
    logger1.info("join path:%s" %join_path)
    if os.path.exists(r'D:/swx/1_hundsun/tmp/fintcs-query-service-181'):
        shutil.rmtree(r'D:/swx/1_hundsun/tmp/fintcs-query-service-181')
    os.mkdir(r'D:/swx/1_hundsun/tmp/fintcs-query-service-181')

def test_osutil():
    local_dir = r'D:\logs'
    logger1.info("file list:")
    logger1.info(os_util.get_all_files_in_local_dir(local_dir))


def test_pymysql():
    builder = PyMysqlFactory('127.0.0.1', 'seepp', 'seepp876', 'seepp')
    conn = builder.get_connection()
    sql = """INSERT INTO seepp.seeppt_exec_log (vc_cmd, vc_host, vc_srv_log_dir, vc_nmon_dir, dt_exec_datetime, vc_desc)
        VALUES (%s, '127.0.0.1', 'test2', null, null, null);"""
    v_cmd = 'test cmd2'

    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()

    # 执行SQL语句
    cursor.execute(sql, [v_cmd])

    # 提交事务
    conn.commit()
    cursor.close()


def test_datetime():
    print("time.time(): ", time.time())
    print("time.localtime(time.time()): ", time.localtime(time.time()))
    print("time.asctime(): ", time.asctime())
    print("time.ctime(): ", time.ctime())
    print("time.ctime(0): ", time.ctime(0))


def test_list():
    test_list = ['a', 'b', 'c']
    print(test_list)

    print('test_list.index(''a'')', test_list.index('b'))
    print('test_list.reverse()', test_list.reverse())
    print('d' in test_list)


def test_telnet():
    # result = telnetlib.Telnet('192.168.76.175', '8076')
    result = telnetlib.Telnet('127.0.0.1', '8076')
    print('result', result)


def test_logger():
    # logger = LoggerFactory('seepp').get_logger()
    logger = LoggerFactory(__name__).get_logger()
    logger.debug("debug log")
    logger.info("info log")
    logger.error("error log", exc_info=True) # 等价于logger.exception(msg, _args)
    print(__name__)
    print(__file__)


def test_os_path():
    print(os.path.dirname(os.path.abspath(__file__)))
    print(os.path.dirname(os.path.abspath('..')))


def test_regex():
    cmd = r'sed -i "s/%s.*\.jar$/%s/g" %s/springboot/%s'
    cmd2 = 'nohup sh %s/springboot/%s>%s/nohup-$(date "+%%Y%%m%%d-%%H%%M%%S").log 2>&1 &'
    print(cmd %('fintcs-query-service' ,'fintcs-query-service-1.1.1.jar' ,r'/home/see/workspace/fintcs-query-service','startFSDPL_BOOT.sh'))
    print(cmd2 % ('aaa', 'bbb', 'ccc'))


if __name__ == '__main__':
    # test_sshclient()
    # test_sftp()
    # test_ftplib()
    # print("BASE_DIR:" + settings.BASE_DIR)

    # print ('date -s "'+sys.argv[1]+'"')
    # test_read_config()
    # test_fetch_pkg()
    # unzip(r'D:\swx\temp\FS50-FINFSS-QUERY-SERVICE-V202003-00-000-product-20200331-e4732b2eaaf88d584c4952c28cc9f8447b08857c.zip','application/fintcs-query-service-5.1.3.0-SNAPSHOT.jar',r'D:\swx\temp\fintcs-query-service')
    # test_osutil()
    # test_pymysql()
    # test_datetime()
    # test_list()
    # test_telnet()
    test_logger()
    # test_os_path()
    # test_os()
    # test_regex()
