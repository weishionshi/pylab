import threading
from datetime import datetime

import paramiko
import os
import sys
from util.file import file_util
from util.logging.logger_manager import LoggerFactory
from util.ssh.ssh_client import ParamikoThreading

logger = LoggerFactory(__name__).get_logger()
BASE_DIR = os.path.dirname(os.getcwd())
sys.path.append(BASE_DIR)

# read config
sections_map = file_util.LoadConfig.get_config_parser("local_config_pu1.ini")
service_list = sections_map['seepp']['services'].split('|')


def set_date():
    try:
        #command = 'date -s "'+sys.argv[1]+'"'
        time = datetime.now().strftime('%H:%M:%S')
        command = 'date -s "20201010 %s"' % time
    except IndexError:
        logger.info('ERROR:please append datetime as param,e.g. SetDate "20191111 12:00:30"')
        #TODO:报错：logger.error('ERROR:please append datetime as param,e.g. set_date "20191111 12:00:00"')
    else:
        t_pool = []
        for service in service_list:
            items = sections_map[service]
            t = paramikoThreading(
                host=items.get("host", "localhost"),
                username=items.get("user", "root"),
                password=items.get("password", "123456"),
                command=command
            )
            t_pool.append(t)
        for t in t_pool:
            t.start()
        for t in t_pool:
            t.join()

def get_date():
    try:
        command = 'date +"%Y-%m-%d %H:%M:%S" '
    except IndexError:
        logger.info('ERROR:please append datetime as param,e.g. SetDate "20191111 12:00:30"')
    else:
        t_pool = []
        for service in service_list:
            items = sections_map[service]
            t = ParamikoThreading(
                host=items.get("host", "localhost"),
                username=items.get("user", "root"),
                password=items.get("password", "123456"),
                command=command
            )
            t_pool.append(t)
        for t in t_pool:
            t.start()
        for t in t_pool:
            t.join()


if __name__ == '__main__':
    # set date in parallel
    # set_date()
    get_date()
