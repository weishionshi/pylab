# from util.ReadConfig import get_config_parser
# from util import ReadConfig
from util.file import file_util
from util.ssh.ssh_client import SSHClient
from util.db.pymysql_builder import PyMysqlFactory
import logging
from util import log_color
import datetime

# globle var
TENANT = 'puyin'
CFG_FILE = 'local_config_' + TENANT + '.ini'
PKG_VERSION = 'fintcs-query-service-5.1.2.0-SNAPSHOT'
BATCH_NO = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
RUN_DATETIME = 'r' + datetime.datetime.now().strftime('%m%d-%H%M%S')
REMOTE_NMON_DIR = r'/usr/local/nmon'
LOCAL_NMON_DIR = r'D:\software\nmon'

# 接口名
intf_name = 'GeRenKaiHu-'
desc = intf_name + 'debug'

nmon_cnt = '10'
sys_date = 's1109-'

# init logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# read config
# sections_map = ReadConfig.get_config_parser("local_config_ht.ini")
sections_map = file_util.LoadConfig.get_config_parser(CFG_FILE)

# init mysql connection
db_url = sections_map['seepp']['db_url']
db_user = sections_map['seepp']['db_user']
db_pwd = sections_map['seepp']['db_pwd']
db_name = sections_map['seepp']['db_name']
builder = PyMysqlFactory(db_url, db_user, db_pwd, db_name)
conn = builder.get_connection()
sql = """INSERT INTO seeppt_exec_log (vc_tenant_id,vc_batch_no,vc_cmd, vc_host, vc_srv_log_dir, vc_nmon_dir, vc_exec_datetime, vc_desc,vc_pkg_version)
    VALUES (%s,%s,%s, %s, %s, %s, %s, %s,%s);"""


def start(service_name):
    # get connfig based on service_name
    items = sections_map[service_name]

    # init ssh client
    logger.info("connect via ssh:" + items['host'] + "," + items['user'])
    client = SSHClient(items['host'], items['user'], items['password'], 22)

    # run start.sh
    # 这种写法，如果没有取到 start_shell，就会报错
    # cmd = r'sh ' + items['deploy_path'] + r'/' + items['start_shell']

    # 这种写法，如果没有取到 start_shell，会用默认值，不会报错
    # cmd = r'sh ' + items['deploy_path'] + r'/' + items.get('start_shell', 'start.sh')
    # nohup sh startFSDPL_BOOT.sh>./logs/nohup-s0203-r0204-$(date "+%H%M%S").log 2>&1 &
    log_name = items['log_path'] + r'/' + intf_name + sys_date + RUN_DATETIME + '.log'
    cmd1 = 'cd ' + items['deploy_path']
    cmd2 = r'nohup sh ' + items.get('start_shell',
                                    'start.sh') + r'>' + log_name + r' 2>&1 &'
    cmd = cmd1 + " && " + cmd2
    logger.debug("cmd:" + cmd)
    client.exec_cmd_nb(cmd)

    # insert exec log into db
    logger.info('insert exec log into db:' + db_url + ',' + db_name)
    cursor = conn.cursor()
    try:
        cursor.execute(sql,
                       [TENANT, BATCH_NO, cmd, items['host'], r'tail -f ' + items['deploy_path'] + r'/' + log_name, '',
                        datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), desc, PKG_VERSION])
        conn.commit()
        logger.debug("sql:" + sql)
    except Exception as e:
        conn.rollback()
        logger.error("insert db error")


def stop(service_name):
    # get connfig based on service_name
    items = sections_map[service_name]

    # init ssh client
    logger.info("connect via ssh:" + items['host'] + "," + items['user'])
    client = SSHClient(items['host'], items['user'], items['password'], 22)

    # run stop.sh
    logger.info("run stop shell...")
    # cmd = r'sh ' + items['deploy_path'] + r'/' + items.get('stop_shell', 'stop.sh')
    cmd1 = 'cd ' + items['deploy_path']
    cmd2 = r'sh ' + items.get('stop_shell', 'stop.sh')
    cmd = cmd1 + " && " + cmd2
    logger.debug("cmd:" + cmd)
    client.exec_cmd(cmd)


