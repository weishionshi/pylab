import threading
import paramiko
import sys

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
        print("ip:%s,   command:%s,\n" % (self.host, self.command))
        print(stdout.read().decode())
        print("*" * 60)
        ssh.close()


if __name__ == '__main__':
    # from settings import hosts  # 调用配置文件配置文件为settings.py
    hosts = [#dict(host="192.168.76.158", username="root", password="caifu@123"),
             #dict(host="192.168.76.188", username="root", password="caifu@123"),
             dict(host="192.168.76.175", username="root", password="caifu@123"),
             dict(host="192.168.76.181", username="root", password="caifu@123")
             #dict(host="192.168.76.184", username="root", password="caifu@123")
             ]
    try:
        command = 'date -s "'+sys.argv[1]+'"'
    except IndexError:
        print('ERROR:please append datetime as param,e.g. SetDate "20191111 12:00:00"')
    else:
        t_pool = []
        for host in hosts:
            t = paramikoThreading(
                host=host.get("host", "localhost"),
                username=host.get("username", "root"),
                password=host.get("password", "caifu@123"),
                command=command
            )
            t_pool.append(t)
        for t in t_pool:
            t.start()
        for t in t_pool:
            t.join()
