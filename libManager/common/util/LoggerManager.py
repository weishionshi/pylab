# -*- coding: utf-8 -*-

import logging,logging.handlers
import os
import sys
from django.conf import settings

'''
Python使用logging模块记录日志涉及四个主要类，使用官方文档中的概括最为合适：
    1>.logger提供了应用程序可以直接使用的接口；
    2>.handler将(logger创建的)日志记录发送到合适的目的输出；
    3>.filter提供了细度设备来决定输出哪条日志记录；
    4>.formatter决定日志记录的最终输出格式。
'''


def get_logger():
    logger_obj = logging.getLogger(__name__)  # 创建一个logger对象，它提供了应用程序可以直接使用的接口，其类型为“<class 'logging.RootLogger'>”；

    path = settings.BASE_DIR + "/logs/PyLab.error.log"
    fh = logging.handlers.TimedRotatingFileHandler(path, 'midnight', 1)  # 创建一个文件输出流；
    fh.suffix = "%Y-%m-%d.log"
    fh.setLevel(logging.ERROR)  # 定义文件输出流的告警级别；

    ch = logging.StreamHandler(sys.stdout)  # 创建一个屏幕输出流；
    ch.setLevel(logging.DEBUG)  # 定义屏幕输出流的告警级别；

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')  # 自定义日志的输出格式，这个格式可以被文件输出流和屏幕输出流调用；
    fh.setFormatter(formatter)  # 添加格式花输出，即调用我们上面所定义的格式，换句话说就是给这个handler选择一个格式；
    ch.setFormatter(formatter)

    logger_obj.addHandler(fh)  # logger对象可以创建多个文件输出流（fh）和屏幕输出流（ch）
    logger_obj.addHandler(ch)

    return logger_obj
