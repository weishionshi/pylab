# _*_coding:utf-8_*_
from django.conf import settings
from util.logging.logger_manager import LoggerFactory
import time
import logging
from util.ReadConfig import get_config_parser

from util.ssh import ssh_client
from util.os import OsUtil
from util.db.pymysql_builder import PyMysqlFactory
from util.file import file_util
import telnetlib
import zipfile
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger1 = logging.getLogger(__name__)


def test_read_config():
    sections_map = get_config_parser("local_config_puyin.ini")
    print(sections_map)


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
    local_dir = 'D:/swx/temp'
    remote_dir = '/提交测试目录/销售系统/交易/V2020XX'
    client = ssh_client.SSHClient('192.168.76.184', 'root', 'caifu@123', 22)
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
        unzip(local_zip_path,local_dir)


def unzip(file_path,extract_dir):
    zf = zipfile.ZipFile(file_path,'r')
    zf.extract(file_path,extract_dir)
    zf.close()


def test_osutil():
    local_dir = r'D:\logs'
    logger1.info("file list:")
    logger1.info(OsUtil.get_all_files_in_local_dir(local_dir))


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
    logger = LoggerFactory('seepp').get_logger()
    logger.debug("debug log")
    logger.info("info log")
    logger.error("error log")


def test_os_path():
    print(os.path.dirname(os.path.abspath(__file__)))
    print(os.path.dirname(os.path.abspath('..')))


if __name__ == '__main__':
    # print("BASE_DIR:" + settings.BASE_DIR)

    # print ('date -s "'+sys.argv[1]+'"')
    # test_read_config()
    # test_fetch_pkg()
    unzip(r'/root/tmp/FS50-FINFSS-QUERY-SERVICE.zip',r'/root/tmp')
    # test_osutil()
    # test_pymysql()
    # test_datetime()
    # test_list()
    # test_telnet()
    # test_logger()
    # test_os_path()
