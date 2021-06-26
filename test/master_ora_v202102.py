#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author  : shiwx27477
# @time    : 2021/4/27 10:00
# @file    : master_ora_v202102.py
import time
from unittest import TestCase

from seepp.service.lcs import Liquidate
from util.logging.logger_manager import LoggerFactory


class TestLiquidate(TestCase):
    # init logger
    logger = LoggerFactory(__name__).get_logger()
    liq = Liquidate('local_config_master_ora.ini')
    SYSDATE = '20210603'

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

    def test_refresh_service(self):
        self.liq.refresh_service('acs-158')
        self.liq.refresh_service('tcs-158')

    def test_refresh_services_tcs(self):
        self.liq.refresh_services()

    def test_refresh_services_lcs(self):
        self.liq.refresh_services_lcs()

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
        message_id = 'd45840e4-f990-4166-9104-246e41c4f8a7'
        # 清除异常任务
        self.liq.correct_task_excetpion()

        # 清除异常消息,除了本次的message_id
        self.liq.correct_msg_excetpion_but(message_id)

    def test_trigger_exportliqfile(self):
        """
        触发清算定时任务:EXPORTLIQFILE-导出清算文件,
        @return:
        """
        task_name = 'EXPORTLIQFILE'
        # 清除异常任务
        self.liq.correct_task_excetpion()
        # 修改时间和状态
        self.liq.trigger_auto_task(task_name)


    def test_update_log_level(self):
        level = 'info'
        # self.liq.update_log_level('acs-158', level)
        # self.liq.update_log_level('tcs-158', level)
        # self.liq.update_log_level('query-158', level)

        self.liq.update_log_level('acs-72', level)
        self.liq.update_log_level('tcs-72', level)
        self.liq.update_log_level('query-72', level)

        # self.liq.update_log_level('lcs-158', level)
        # self.liq.update_log_level('lcs-175', level)

    def test_update_log_2kafka(self):
        self.liq.update_log_2kafka('query-158', 'true')
        self.liq.update_log_2kafka('acs-158', 'true')

    def test_call_create_lcs_request_hisrory(self):
        cursor = self.liq.conn_lcs.cursor()

        try:
            cursor.execute('truncate table LC_THREQUEST')

        except Exception as e:
            self.conn_tcs.rollback()
            self.logger.error(e, exec_info=True)
        finally:
            cursor.close()

        for i in range(1, 13):  # ta个数
            ta_code = str(i).zfill(2)
            for j in range(1, 6):  # 产品个数
                product_code = ta_code + str(j).zfill(4)
                self.logger.info(ta_code + ',' + product_code)
                self.liq.call_procedure('lcs', 'CREATE_LCS_REQUEST_HISTORY', ['50000', ta_code, product_code, '022', '100'])
                time.sleep(2)
