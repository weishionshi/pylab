#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author  : shiwx27477
# @time    : 2021/4/20 16:23
# @file    : aio_lcs.py
from unittest import TestCase

from seepp.service.lcs import Liquidate
from util.logging.logger_manager import LoggerFactory


class TestLiquidate(TestCase):
    # init logger
    logger = LoggerFactory(__name__).get_logger()
    liq = Liquidate('local_config_master_aio.ini')
    SYSDATE = '20210421'
    SALECODE = '225'

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


    def test_init_env(self):
        """
        开始跑清算前的环境初始化
        @return:
        """
        self.liq.set_lcs_sysdate(self.SYSDATE)
        self.liq.set_tcs_sysdate(self.SYSDATE)

        self.liq.set_tcs_sale_code(self.SALECODE)
        self.liq.set_lcs_sale_code(self.SALECODE)

        self.liq.correct_task_excetpion()
        self.liq.correct_msg_excetpion_but()

        # TODO:设置垫资户
        # TODO:把基础数据从交易库同步到清算库

    def test_set_sysdate(self):
        self.liq.set_lcs_sysdate(self.SYSDATE)
        self.liq.set_tcs_sysdate(self.SYSDATE)

    def test_pre_check(self):
        self.liq.pre_check(self.SYSDATE)

    def test_refresh_service(self):
        self.liq.refresh_services()

    def test_correct_exception(self):
        self.liq.correct_task_excetpion()
        self.liq.correct_msg_excetpion_but()

    def test_prepare_deal_data(self):
        """
        处理确认数据,前置准备
        @return:
        """
        self.liq.correct_task_excetpion()
        self.liq.correct_msg_excetpion_but()

        # tainfo.C_TA_DEAL_FLAG
        self.liq.reset_ta_deal_flag('00')

        # 处理确认数据
        self.liq.reset_lcs_process('DEALDATA')