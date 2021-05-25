#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author  : shiwx27477
# @time    : 2021/4/27 10:00
# @file    : master_ora_v202102.py
from unittest import TestCase

from seepp.service.lcs import Liquidate
from util.logging.logger_manager import LoggerFactory


class TestLiquidate(TestCase):
    # init logger
    logger = LoggerFactory(__name__).get_logger()
    liq = Liquidate('local_config_master_ora.ini')
    SYSDATE = '20201203'

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

    def test_health_check(self):
        self.liq.check_services_health()

    def test_refresh_services(self):
        # self.liq.refresh_services()
        self.liq.refresh_service('acs-72')
        self.liq.refresh_service('tcs-72')

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

    def test_update_log_level(self):
        self.liq.update_log_level('acs-72', 'info')
        self.liq.update_log_level('tcs-72', 'info')
        self.liq.update_log_level('query-72', 'info')

    def test_update_log_2kafka(self):
        self.liq.update_log_2kafka('query-72', 'true')
        self.liq.update_log_2kafka('acs-72', 'true')
