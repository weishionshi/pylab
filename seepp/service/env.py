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
        db_section = self.sections_map.get('seepp').get('db')
        self.__init_db_conn(db_section)

        # init redis connections
        rds_section = self.sections_map.get('seepp').get('redis')
        self.__init_redis_conn(rds_section)

    def __init_db_conn(self, section):
        # init db connection
        dbms = self.sections_map.get(section)['dbms']
        db_host = self.sections_map.get(section)['host']
        db_port = self.sections_map.get(section)['db_port']
        db_pwd = self.sections_map.get(section)['db_password']
        tcs_db_name = self.sections_map.get(section)['tcs_db_name']
        lcs_db_name = self.sections_map.get(section)['lcs_db_name']
        if dbms.lower() == 'mysql' or dbms.lower() == 'mariadb':
            db_user = self.sections_map.get(section)['db_user']
            self.conn_tcs = PyMysqlFactory(db_host, int(db_port), db_user, db_pwd, tcs_db_name).get_connection()
            self.conn_lcs = PyMysqlFactory(db_host, int(db_port), db_user, db_pwd, lcs_db_name).get_connection()
        if dbms.lower() == 'oracle':
            sid = self.sections_map.get(section)['sid']
            self.conn_tcs = cx_Oracle.connect(tcs_db_name,db_pwd,db_host+':'+db_port+'/' + sid)
            self.conn_lcs = cx_Oracle.connect(lcs_db_name,db_pwd,db_host+':'+db_port+'/' + sid)

    def __init_redis_conn(self, section):
        pool = redis.ConnectionPool(host=self.sections_map.get(section)['host'],
                                    port=self.sections_map.get(section)['rds_port'],
                                    password=self.sections_map.get(section)['rds_password'], decode_responses=True)
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
        config_path = self.sections_map.get(srv_name)['deploy_path'] + '/' + file_name
        self.logger.debug('config path is ' + config_path)
        cmd = 'echo -e \'%s\' >> %s' % (string, config_path)

        ssh_client = self.__get_ssh_client(srv_name)
        ssh_client.exec_cmd(cmd=cmd)

    def get_db_version(self):
        cursor = self.conn_tcs.cursor()
        cursor.execute('select * from v$version')
        print('oracle version:' + cursor.fetchone())

    def __get_ssh_client(self, srv_name):
        srv_dict = self.sections_map[srv_name]
        ssh_client = SSHClient(srv_dict['host'], srv_dict['user'], srv_dict['password'], srv_dict['ssh_port'])
        return ssh_client
