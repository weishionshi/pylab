import threading
import paramiko
import os
import sys
from util.file import file_util
from util.logging import logger_manager

# logger = logger_manager.LoggerFactory().get_logger()
BASE_DIR = os.path.dirname(os.getcwd())
sys.path.append(BASE_DIR)

# read config
sections_map = file_util.LoadConfig.get_config_parser("local_config_ht.ini")
service_list = sections_map['seepp']['services'].split('|')


class paramikoThreading(threading.Thread):
    def __init__(self, command, host, username, password, port=22):
        self.command = command
        self.host = host
        self.username = username
        self.password = password
        self.port = port

        super(paramikoThreading, self).__init__()

    def run(self):
        ssh = paramiko.SSHClient()
        # 创建一个ssh的白名单
        know_host = paramiko.AutoAddPolicy()
        # 加载创建的白名单
        ssh.set_missing_host_key_policy(know_host)

        # 连接服务器
        ssh.connect(
            hostname=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
        )

        stdin, stdout, stderr = ssh.exec_command(self.command)
        print("*" * 60)
        print("ip:[%s],   command:[%s],\n" % (self.host, self.command))
        print(stdout.read().decode())
        print("*" * 60)
        ssh.close()


def set_date():
    try:
        # command = 'date -s "'+sys.argv[1]+'"'
        command = 'date -s "20200302 10:49:30"'
    except IndexError:
        print('ERROR:please append datetime as param,e.g. SetDate "20191111 12:00:20"')
        #报错：logger.error('ERROR:please append datetime as param,e.g. SetDate "20191111 12:00:00"')
    else:
        t_pool = []
        for service in service_list:
            items = sections_map[service]
            t = paramikoThreading(
                host=items.get("host", "localhost"),
                username=items.get("user", "root"),
                password=items.get("password", "caifu@123"),
                command=command
            )
            t_pool.append(t)
        for t in t_pool:
            t.start()
        for t in t_pool:
            t.join()


if __name__ == '__main__':
    # set date in parallel
    set_date()
