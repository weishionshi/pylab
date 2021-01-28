#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author  : shiwx27477
# @time    : 2020/10/21 11:48
# @file    : puyi-lcs.py
from util.file import file_util
from util.db.conn_builder import PyMysqlFactory, PyOracleFactory


class LcsProcess:
    def __init__(self, cfg_file):
        # get config map from cfg file
        self.cfg_map = file_util.LoadConfig.get_config_parser(cfg_file)
        # create db connection for lcs,tcs
        self.lcs_conn = self.__get_db_conn(self.cfg_map['db-lcs'])
        self.tcs_conn = self.__get_db_conn(self.cfg_map['db-tcs'])

    def pre_check(self):
        pass

    def get_lcs_sysdate(self):
        pass

    def get_tcs_sysdate(self):
        pass


    @staticmethod
    def __get_db_conn(self, map1):
        if map1.get('dbms') == 'oracle':
            return PyOracleFactory(map1.get('host'), map1.get('port'), map1.get('user'), map1.get('password'),
                                   map1.get('srv_name')).get_connection()
        if map1.get('dbms') == 'mysql':
            return PyMysqlFactory(map1.get('host'), map1.get('port'), map1.get('user'), map1.get('password'),
                                  map1.get('db_name')).get_connection()
