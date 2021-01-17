#!/usr/bin/env python
# -*- coding(): utf-8 -*-
# @author  (): shiwx27477
# @time    (): 2020/10/16 10():40
# @file    (): pu1.py
import logging

import pymysql

from util.db.conn_builder import PyMysqlFactory
from util.file import file_util

SYS_PARAMATER_SQL = "select VC_VALUE from %s where vc_item = %s and vc_tenant_id='10000';"
SYS_PARAMATER_SQL1 = "select VC_VALUE from TC_TSYSPARAMETER where vc_item = %s and vc_tenant_id='10000';"
SYS_PARAMATER_SQL2 = "select VC_VALUE from LC_TSYSPARAMETER where vc_item = %s and vc_tenant_id='10000';"
# pymysql.escape_string(res)

# init logger
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# read config
sections_map = file_util.LoadConfig.get_config_parser("local_config_sf.ini")
service_list = sections_map['seepp']['services'].split('|')

# init mysql connection
db_host = sections_map['mariadb-172']['host']
db_port = sections_map['mariadb-172']['port']
db_user = sections_map['mariadb-172']['user']
db_pwd = sections_map['mariadb-172']['password']
db_name = sections_map['mariadb-172']['tcs_db_name']
builder1 = PyMysqlFactory(db_host, int(db_port), db_user, db_pwd, db_name)
conn_tcs = builder1.get_connection()

db_host = sections_map['mariadb-235']['host']
db_port = sections_map['mariadb-172']['port']
db_user = sections_map['mariadb-235']['user']
db_pwd = sections_map['mariadb-235']['password']
db_name = sections_map['mariadb-235']['lcs_db_name']
builder2 = PyMysqlFactory(db_host, int(db_port), db_user, db_pwd, db_name)
conn_lcs = builder2.get_connection()

"""
scan pre conditions():
    - sysdate
    - next_fire_time
"""


def pre_check():
    print('tcs SYSDATE:%s' % get_tcs_sysdate())
    print('lcs SYSDATE:%s' % get_lcs_sysdate())
    print(get_all_machines_datetime())


"""
sync servers' datetime
"""


def sync_machine_time():
    pass


def get_all_machines_datetime():
    pass


"""
update qrtz_triggers.next_fire_time
"""


def update_qrtz_triggers(datetime):
    # exec update sql  date_add(now(),interval 5 second )
    sql = """update qrtz_triggers t
    set t.NEXT_FIRE_TIME=timestampdiff(second ,'1970-01-01 08:00:00',%s)*1000 
    where 1=1  and t.SCHED_NAME='liq';
    """
    cursor = conn_tcs.cursor()
    try:
        rows = cursor.execute(sql, [datetime])
        conn_tcs.commit()
        logger.info("[%d] rows affected by sql: [%s]" % (rows, sql))
    except Exception as e:
        conn_tcs.rollback()
        logger.error(e)
    finally:
        cursor.close()

    cursor = conn_lcs.cursor()
    try:
        rows = cursor.execute(sql, [datetime])
        conn_lcs.commit()
        logger.info("[%d] rows affected by sql: [%s]" % (rows, sql))
    except Exception as e:
        conn_lcs.rollback()
        logger.error(e)
    finally:
        cursor.close()


"""
backup database
"""


def backup_db():
    pass


def get_tcs_sysdate():
    sql = "select VC_VALUE from TC_TSYSPARAMETER where vc_item = '%s' and vc_tenant_id='10000'" % ('SYSDATE')
    cursor = conn_tcs.cursor()
    try:
        # TODO:这么写报错,cursor.execute(SYS_PARAMATER_SQL, [pymysql.escape_string('TC_TSYSPARAMETER'), 'SYSDATE'])
        cursor.execute(sql)
        logger.debug("sql:" + sql)
    except Exception as e:
        logger.error(e)
    finally:
        cursor.close()
    return cursor.fetchone()[0]


def get_lcs_sysdate():
    sql = "select VC_VALUE from LC_TSYSPARAMETER where vc_item = '%s' and vc_tenant_id='10000'" % ('SYSDATE')
    cursor = conn_lcs.cursor()
    try:
        # TODO:这么写报错,cursor.execute(SYS_PARAMATER_SQL, [pymysql.escape_string('LC_TSYSPARAMETER'), 'SYSDATE'])
        cursor.execute(sql)
        logger.debug("sql:" + sql)
    except Exception as e:
        logger.error(e)
    finally:
        cursor.close()
    return cursor.fetchone()[0]


def trigger_auto_task(task_name):
    sql = "update LC_TAUTOTASKCFG t set t.VC_LAST_DATE_TIME='',t.C_TASK_STATE='0' ,t.VC_BEGIN_TIME='000000' where t.VC_TASK_NAME = %s;"
    cursor = conn_lcs.cursor()
    try:
        rows = cursor.execute(sql, [task_name])
        conn_lcs.commit()
        logger.info("[%d] rows affected by sql: [%s]" % (rows, sql))
    except Exception as e:
        conn_lcs.rollback()
        logger.error(e)
    finally:
        cursor.close()


"""
skip process manually
"""


def skip_process(prc_name):
    pass


if __name__ == '__main__':
    pre_check()
    # trigger_auto_task('CHECKDATA')
    # trigger_auto_task('EXPORTREQUESTFILE')
    trigger_auto_task('TRADEDAYINIT')
    update_qrtz_triggers('2020-10-10 00:00:00')
