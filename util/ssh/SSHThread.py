import threading
import paramiko


class ParamikoThreading(threading.Thread):
    def __init__(self, command, host, username, password, port=22):
        self.command = command
        self.host = host
        self.username = username
        self.password = password
        self.port = port

        super(ParamikoThreading, self).__init__()

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

