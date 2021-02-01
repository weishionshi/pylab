import paramiko
import threading
import os
import stat
from util.os.os_util import get_all_files_in_local_dir
from util.logging.logger_manager import LoggerFactory

logger = LoggerFactory(__name__).get_logger()

class SSHClient:

    def __init_ssh_client(self):
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
        return ssh

    def __init_sftp_client(self):
        sf = paramiko.Transport((self.host, int(self.port)))
        sf.connect(username=self.username, password=self.password)
        sftp = paramiko.SFTPClient.from_transport(sf)
        return sftp

    def __init__(self, host, username, password, port=22):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.sshClient = self.__init_ssh_client()
        self.sftpClient = self.__init_sftp_client()
        super(SSHClient, self).__init__()

    def __del__(self):
        self.sshClient.close()
        self.sftpClient.close()

    def exec_cmd(self, cmd):
        stdin, stdout, stderr = self.sshClient.exec_command(cmd)
        channel = stdout.channel
        status = channel.recv_exit_status()
        logger.info("-" * 60)
        logger.info("host: [%s],   command: [%s]\n" % (self.host, cmd))
        logger.info(stdout.read().decode())
        logger.info(stderr.read().decode())
        logger.info("exit status: %d" % status)
        logger.info("-" * 60)

    # 没有返回值，执行后台命令时不会阻塞
    def exec_cmd_nb(self, cmd):
        transport = self.sshClient.get_transport()
        channel = transport.open_session()
        channel.exec_command(cmd)
        logger.info("-" * 60)
        logger.info("host: [%s],  transport command: [%s]\n" % (self.host, cmd))
        logger.info("-" * 60)

    # get单个文件
    # 注意remotefile, localfile一定是文件，不能是目录,localfile指定本地将要保存的文件名，可以与remotefile的名字不一样
    def sftp_get(self, remotefile, localfile):
        self.sftpClient.get(remotefile, localfile)

    # put单个文件.如果远端文件已存在则覆盖
    # 注意：两个入参都必须是文件，而不能是目录，否则报错
    def sftp_put(self, localfile, remotefile):
        self.sftpClient.put(localfile, remotefile)

    # put all files in local dir to remote dir
    def sftp_put_dir(self, local_dir, remote_dir):

        # 去掉路径字符穿最后的字符'/'，如果有的话
        if remote_dir[-1] == '/':
            remote_dir = remote_dir[0:-1]

        # 如果目录不存在，那么创建
        if not self.check_if_dir_exist(remote_dir=remote_dir):
            logger.info('远端 [%s] 目录不存在,程序先创建' % remote_dir)
            self.sshClient.exec_command('mkdir -p ' + remote_dir)

        # 获取本地指定目录及其子目录下的所有文件
        all_files = get_all_files_in_local_dir(local_dir)
        # 依次put每一个文件
        for file in all_files:
            filename = os.path.split(file)[-1]
            remote_filename = remote_dir + '/' + filename
            logger.info(u'Put文件[%s]，传输中...' % filename)
            self.sftpClient.put(file, remote_filename)
            logger.info('put success:from local [' + file + '] to remote [' + remote_filename + ']')

    def check_if_dir_exist(self, remote_dir):
        stdin, stdout, stderr = self.sshClient.exec_command('ls ' + remote_dir)
        if stdout.readline() != '':
            return True
        else:
            return False

    # get latest modified folder,not the full dir,just the single folder name
    def find_latest_dir(self, base_dir):
        cmd = 'ls ' + base_dir + ' -lt|grep ^d|head -1'
        stdin, stdout, stderr = self.sshClient.exec_command(cmd)
        stdout_str = stdout.read().decode()
        stderr_str = stderr.read().decode()
        self.__print_exec_result(cmd, stdout_str, stderr_str)

        if stdout.channel.recv_exit_status() == 0 and stdout_str != '':
            return stdout_str.split(' ')[-1].replace('\n', '').replace('\r', '')
        else:
            return False
        # TODO,异常处理

    # get latest modified file name
    def find_latest_file(self, base_dir):
        cmd = 'ls ' + base_dir + ' -lt|grep ^-|head -1'
        stdin, stdout, stderr = self.sshClient.exec_command(cmd)
        stdout_str = stdout.read().decode()
        stderr_str = stderr.read().decode()
        self.__print_exec_result(cmd, stdout_str, stderr_str)

        if stdout.channel.recv_exit_status() == 0 and stdout_str != '':
            return stdout_str.split(' ')[-1].replace('\n', '').replace('\r', '')
        else:
            return False
        # TODO,异常处理

    def sftp_find_latest_dir(self, base_dir):
        """
        find the newest dir under base_dir via sftp apis,based on modify time
        @param base_dir:
        @type base_dir:
        @return: latest dir name
        @rtype: string
        """
        f_list = self.sftpClient.listdir_attr(base_dir)

        max_mtime = 0
        for file in f_list:
            # 判断远程文件是不是文件夹
            if stat.S_ISDIR(file.st_mode):
                if file.st_mtime > max_mtime:
                    max_mtime = file.st_mtime
                    latest_dir = file.filename
                else:
                    continue
        return latest_dir

    def sftp_find_latest_file(self, base_dir):
        """
        find the newest filename under base_dir via sftp apis,based on modify time
        @param base_dir:
        @type base_dir:
        @return: file name
        @rtype: string
        """
        f_list = self.sftpClient.listdir_attr(base_dir)
        latest_f_name = ''
        max_mtime = 0
        for file in f_list:
            # 判断远程文件是不是文件夹
            if stat.S_ISREG(file.st_mode):
                if file.st_mtime > max_mtime:
                    max_mtime = file.st_mtime
                    latest_f_name = file.filename
                else:
                    continue
        return latest_f_name

    # print exec result
    @staticmethod
    def __print_exec_result(self, cmd, stdout, stderr):
        logger.info("-" * 60)
        logger.info("host: [%s],   command: [%s]\n" % (self.host, cmd))
        logger.info('stdout:' + stdout)
        logger.info('stderr:' + stderr)
        logger.info("-" * 60)


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
        logger.info("*" * 60)
        logger.info("ip:%s,   command:%s,\n" % (self.host, self.command))
        logger.info(stdout.read().decode())
        logger.info("*" * 60)
        ssh.close()
