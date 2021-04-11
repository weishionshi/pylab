#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author  : shiwx
# @time    : 4/10/21 10:44
# @file    : env.py
import redis

from util.db.conn_builder import PyMysqlFactory
from util.file import file_util
from util.logging.logger_manager import LoggerFactory
from util.ssh.ssh_client import SSHClient


class EnvBase(object):
    # init logger
    __logger = LoggerFactory(__name__).get_logger()

    # __sections_map=None

    def __init__(self, config_path):
        self.config_path = config_path

        # read config
        self.__sections_map = file_util.LoadConfig.get_config_parser(config_path, encoding='utf-8')

        # init db connections
        db_section = self.__sections_map.get('seepp').get('db')
        self.__init_db_conn(db_section)

        # init redis connections
        rds_section = self.__sections_map.get('seepp').get('redis')
        self.__init_redis_conn(rds_section)

    def __init_db_conn(self, section):
        # init mysql connection
        dbms = self.__sections_map.get(section)['dbms']
        db_host = self.__sections_map.get(section)['host']
        db_port = self.__sections_map.get(section)['db_port']
        db_user = self.__sections_map.get(section)['db_user']
        db_pwd = self.__sections_map.get(section)['db_password']
        tcs_db_name = self.__sections_map.get(section)['tcs_db_name']
        lcs_db_name = self.__sections_map.get(section)['lcs_db_name']
        if dbms.lower() == 'mysql' or dbms.lower() == 'mariadb':
            self.conn_tcs = PyMysqlFactory(db_host, int(db_port), db_user, db_pwd, tcs_db_name).get_connection()
            self.conn_lcs = PyMysqlFactory(db_host, int(db_port), db_user, db_pwd, lcs_db_name).get_connection()
        if dbms.lower() == 'oracle':
            pass
            # TODO:init oracle connection

    def __init_redis_conn(self, section):
        pool = redis.ConnectionPool(host=self.__sections_map.get(section)['host'],
                                    port=self.__sections_map.get(section)['rds_port'],
                                    password=self.__sections_map.get(section)['rds_password'], decode_responses=True)
        self.rds = redis.Redis(connection_pool=pool, charset='UTF-8', encoding='UTF-8')


class DeployEnv(EnvBase):
    def __init__(self, config_path):
        EnvBase.__init__(self, config_path)

    def update_jdbc(self, srv_name, new_jdbc_dict):
        # init ssh client
        srv_dict = self.__sections_map[srv_name]
        ssh_client = SSHClient(srv_dict['host'], srv_dict['user'], srv_dict['password'], srv_dict['ssh_port'])

        # update jdbc string by sed command
        cmd = 'sed -i '
        ssh_client.exec_cmd(cmd=cmd)
        pass
