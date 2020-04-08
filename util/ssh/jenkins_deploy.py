"""
@author:  shiwx27477
@createtime:  2020/4/7 09:32
"""
import zipfile

from util.file import file_util
from util.ssh.ssh_client import SSHClient
import logging
import os
import shutil
import sys
import time

# TODO:修改读取配置的类
# TODO:springboot不能写死
# TODO:交易和查询放在同一个目录下，查找时需要加关键字区分
# TODO:可能是jar，也可能是war
CFG_FILE = 'local_config_puyin.ini'

# init logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# read config
# sections_map = ReadConfig.get_config_parser("local_config_ht.ini")
sections_map = file_util.LoadConfig.get_config_parser(CFG_FILE)


class JenkinsDeployer:
    __TMP_BASE_DIR = r'D:/swx/1_hundsun/tmp'
    __jar_name = ''

    def __init__(self, app_name):
        self.app_name = app_name
        self.items = sections_map[app_name]
        self.client = SSHClient(self.items['host'], self.items['user'], self.items['password'], self.items['ssh_port'])
        self.pkg_items = sections_map['pkg_server']
        self.pkg_client = SSHClient(self.pkg_items['host'], self.pkg_items['user'], self.pkg_items['password'],
                                    self.pkg_items['ssh_port'])

    # start deploy
    def deploy(self):
        # 1.find latest zip file
        pkg_base_dir = self.items['pkg_base_dir']
        local_tmp_dir = self.__TMP_BASE_DIR + '/' + self.app_name
        latest_pkg_dir = self.pkg_client.find_latest_dir(pkg_base_dir)
        if latest_pkg_dir:
            logger.debug('the latest pkg dir is:' + latest_pkg_dir)
            remote_latest_file_name = self.pkg_client.find_latest_file(pkg_base_dir + '/' + latest_pkg_dir)

        if remote_latest_file_name:
            remote_latest_file_path = pkg_base_dir + '/' + latest_pkg_dir + '/' + remote_latest_file_name
            logger.info('the latest remote zip file path:' + remote_latest_file_path)

            # recreate local tmp dir
            if os.path.exists(local_tmp_dir):
                shutil.rmtree(local_tmp_dir)
            os.mkdir(local_tmp_dir)

            # 2.download zip file from remote to local tmp dir
            logger.info("STEP:download zip file from remote to local tmp dir")
            local_zip_path = local_tmp_dir + '/' + remote_latest_file_name
            logger.info('local_zip_path:%s' % local_zip_path)
            self.__download(remote_latest_file_path, local_zip_path)

            # 3.unzip
            logger.info("STEP:extract jar file from zip file")
            self.__unzip(local_zip_path, local_zip_path.replace(r'.zip', ''))

            # 4.deploy jar to remote server
            logger.info("STEP:deploy jar to remote server")
            self.__jar_name = os.listdir(local_zip_path.replace(r'.zip', '') + r'/application')[0]
            local_jar_path = os.path.join(local_zip_path.replace(r'.zip', ''), 'application', self.__jar_name)
            remote_jar_path = self.items['deploy_path'] + '/springboot/application/' + self.__jar_name
            logger.debug("local jar name:%s" % self.__jar_name)
            logger.debug("local jar path:%s" % local_jar_path)
            logger.debug("remote jar path:%s" % remote_jar_path)
            self.__upload(local_jar_path, remote_jar_path)

            # 5.update remote start shell
            logger.info("STEP:begin to edit start shell")
            self.__update_remote_start_shell()

            # 6.restart service
            self.__restart_remote_service()

    # unzip file
    def __unzip(self, zip_path, extract_dir):
        """
        unzip zipfile to designated dir
        @param zip_path:
        @type zip_path: string
        @param extract_dir: string
        @type extract_dir: extract dir,file name appended
        @return:
        @rtype:
        """
        zf = zipfile.ZipFile(zip_path, 'r')
        zf.extractall(extract_dir)
        zf.close()

    def __upload(self, local_jar, remote_jar):
        self.client.sftp_put(local_jar, remote_jar)

    def __download(self, remote_file, local_file):
        """
        download deploy package from remote server
        @param remote_file: remote pkg path,cannot be dir
        @type remote_file:
        @param local_file: local pkg path,cannot be dir
        @type local_file:
        @return:
        @rtype:
        """
        self.pkg_client.sftp_get(remote_file, local_file)

    def __update_remote_start_shell(self):
        """
        update jar name in starter shell
        @param jar_name:
        @type jar_name:
        @return:
        @rtype:
        """
        cmd = r'sed -i "s/%s.*\.(j|w)ar$/%s/g" %s/springboot/%s'
        self.client.exec_cmd(
            cmd % (self.items['app_name'], self.__jar_name, self.items['deploy_path'], self.items['start_shell']))

    def __restart_remote_service(self):
        """
        restart service
        @return:
        @rtype:
        """
        cmd1 = 'ps -ef|grep %s|grep -v grep|cut -c 9-15|xargs kill -9'
        cmd2a = 'cd ' + self.items['deploy_path'] + '/springboot'
        cmd2b = 'nohup sh %s>%s/nohup-$(date "+%%Y%%m%%d-%%H%%M%%S").log 2>&1 &'
        cmd2 = cmd2a + " && " + cmd2b
        self.client.exec_cmd(cmd1 % self.items['app_name'])
        self.client.exec_cmd_nb(cmd2 % (self.items['start_shell'], self.items['log_path']))
