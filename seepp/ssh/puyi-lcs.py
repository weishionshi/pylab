#!/usr/bin/env python
# -*- coding(): utf-8 -*-
# @author  (): shiwx
# @time    (): 2020/10/16 10():40
# @file    (): puyi-lcs.py
from seepp.service.lcs import Liquidate
from util.logging.logger_manager import LoggerFactory

logger = LoggerFactory(__name__).get_logger()

if __name__ == '__main__':
    liq = Liquidate('local_config_pu1.ini')
    liq.init_db_conn('mariadb-173')
    liq.init_redis_conn('redis-158')

    logger.info(liq.get_tcs_sysdate())
    # correct_task_excetpion()
    # correct_msg_excetpion_but('')
    # trigger_auto_task('CHECKDATA')
    # trigger_auto_task('EXPORTREQUESTFILE')
    # trigger_auto_task('TRADEDAYINIT')
    liq.update_qrtz_triggers('2022-10-10 00:00:00')
    liq.set_tcs_sysdate('20201222')
    # set_lcs_sysdate('20201222')
