# _*_coding:utf-8_*_
# from django.conf import settings
# import libManager.common.util.LoggerManager
import sys
import logging
from util.ReadConfig import get_config_parser
from util.ssh import SSHClient
from util.os import OsUtil
from util.db.pymysql_builder import PyMysqlFactory

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


def test_ssh_client():
    sections_map = get_config_parser("local_config_puyin.ini")
    items = sections_map['fintcs-query-service']
    logger1.info("connect via ssh:" + items['host'] + "," + items['user'])
    client = SSHClient.SSHClient(items['host'], items['user'], items['password'], 22)
    ssh = getattr(client, 'sshClient')
    sftp = getattr(client, 'sftpClient')

    # stdin, stdout, stderr = ssh.exec_command('pwd;date')
    # res = stdout.read() + stderr.read()
    # print(res.decode())

    client.exec_cmd('date')


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


if __name__ == '__main__':
    # print("BASE_DIR:" + settings.BASE_DIR)
    # logger = libManager.common.util.LoggerManager.get_logger()
    # logger.debug("debug log")
    # logger.info("info log")
    # logger.error("error log")
    # print ('date -s "'+sys.argv[1]+'"')
    # test_read_config()
    # test_ssh_client()
    # test_osutil()
    test_pymysql()
