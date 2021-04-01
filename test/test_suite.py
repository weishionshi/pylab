#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author  : shiwx27477
# @time    : 2020/4/14 10:17
# @file    : test_suite.py
import unittest
import datetime

from test.test_main import UnitTest
#from test.HTMLTestRunner import HTMLTestRunner

if __name__ == '__main__':
    suite = unittest.TestSuite()
    # load UnitTest类中的所有case
    # suite.addTests(unittest.TestLoader().loadTestsFromTestCase(UnitTest))

    # 自定义case
    tests = [UnitTest("test_get_tcs_sysdate")]
    suite.addTests(tests)

    # txt版报告
    with open('UnittestTextReport.txt', 'a') as f:
        runner = unittest.TextTestRunner(stream=f, verbosity=2)
        runner.run(suite)

    time = datetime.datetime.now().strftime('%H:%M:%S')
    print('date -s "20201009 %s"' % time)

    # html版报告,TODO:报错
    # with open('HTMLReport.html', 'w') as f:
    #     runner = HTMLTestRunner(stream=f,
    #                             title='MathFunc Test Report',
    #                             description='generated by HTMLTestRunner.',
    #                             verbosity=2
    #                             )
    #     runner.run(suite)
