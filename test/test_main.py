#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author  : shiwx27477
# @time    : 2020/4/14 9:53
# @file    : test_main.py
import unittest
from util.file import file_util
from util.ssh.ssh_client import SSHClient
import logging
import paramiko

CFG_FILE = 'local_config_puyin.ini'
# init logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()


class UnitTest(unittest.TestCase):
    __sections_map = file_util.LoadConfig.get_config_parser(CFG_FILE)
    # __sections_map = {}

    def test_sftp(self):
        remote_path = '/提交测试目录/销售系统/交易/V2020XX'
        items = self.__sections_map['code_server_182']

        transport = paramiko.Transport((items.get('host'), int(items.get('ftp_port'))))
        transport.connect(username=items.get('user'), password=items.get('password'))
        sftp = paramiko.SFTPClient.from_transport(transport)

        # client = SSHClient(items.get('host'), items.get('user'), items.get('password'),
        #                    items.get('ftp_port'))
        # print(client.sftpClient.listdir('/'))
        self.assertIsNotNone(sftp.listdir_attr('/提交测试目录/销售系统/交易/V2020XX'),'cannot be null')
        print(sftp.listdir_attr(remote_path))
        print('stat:' + sftp.stat(remote_path))

    def test_sftp_in_class(self):
        remote_path = '/提交测试目录/销售系统/交易/V2020XX'
        items = self.__sections_map['code_server_182']

        client = SSHClient(items.get('host'), items.get('user'), items.get('password'),
                           items.get('ftp_port'))
        print(client.sftpClient.listdir('/'))
        self.assertIsNotNone(client.sftpClient.listdir_attr('/提交测试目录/销售系统/交易/V2020XX'),'cannot be null')
        print(client.sftpClient.listdir_attr('/提交测试目录/销售系统/交易/V2020XX'))
        print('stat:' + str(client.sftpClient.stat(remote_path)))

    @classmethod
    def setUpClass(cls):
        """
        load config
        @return:
        @rtype:
        """
        # cls.__section_map = file_util.LoadConfig.get_config_parser(CFG_FILE)
        print('__section_map in setUpClass():')

    @classmethod
    def tearDownClass(cls):
        """
        tear down after all testcases finished,run only once
        @return:
        @rtype:
        """
        cls.__section_map = {}

    def test_demo(self):
        test = 'abc'
        self.assertEqual('abc', test)

    def test_ssh_client(self):
        items = self.__sections_map['pkg_server']
        client = SSHClient(items.get('host'), items.get('user'), items.get('password'),
                           items.get('ftp_port'))
        latest_dir = client.find_latest_dir('/提交测试目录/销售系统/交易/V2020XX')
        logger.info('latest dir:' + latest_dir)
        self.assertIsNotNone(latest_dir, 'lastest cannot be null')

    @unittest.skip("skip this case.")
    def test_osutil(self):
        pass


# 可以直接在用例里执行，也可以把用例组织为TestSuite执行
if __name__ == '__main__':
    unittest.main()
