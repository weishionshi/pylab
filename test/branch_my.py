#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author  : shiwx27477
# @time    : 2021/3/21 17:47
# @file    : master_my_v202102.py
from unittest import TestCase

from seepp.service.lcs import Liquidate
from util.logging.logger_manager import LoggerFactory


class TestLiquidate(TestCase):
    # init logger
    logger = LoggerFactory(__name__).get_logger()
    liq = Liquidate('local_config_branch_my.ini')
    # 公募交易
    SYSDATE = '20210301'
    REQ_DATE = '20210707'
    CONFIRM_DATE = '20210708'
    # 公募清算
    QSYSDATE = '20201104'
    QREQ_DATE = '20201105'
    QCONFIRM_DATE = '20201106'

    # 私募交易
    PSYSDATE = '20210319'
    PREQ_DATE = '2021320'
    PCONFIRM_DATE = '2021321'

    # 私募清算
    PQSYSDATE = '20210323'
    PQREQ_DATE = '20210324'
    PQCONFIRM_DATE = '20210325'

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
        # self.liq.refresh_services_lcs()
        self.liq.refresh_service('acs-133')
        self.liq.refresh_service('tcs-133')
        # self.liq.refresh_service('pps-133')

        # self.liq.refresh_service('acs-158')
        # self.liq.refresh_service('tcs-158')
        # self.liq.refresh_service('pps-133')

    def test_refresh_services_lcs(self):
        self.liq.refresh_services_lcs()

    def test_set_sysdate(self):
        self.liq.set_lcs_sysdate(self.QSYSDATE)
        self.liq.set_tcs_sysdate(self.QSYSDATE)
        self.liq.rds.flushdb()
        self.logger.info('redis flushed!')

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
        self.liq.correct_msg_excetpion_but('13f970e4-1339-41f1-a78b-cc033cfd802c')

    def test_update_log_level(self):
        # self.liq.update_log_level('acs-133', 'info')
        # self.liq.update_log_level('tcs-133', 'info')
        self.liq.update_log_level('query-133', 'debug')

    def test_update_log_2kafka(self):
        self.liq.update_log_2kafka('query-133', 'true')
        self.liq.update_log_2kafka('acs-133', 'true')
