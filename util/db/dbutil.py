#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author  : shiwx27477
# @time    : 2021/6/2 14:56
# @file    : dbutil.py

def convert_mysql_2_oracle(mysql):
    index = 1
    while '%s' in mysql:
        mysql = mysql.replace('%s', ':%s' % index, 1)
        index += 1
    return mysql.replace('\n','').replace('`','')