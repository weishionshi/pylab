#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author  : shiwx27477
# @time    : 2021/3/21 17:47
# @file    : master_v202102.py
from unittest import TestCase

from seepp.service.lcs import Liquidate
from util.logging.logger_manager import LoggerFactory


class TestLiquidate(TestCase):
    # init logger
    logger = LoggerFactory(__name__).get_logger()
    liq = Liquidate('local_config_master.ini')
    SYSDATE = '20210318'

    @classmethod
    def setUpClass(cls):
        """
        load config and init liq,run only once
        @return:
        @rtype:
        """
        # cls.liq = Liquidate('local_config_pu1.ini') TODO:这样写不对,下面的用例无法引用到liq
        print('setUpClass')

    @classmethod
    def tearDownClass(cls):
        """
        tear down after all testcases finished,run only once
        @return:
        @rtype:
        """
        print('tearDownClass')

    def test_pre_check(self):
        self.liq.pre_check(sysdate=self.SYSDATE)

    def test_refresh_service(self):
        self.liq.refresh_service()

    def test_set_sysdate(self):
        self.liq.set_lcs_sysdate(self.SYSDATE)
        self.liq.set_tcs_sysdate(self.SYSDATE)

    def test_trigger_auto_task(self):
        # 清除异常任务
        self.liq.correct_task_excetpion()

        # 清除异常消息,除了本次的message_id
        self.liq.correct_msg_excetpion_but()

        # 交易导出申请
        self.liq.trigger_auto_task('EXPORTREQUESTFILE')

    def test_trigger_message_task(self):
        # 清除异常任务
        self.liq.correct_task_excetpion()

        # 清除异常消息,除了本次的message_id
        self.liq.correct_msg_excetpion_but()


