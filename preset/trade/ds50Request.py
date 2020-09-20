#!/usr/bin/env python
# coding: utf-8

"""
@File     : ds50Request.py
@copyright: HS
@Author   : huyb20630
@Date     : 2020/7/9 下午2:15
@Desc     :
"""
import os
import traceback
from configparser import ConfigParser

import datetime

# 读取配置
import cx_Oracle
from multidict import CIMultiDict

os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'

conf = ConfigParser()
conf.read("conf.ini")


# 数据库连接
class DbConn:
    def __init__(self, username, password, dsn, charset="utf8"):
        self.conn = cx_Oracle.connect("{0}/{1}@{2}".format(username, password, dsn))
        self.cursor = self.conn.cursor()

    def execute(self, sql, params):
        try:
            self.cursor.executemany(sql, params)
        except BaseException:
            traceback.print_exc()

    def close(self):
        if self.cursor:
            self.cursor.close()

        if self.conn:
            self.conn.close()


conn_info = {"username": "ds50acco", "password": "Caifu123", "dsn": "192.168.76.152:1521/ora11g"}
conn = DbConn(**conn_info)

curr_date = datetime.datetime.now().strftime("%Y%m%d")

# 读取参数
params_dict = CIMultiDict()
for param in conf["params"]:
    params_dict[param] = conf["params"][param]

# 读取sql配置
sqls_dcit = {}
for section in conf.sections():
    if section.startswith("sql_"):
        sqls_dcit.setdefault(section, {})

        for option in conf[section]:
            sqls_dcit[section][option] = conf[section][option]
        # 临时数据存放
        sqls_dcit[section].setdefault("data", [])

data_nums = 1000
for index in range(1, data_nums+1):
    # print(index)

    # 生成参数
    params = CIMultiDict()
    for param in params_dict:
        params[param] = eval(params_dict[param])

    for section in sqls_dcit:
        data = [params[item.strip()] for item in sqls_dcit[section]["params"].split(",")]
        sqls_dcit[section]["data"].append(tuple(data))

        if index % 1000 == 0 or index == data_nums:
            sql = sqls_dcit[section]["template"]
            conn.execute(sql, sqls_dcit[section]["data"])
            conn.conn.commit()
            sqls_dcit[section]["data"] = []

conn.close()

