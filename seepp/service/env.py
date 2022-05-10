#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author  : shiwx
# @time    : 4/10/21 10:44
# @file    : env.py

import json
import urllib
from urllib import request
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
        db_sec_qs = self.sections_map.get('seepp').get('db_qs')
        self.db_section = self.sections_map.get(db_sec)
        self.db_section_qs = self.sections_map.get(db_sec_qs)
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
        # init db connection for trade env
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

        # init db connection for liq env
        self.dbms_qs = self.db_section_qs['dbms']
        db_host = self.db_section_qs['host']
        db_port = self.db_section_qs['db_port']
        db_pwd = self.db_section_qs['db_password']
        tcs_db_name = self.db_section_qs['tcs_db_name']
        lcs_db_name = self.db_section_qs['lcs_db_name']
        if self.dbms_qs.lower() == 'mysql' or self.dbms_qs.lower() == 'mariadb':
            db_user = self.db_section_qs['db_user']
            self.conn_tcs_qs = PyMysqlFactory(db_host, int(db_port), db_user, db_pwd, tcs_db_name).get_connection()
            self.conn_lcs_qs = PyMysqlFactory(db_host, int(db_port), db_user, db_pwd, lcs_db_name).get_connection()
        if self.dbms_qs.lower() == 'oracle':
            sid = self.db_section_qs['sid']
            self.conn_tcs_qs = cx_Oracle.connect(tcs_db_name, db_pwd, db_host + ':' + db_port + '/' + sid)
            self.conn_lcs_qs = cx_Oracle.connect(lcs_db_name, db_pwd, db_host + ':' + db_port + '/' + sid)


    def __init_redis_conn(self):
        pool = redis.ConnectionPool(host=self.rds_section['host'],
                                    port=self.rds_section['rds_port'],
                                    password=self.rds_section['rds_password'],
                                    db=0,
                                    decode_responses=True)
        self.rds = redis.Redis(connection_pool=pool, charset='UTF-8', encoding='UTF-8')


