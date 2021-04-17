#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author  : shiwx
# @time    : 4/10/21 10:44
# @file    : env.py
import cx_Oracle
import redis

from util.db.conn_builder import PyMysqlFactory
from util.file import file_util
from util.logging.logger_manager import LoggerFactory
from util.ssh.ssh_client import SSHClient


class EnvBase(object):
    # init logger
    logger = LoggerFactory(__name__).get_logger()

    # sections_map=None

    def __init__(self, config_path):
        self.config_path = config_path

        # read config
        self.sections_map = file_util.LoadConfig.get_config_parser(config_path, encoding='utf-8')

        # init db connections
        db_sec = self.sections_map.get('seepp').get('db')
        self.db_section = self.sections_map.get(db_sec)
        self.__init_db_conn()

        # init redis connections
        rds_sec = self.sections_map.get('seepp').get('redis')
        self.rds_section = self.sections_map.get(rds_sec)
        self.__init_redis_conn()

    # def __del__(self):
    #     if self.conn_tcs:
    #         self.conn_tcs.close()
    #     if self.conn_lcs:
    #         self.conn_lcs.close()


    def __init_db_conn(self):
        # init db connection
        self.dbms = self.db_section['dbms']
        db_host = self.db_section['host']
        db_port = self.db_section['db_port']
        db_pwd = self.db_section['db_password']
        tcs_db_name = self.db_section['tcs_db_name']
        lcs_db_name = self.db_section['lcs_db_name']
        if self.dbms.lower() == 'mysql' or self.dbms.lower() == 'mariadb':
            db_user = self.db_section['db_user']
            self.conn_tcs = PyMysqlFactory(db_host, int(db_port), db_user, db_pwd, tcs_db_name).get_connection()
            self.conn_lcs = PyMysqlFactory(db_host, int(db_port), db_user, db_pwd, lcs_db_name).get_connection()
        if self.dbms.lower() == 'oracle':
            sid = self.db_section['sid']
            self.conn_tcs = cx_Oracle.connect(tcs_db_name, db_pwd, db_host + ':' + db_port + '/' + sid)
            self.conn_lcs = cx_Oracle.connect(lcs_db_name, db_pwd, db_host + ':' + db_port + '/' + sid)

    def __init_redis_conn(self):
        pool = redis.ConnectionPool(host=self.rds_section['host'],
                                    port=self.rds_section['rds_port'],
                                    password=self.rds_section['rds_password'], decode_responses=True)
        self.rds = redis.Redis(connection_pool=pool, charset='UTF-8', encoding='UTF-8')


class DeployEnv(EnvBase):
    def __init__(self, config_path):
        EnvBase.__init__(self, config_path)

    def update_jdbc(self, srv_name, new_jdbc_dict):
        # init ssh client
        ssh_client = self.__get_ssh_client(srv_name)
        # update jdbc string by sed command
        cmd = 'sed -i '
        ssh_client.exec_cmd(cmd=cmd)
        pass

    def append_config(self, srv_name, file_name, string):
        """
        往指定配置文件里增加配置
        @param srv_name: 服务名
        @param file_name: 配置文件名,相对于配置文件中的deploy_path
        @param string:
        @return:
        """
        config_path = self.sections_map.get(srv_name)['deploy_path'] + '/' + file_name
        self.logger.debug('config path is ' + config_path)
        cmd = 'echo -e \'%s\' >> %s' % (string, config_path)

        ssh_client = self.__get_ssh_client(srv_name)
        ssh_client.exec_cmd(cmd=cmd)

    def update_log_level(self, srv_name, log_level, file_name='springboot/config/log4j2.xml'):
        """
        修改log4j2.xml中的全局日志级别
        <Property name="logging.level">info</Property>
        @param srv_name:
        @param log_level:
        @param file_name: 日志配置文件名,相对于配置文件中的deploy_path
        @return:
        """
        log4j_path = self.sections_map.get(srv_name)['deploy_path'] + '/' + file_name
        cmd = 'sed -i \'s/<Property name="logging.level">.*$/<Property name="logging.level">%s<\\/Property>/g\' %s' % (log_level, log4j_path)
        ssh_client = self.__get_ssh_client(srv_name)
        ssh_client.exec_cmd(cmd=cmd)
        cmd = 'grep \'name="logging.level"\' %s' % log4j_path
        self.logger.info('log level after update is:')
        ssh_client.exec_cmd(cmd=cmd)

    def get_db_version(self):
        cursor = self.conn_tcs.cursor()
        if self.dbms.lower() == 'oracle':
            cursor.execute('select * from v$version')
            print('oracle version:' + str(cursor.fetchone()))
        if self.dbms.lower() == 'mysql' or self.dbms.lower() == 'mariadb':
            self.conn_tcs.ping(reconnect=True)
            cursor.execute('select version()')
            print('mysql version:' + str(cursor.fetchone()))
        cursor.close()

    def __get_ssh_client(self, srv_name):
        srv_dict = self.sections_map[srv_name]
        ssh_client = SSHClient(srv_dict['host'], srv_dict['user'], srv_dict['password'], srv_dict['ssh_port'])
        return ssh_client
