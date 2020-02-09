from util.ReadConfig import get_config_parser
import logging
from util.ssh.SSHClient import SSHClient
import sys
import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
sections_map = get_config_parser("local_config_ht.ini")
run_datetime = 'r' + datetime.datetime.now().strftime('%m%d-%H%M%S')
sys_date = 's0206-'
# step = 'ExportData-'
# step = 'ImportConfirm-'
step = 'DealData-'

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
    cmd1 = 'cd ' + items['deploy_path']
    cmd2 = r'nohup sh ' + items.get('start_shell',
                                    'start.sh') + r'>./logs/nohup-' + step + sys_date + run_datetime + r'.log 2>&1 &'
    cmd = cmd1 + " && " + cmd2
    logger.debug("cmd:" + cmd)
    client.exec_cmd_nb(cmd)


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


def start_all():
    service_list = sections_map['seepp']['services'].split('|')
    logger.info("all services to start:" + ','.join(service_list))
    for service in service_list:
        start(service)


def stop_all():
    service_list = sections_map['seepp']['services'].split('|')
    logger.info("all services to stop:" + ','.join(service_list))
    for service in service_list:
        stop(service)


if __name__ == '__main__':
    start_all()
    # stop_all()
    # start('finlcs-181-1')
    # stop('finlcs-181-1')


    # if (sys.argv[1] == 'start'):
    #     start_all()
    # if (sys.argv[1] == 'stop'):
    #     stop_all()
