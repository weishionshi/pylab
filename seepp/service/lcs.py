#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author  : shiwx
# @time    : 2021/1/28 19:21
# @file    : lcs.py
import datetime
import json
import urllib
from urllib import request
from util.logging.logger_manager import LoggerFactory
from util.file import file_util
from util.db.conn_builder import PyMysqlFactory
from util.ssh.ssh_client import ParamikoThreading
import time
import redis


class Liquidate:
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

    def get_tcs_sysdate(self):
        sql = "select VC_ITEM,VC_VALUE from TC_TSYSPARAMETER where vc_item in (%s) and vc_tenant_id='10000'"
        cursor = self.conn_tcs.cursor()
        self.conn_tcs.ping(reconnect=True)
        try:
            # TODO:这么写报错,cursor.execute(SYS_PARAMATER_SQL, [pymysql.escape_string('TC_TSYSPARAMETER'), 'SYSDATE'])
            cursor.execute(sql, ['SYSDATE'])
            self.__logger.debug("sql:" + sql)
            result = cursor.fetchall()
        except Exception as e:
            self.__logger.error(e, exc_info=True)
        finally:
            cursor.close()
        # self.__logger.debug(type(result))
        self.__logger.debug(result)
        # self.__logger.debug(result[0][0])

        return result

    def get_lcs_sysdate(self):
        sql = "select VC_ITEM,VC_VALUE from LC_TSYSPARAMETER where vc_item in (%s) and vc_tenant_id='10000'"
        cursor = self.conn_lcs.cursor()
        self.conn_lcs.ping(reconnect=True)
        try:
            cursor.execute(sql, ['SYSDATE'])
            self.__logger.debug("sql:" + sql)
            result = cursor.fetchall()
            self.__logger.debug(result)
        except Exception as e:
            self.__logger.error(e, exc_info=True)
        finally:
            cursor.close()
        return result

    def get_version(self):
        # 使用 cursor() 方法创建一个游标对象 cursor
        cursor = self.conn_tcs.cursor()
        self.conn_tcs.ping(reconnect=True)

        # 使用 execute()  方法执行 SQL 查询
        cursor.execute("SELECT VERSION()")

        # 使用 fetchone() 方法获取单条数据.
        data = cursor.fetchone()

        self.__logger("Database version : %s " % data)

    """
    set SYSDATE in DB and refresh redis
    """

    def set_lcs_sysdate(self, sys_date):
        self.__logger.info('original SYSDATE in db is [%s]' % self.get_tcs_sysdate())
        sql = "update LC_TSYSPARAMETER set vc_value= %s where vc_item = %s and vc_tenant_id='10000'"
        delta = datetime.timedelta(days=-1)
        last_sys_date = datetime.datetime.strftime(datetime.datetime.strptime(sys_date, "%Y%m%d") + delta,'%Y%m%d')
        cursor = self.conn_lcs.cursor()
        self.conn_lcs.ping(reconnect=True)
        try:
            cursor.execute(sql, [sys_date, 'SYSDATE'])
            cursor.execute(sql, [last_sys_date, 'LASTSYSDATE'])
            self.__logger.debug("sql:" + sql)
            self.conn_lcs.commit()
        except Exception as e:
            self.conn_lcs.rollback()
            self.__logger.error(e, exec_info=True)
        finally:
            cursor.close()

        self.__logger.info('SYSDATE in db [after update] is [%s]' % self.get_lcs_sysdate())

        if self.rds.get('{"item":"SYSDATE","tenantId":"10000"}') is None:
            self.__logger.info('[original ]SYSDATE in redis is [NULL]')
        else:
            self.__logger.info(
                '[original] SYSDATE in redis is [%s]' % self.rds.get('{"item":"SYSDATE","tenantId":"10000"}'))

        # hdel sysdate
        self.rds.delete('{"item":"SYSDATE","tenantId":"10000"}')
        time.sleep(6)
        if self.rds.get('{"item":"SYSDATE","tenantId":"10000"}') is None:
            self.__logger.info('SYSDATE in redis [after DEL] is NULL')
        else:
            self.__logger.info(
                'SYSDATE in redis [after DEL] is [%s]' % self.rds.get('{"item":"SYSDATE","tenantId":"10000"}'))

    def set_tcs_sysdate(self, sys_date):
        self.__logger.info('[original] SYSDATE in db is [%s]' % self.get_tcs_sysdate())
        sql = "update TC_TSYSPARAMETER set vc_value= %s where vc_item = %s and vc_tenant_id='10000'"
        delta = datetime.timedelta(days=-1)
        last_sys_date = datetime.datetime.strftime(datetime.datetime.strptime(sys_date, "%Y%m%d") + delta,'%Y%m%d')
        cursor = self.conn_tcs.cursor()
        self.conn_tcs.ping(reconnect=True)
        try:
            cursor.execute(sql, [sys_date, 'SYSDATE'])
            cursor.execute(sql, [last_sys_date, 'LASTSYSDATE'])
            self.__logger.debug("sql:" + sql)
            self.conn_tcs.commit()
        except Exception as e:
            self.conn_tcs.rollback()
            self.__logger.error(e)
        finally:
            cursor.close()

        self.__logger.info('SYSDATE in db [after] update is [%s]' % self.get_tcs_sysdate())

        # update redis
        if self.rds.hget('sys_param_10000', 'SYSDATE') is None:
            self.__logger.info('[original] SYSDATE in redis is [NULL]')
        else:
            self.__logger.info('[original] SYSDATE in redis is [%s]' % self.rds.hget('sys_param_10000', 'SYSDATE'))
        # hdel sysdate
        self.rds.hdel('sys_param_10000', 'SYSDATE')
        time.sleep(6)
        if self.rds.hget('sys_param_10000', 'SYSDATE') is None:
            self.__logger.info('SYSDATE in redis [after HDEL] is NULL')
        else:
            self.__logger.info('SYSDATE in redis [after HDEL] is [%s]' % self.rds.hget('sys_param_10000', 'SYSDATE'))

    def set_tcs_sale_code(self,sale_code):
        sql = "update TC_TSYSPARAMETER set vc_value= %s where vc_item = %s and vc_tenant_id='10000'"
        cursor = self.conn_tcs.cursor()
        self.conn_tcs.ping(reconnect=True)
        try:
            cursor.execute(sql, [sale_code, 'SALECODE'])
            self.conn_tcs.commit()
        except Exception as e:
            self.conn_tcs.rollback()
            self.__logger.error(e)
        finally:
            cursor.close()

    def set_lcs_sale_code(self, sale_code):
        sql = "update LC_TSYSPARAMETER set vc_value= %s where vc_item = %s and vc_tenant_id='10000'"
        cursor = self.conn_lcs.cursor()
        self.conn_lcs.ping(reconnect=True)
        try:
            cursor.execute(sql, [sale_code, 'SALECODE'])
            self.conn_lcs.commit()
        except Exception as e:
            self.conn_lcs.rollback()
            self.__logger.error(e, exec_info=True)
        finally:
            cursor.close()

    def sync_machine_time(self):
        pass

    def get_all_machines_datetime(self):
        command = 'date +"%Y-%m-%d %H:%M:%S" '
        all_list = self.__sections_map.get('seepp').get('services').split('|')
        all_list.append(self.__sections_map.get('seepp').get('db'))
        self.__logger.debug('all machines:' + str(all_list))

        t_pool = []
        for service in all_list:
            items = self.__sections_map[service]
            t = ParamikoThreading(
                host=items.get("host", "localhost"),
                username=items.get("user", "root"),
                password=items.get("password", "123456"),
                command=command
            )
            t_pool.append(t)
        for t in t_pool:
            t.start()
        for t in t_pool:
            t.join()

    def pre_check(self, sysdate):
        tcs_tuple = self.get_tcs_sysdate()
        lcs_tuple = self.get_lcs_sysdate()
        tcs_dict = {tcs_tuple[0][0]: tcs_tuple[0][1]}
        lcs_dict = {lcs_tuple[0][0]: lcs_tuple[0][1]}
        assert tcs_dict['SYSDATE'] == sysdate
        assert lcs_dict['SYSDATE'] == sysdate


        self.get_all_machines_datetime()
        # check app health
        self.check_service_health()

        # TODO:硬件健康检查(磁盘)

    def check_service_health(self):
        """
        后台应用健康检查
        """
        srv_list = self.__sections_map.get('seepp').get('services').split('|')
        for service in srv_list:
            items = self.__sections_map[service]
            url = 'http://' + items.get("host") + ':' + items.get("port") + '/health'
            self.__logger.debug('url:' + url)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1'}
            # 重构useragent
            req = urllib.request.Request(url=url, headers=headers)
            # 发送请求获取响应对象(urlopen)
            res = urllib.request.urlopen(req)
            # 获取响应内容,并转换成python dict
            response = json.loads(res.read().decode())
            self.__logger.debug(response)
            self.__logger.info('[%s] is [%s]' % (url, response['status']))
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

    def refresh_service(self):
        """
        后台应用健康检查
        """
        srv_list = self.__sections_map.get('seepp').get('services').split('|')
        for service in srv_list:
            items = self.__sections_map[service]
            url = 'http://' + items.get("host") + ':' + items.get("port") + '/refresh'
            self.__logger.debug('url:' + url)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1'}
            # 重构useragent
            req = urllib.request.Request(url=url, headers=headers)
            # 发送请求获取响应对象(urlopen)
            res = urllib.request.urlopen(req)
            # 获取响应内容,并转换成python dict
            response = res.read().decode()
            self.__logger.debug(response)
            self.__logger.info('refresh response of [%s] is [%s]' % (url, response))
            assert 'success' in response or 'ok' in response

    def update_qrtz_triggers(self, datetime):
        """
        update qrtz_triggers.next_fire_time
        """
        # exec update sql  date_add(now(),interval 5 second )
        sql = """update qrtz_triggers t
        set t.NEXT_FIRE_TIME=timestampdiff(second ,'1970-01-01 08:00:00',%s)*1000 
        where 1=1  and t.SCHED_NAME='liq';
        """
        cursor = self.conn_tcs.cursor()
        self.conn_tcs.ping(reconnect=True)
        try:
            rows = cursor.execute(sql, [datetime])
            self.conn_tcs.commit()
            self.__logger.info("[%d] rows affected by sql: [%s]" % (rows, sql))
        except Exception as e:
            self.conn_tcs.rollback()
            self.__logger.error(e, exec_info=True)
        finally:
            cursor.close()

        cursor = self.conn_lcs.cursor()
        self.conn_lcs.ping(reconnect=True)
        try:
            rows = cursor.execute(sql, [datetime])
            self.conn_lcs.commit()
            self.__logger.info("[%d] rows affected by sql: [%s]" % (rows, sql))
        except Exception as e:
            self.conn_lcs.rollback()
            self.__logger.error(e, exec_info=True)
        finally:
            cursor.close()

    """
    backup database
    """

    def backup_db(self):
        pass

    def start_db(self):  # TODO
        pass

    def shutdown_db(self):  # TODO
        pass

    def trigger_auto_task(self, task_name):
        sql = "update LC_TAUTOTASKCFG t set t.VC_LAST_DATE_TIME='',t.C_TASK_STATE='0' ,t.VC_BEGIN_TIME='000000' where t.VC_TASK_NAME = %s;"
        cursor = self.conn_lcs.cursor()
        self.conn_lcs.ping(reconnect=True)
        try:
            rows = cursor.execute(sql, [task_name])
            self.conn_lcs.commit()
            self.__logger.info("[%d] rows affected by sql: [%s]" % (rows, sql))
        except Exception as e:
            self.conn_lcs.rollback()
            self.__logger.error(e, exec_info=True)
        finally:
            cursor.close()

    def correct_task_excetpion(self):
        sql1 = "update LC_TAUTOTASKRESULT t set t.C_RESULT_STATE='1' where t.C_RESULT_STATE='0';"
        cursor = self.conn_lcs.cursor()
        self.conn_lcs.ping(reconnect=True)
        try:
            rows = cursor.execute(sql1)
            self.__logger.info("[%d] rows affected by sql: [%s]" % (rows, sql1))
            self.conn_lcs.commit()
        except Exception as e:
            self.conn_lcs.rollback()
            self.__logger.error(e, exec_info=True)
        finally:
            cursor.close()

    def correct_msg_excetpion_but(self, msg_id=''):
        sql1 = "update LC_TMESSAGEDEAL t set t.C_MESSAGE_STATE = '2' where t.C_MESSAGE_STATE<>'2' "
        sql2 = "update LC_TMESSAGEDEAL t set t.C_MESSAGE_STATE = '2' where t.C_MESSAGE_STATE<>'2' and  VC_MESSAGE_ID<>%s "
        cursor = self.conn_lcs.cursor()
        self.conn_lcs.ping(reconnect=True)

        try:
            if msg_id == '':
                rows = cursor.execute(sql1)
                self.__logger.info("[%d] rows affected by sql1: [%s]" % (rows, sql1))
            else:
                rows = cursor.execute(sql2, [msg_id])
                self.__logger.info("[%d] rows affected by sql2: [%s]" % (rows, sql2))
            self.conn_lcs.commit()
        except Exception as e:
            self.conn_lcs.rollback()
            self.__logger.error(e, exec_info=True)
        finally:
            cursor.close()

    """
    skip process manually
    """

    def skip_process(self, prc_name):
        pass