def restart_nmon(service_name):
    # get config based on service_name
    items = sections_map[service_name]

    # init ssh client
    logger.info("connect via ssh:" + items['host'] + "," + items['user'])
    client = SSHClient(items['host'], items['user'], items['password'], 22)

    # stop nmon first
    cmd = r'ps -ef|grep /home/see/workspace/nmon/nmon|grep -v grep|cut -c 9-15|xargs kill -9'
    logger.debug("exec kill nmon cmd:" + cmd)
    client.exec_cmd(cmd)

    # start nmon
    # e.g.  /home/see/workspace/nmon/nmon -s 3 -c 2400 -F /var/log/ExportData-s0205-r0206-1731.nmon &
    # TODO:判断服务器上是否已经部署了nmon服务，如果没有就通过sftp从本地上传上去
    nmon_file_path = r'/var/log/' + items['host'] + '-' + intf_name + sys_date + RUN_DATETIME + '.nmon'
    cmd = r'/home/see/workspace/nmon/nmon -s 3 -c ' + nmon_cnt + ' -F ' + nmon_file_path + '&'
    logger.debug("start nmon cmd:" + cmd)
    client.exec_cmd_nb(cmd)

    # insert exec log into db
    logger.info('insert exec log into db:' + db_url + ',' + db_name)
    cursor = conn.cursor()
    try:
        cursor.execute(sql, [TENANT, BATCH_NO, cmd, items['host'], items['deploy_path'] + r'/' + '', nmon_file_path,
                             datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '', PKG_VERSION])
        conn.commit()
        logger.debug("sql:" + sql)
    except Exception as e:
        conn.rollback()
        logger.error("insert log into db error")


def stop_nmon(service_name):
    # get connfig based on service_name
    items = sections_map[service_name]

    # init ssh client
    logger.info("connect via ssh:" + items['host'] + "," + items['user'])
    client = SSHClient(items['host'], items['user'], items['password'], 22)

    # stop nmon first
    cmd = r'ps -ef|grep /home/see/workspace/nmon/nmon|grep -v grep|cut -c 9-15|xargs kill -9'
    logger.debug("exec kill nmon cmd:" + cmd)
    client.exec_cmd(cmd)


# TODO:通过sftp把监控文件，日志文件下载到本地
# upload local nmon to remote server
def upload_nmon(service_name):
    # get connfig based on service_name
    items = sections_map[service_name]

    # init ssh client
    logger.info("connect via ssh:" + items['host'] + "," + items['user'])
    client = SSHClient(items['host'], items['user'], items['password'], 22)
    client.sftp_put_dir(LOCAL_NMON_DIR, REMOTE_NMON_DIR)

    # change mode
    client.exec_cmd('chmod -R 775 ' + REMOTE_NMON_DIR)


# upload local nmon to remote server in batch
def upload_all_nmon():
    service_list = sections_map['seepp']['services'].split('|')
    logger.info("all services to deploy nmon:" + ','.join(service_list))
    for service in service_list:
        upload_nmon(service)


def start_all_services():
    service_list = sections_map['seepp']['services'].split('|')
    logger.info("all services to start:" + ','.join(service_list))
    for service in service_list:
        start(service)


def stop_all_services():
    service_list = sections_map['seepp']['services'].split('|')
    logger.info("all services to stop:" + ','.join(service_list))
    for service in service_list:
        stop(service)


def stop_all_nmon():
    service_list = sections_map['seepp']['services'].split('|')
    others_list = sections_map['seepp']['others'].split('|')
    logger.info("all nomn to stop:" + ','.join(service_list) + ',' + ','.join(others_list))
    for service in service_list:
        stop_nmon(service)
    for other in others_list:
        stop_nmon(other)


# 一键启动所有：先启监控,后启服务
def start_in_one():
    nmon_started_list = []
    service_list = sections_map['seepp']['services'].split('|')
    others_list = sections_map['seepp']['others'].split('|')

    # 1.先启动nmon,需要要避免重复启nmon
    for service in service_list:
        items = sections_map[service]
        # 如果已经在此主机上启动过，则跳过，不再启
        if items['host'] in nmon_started_list:
            logger.info("nmon has been started in [%s],skip", items['host'])
            continue
        # 如果没启动过nmon，则启动
        restart_nmon(service)
        nmon_started_list.append(items['host'])

    # 启动nmon，不需要判断重复启的情况
    for other in others_list:
        restart_nmon(other)

    # 2.在启动服务
    start_all_services()


# TODO:改成并发启停
# #########################
# ！！！执行前，先去顶部设置全局变量！！！
# #########################
if __name__ == '__main__':
    upload_all_nmon()
    # stop_all_services()

    # 一键启动所有：先启nmon监控，再起服务
    # start_in_one()

    # restart_nmon('fintcs-query-service-181')
    # restart_nmon('ora11g-172')
    # stop_all_nmon()

    # stop_nmon('mysql-172')
    # stop_nmon('nfs-241')
    # stop_nmon('finlcs-175-1')
    # stop_nmon('finlcs-158-1')
    # stop_nmon('finlcs-200-1')
    # stop_nmon('finlcs-181-1')

# start('finlcs-181-1')
# stop('finlcs-181-1')


# if sys.argv[1] == 'start':
#     start_in_one()
# if sys.argv[1] == 'stop':
#     stop_all()