class DeployEnv(EnvBase):
    def __init__(self, config_path):
        EnvBase.__init__(self, config_path)

    def check_services_health(self):
        """
        后台应用健康检查
        """
        srv_list = self.sections_map.get('seepp').get('services').split('|')
        for service in srv_list:
            items = self.sections_map[service]
            url = 'http://' + items.get("host") + ':' + items.get("port") + '/health'
            self.logger.debug('url:' + url)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1'}
            # 重构useragent
            req = urllib.request.Request(url=url, headers=headers)
            # 发送请求获取响应对象(urlopen)
            res = urllib.request.urlopen(req)
            # 获取响应内容,并转换成python dict
            response = json.loads(res.read().decode())
            self.logger.debug(response)
            self.logger.info('[%s] is [%s]' % (url, response['status']))
            assert response['status'] == 'UP'

    def check_db_ping(self):
        """
        数据库健康检查
        """
        pass

    def check_hardware_health(self):
        """
        硬件资源健康检查
        """
        pass

    def refresh_services(self):
        """
        刷新缓存
        """
        srv_list = self.sections_map.get('seepp').get('services').split('|')
        for srv in srv_list:
            self.refresh_service(srv)

    def refresh_services_lcs(self):
        """
        刷新清算服务缓存
        """
        srv_list = self.sections_map.get('seepp').get('qs_services').split('|')
        for srv in srv_list:
            self.refresh_service(srv)

    def restore_db_tcs(self, args):
        """
        开始测试销售系统前,先恢复基础存量数据,即把接口新跑出来的数据先删除
        :return:
        """
        #删除开户数据
        self.call_procedure('tcs','TCS_DELETE_OPEN_ACCO', args)

        #删除增开交易账户数据
        self.call_procedure('tcs','TCS_DELETE_ADD_TRADE_ACCO', args)
        #删除交易申请

        #删除账户申请

        #删除资金流水

    def preset_tcs_db(self):
        """
        开始测试销售系统前,先预置基础数据,比如打开本地缓存开关,更新所有用户密码,等等
        :return:
        """
        sql_list = []
        if self.dbms.lower() == 'oracle':
            sql_list = []
        if self.dbms.lower() == 'mysql' or self.dbms.lower() == 'mariadb':
            sql_list = [
                '''update TC_TSYSPARAMETER t set t.VC_VALUE = '1' 
                where t.vc_tenant_id ='10000' 
                and t.VC_ITEM = 'STATIC_DATA_CACHE_TYPE' ''',
                "update tc_tsysparameter t  set t.VC_VALUE =(select replace(group_concat(distinct t1.C_CAPITAL_MODE),',','|') from tc_tcapitalacco t1)  where t.vc_tenant_id ='10000' and t.VC_ITEM = 'FTSUPPORTCAP' ",
                "update tc_tcustinfodetail t set t.VC_DEAL_PWD = '123456' where t.VC_DEAL_PWD <>'123456'",
                "update tc_taccoinfo t set t.VC_ALLOW_TRUST = '0|1|2|3|4' where 1=1",
                "update tc_tfundacco t set t.C_FUND_ACCO_STATE = '0' where t.C_FUND_ACCO_STATE<>'0';"

            ]

            self.conn_tcs.ping(reconnect=True)

        cursor = self.conn_tcs.cursor()
        try:
            for sql in sql_list:
                rows = cursor.execute(sql)
                self.logger.info("[%d] rows affected by sql: [%s]" % (rows, sql))
            self.conn_tcs.commit()

        except Exception as e:
            self.conn_tcs.rollback()
            self.logger.error(e, exec_info=True)
        finally:
            cursor.close()

    def update_jdbc(self, srv_name, new_jdbc_dict):
        # init ssh client
        ssh_client = self.__get_ssh_client(srv_name)
        # update jdbc string by sed command
        cmd = 'sed -i '
        ssh_client.exec_cmd(cmd=cmd)
        pass

    def append_config(self, srv_name, file_name, string):
        """
        往指定配置文件末尾追加配置
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
        cmd = 'sed -i \'s/<Property name="logging.level">.*$/<Property name="logging.level">%s<\\/Property>/g\' %s' % (
        log_level, log4j_path)
        ssh_client = self.__get_ssh_client(srv_name)
        ssh_client.exec_cmd(cmd=cmd)
        cmd = 'grep \'name="logging.level"\' %s' % log4j_path
        self.logger.info('log level after update is:')
        ssh_client.exec_cmd(cmd=cmd)

    def update_log_2kafka(self, srv_name, flag, file_name='springboot/config/application.properties'):
        """
        是否把日志发送到日志中心的kafka
        @param srv_name:
        @param flag: true,or false
        @return:
        """
        app_path = self.sections_map.get(srv_name)['deploy_path'] + '/' + file_name
        cmd1 = 'sed -i \'s/kafka.support=.*$/kafka.support=%s/g\' %s' % (flag, app_path)
        cmd2 = 'sed -i \'s/rpc.trace.log=.*$/rpc.trace.log=%s/g\' %s' % (flag, app_path)
        ssh_client = self.__get_ssh_client(srv_name)
        ssh_client.exec_cmd(cmd=cmd1)
        ssh_client.exec_cmd(cmd=cmd2)

        cmd = 'grep \'rpc.trace.log\' %s' % app_path
        self.logger.info('[rpc.trace.log] after update is:')
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

    def refresh_service(self, srv_name):
        items = self.sections_map[srv_name]
        url = 'http://' + items.get("host") + ':' + items.get("port") + '/refresh'
        self.logger.debug('url:' + url)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1'}
        # 重构useragent
        req = urllib.request.Request(url=url, headers=headers)
        # 发送请求获取响应对象(urlopen)
        res = urllib.request.urlopen(req)
        # 获取响应内容,并转换成python dict
        response = res.read().decode()
        self.logger.debug(response)
        self.logger.info('refresh response of [%s] is [%s]' % (url, response))
        assert 'success' in response or 'ok' in response

    def call_procedure(self, db_kind, procedure_name, args):
        if db_kind == 'tcs':
            cursor = self.conn_tcs.cursor()
            try:
                cursor.callproc(procedure_name, args)
            except Exception as e:
                self.logger.error(e.__str__())
            cursor.close()
            self.conn_tcs.commit()

        if db_kind == 'lcs':
            cursor = self.conn_lcs.cursor()
            try:
                result = cursor.callproc(procedure_name, args)
                self.logger.info(procedure_name + ' procedure result:' + str(result))
            except Exception as e:
                self.logger.error(e.__str__())
            cursor.close()
            self.conn_lcs.commit()

    def __get_ssh_client(self, srv_name):
        srv_dict = self.sections_map[srv_name]
        ssh_client = SSHClient(srv_dict['host'], srv_dict['user'], srv_dict['password'], srv_dict['ssh_port'])
        return ssh_client
