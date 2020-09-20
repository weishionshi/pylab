import traceback

from util.db.pymysql_builder import PyMysqlFactory


class CCSPreset:
    def __init__(self, host, port, user, password, database):
        self.conn = PyMysqlFactory(host, port, user, password, database).get_connection()
        self.prefix = 'PF'

    @property
    def ta_cnt(self):
        return self._ta_cnt

    @ta_cnt.setter
    def ta_cnt(self, ta_cnt):
        if not isinstance(ta_cnt, int):
            raise TypeError("Expected a int")
        if ta_cnt < 0 or ta_cnt > 99:
            raise ValueError('ta_cnt must between 0 ~ 255!')
        self._ta_cnt = ta_cnt

        @property
        def prd_cnt(self):
            return self._prd_cnt

        @prd_cnt.setter
        def prd_cnt(self, prd_cnt):
            if not isinstance(prd_cnt, int):
                raise TypeError("Expected a int")
            if prd_cnt % self.ta_cnt != 0:
                raise ValueError('prd_cnt必须是ta_cnt的整数倍')
            self._prd_cnt = prd_cnt

    def insert_ta_info(self):
        self.conn.ping(reconnect=True)
        cursor = self.conn.cursor()
        sql_ta = """
        INSERT INTO pf_ttainfo (VC_TENANT_ID, VC_TA_CODE, VC_TA_NAME, VC_SUPBANK_NO) VALUES ('10000', %s, %s, 'C10305');
        """
        sql_prd = """
        INSERT INTO pf_tfundinfo (VC_TENANT_ID, VC_PRODUCT_CODE, VC_PRODUCT_NAME, VC_MAIN_PRODUCT_CODE, VC_TA_CODE,
                                  C_MONEY_TYPE, VC_TA_ACCO_ID, VC_COLLECT_ACCO_ID, VC_SALE_ACCO_ID, VC_SYS_TYPES,
                                  VC_DEAL_TIME, C_PRODUCT_TYPE, VC_PRODUCT_MANAGER_CODE, VC_GATHER_FLAG,
                                  VC_BUSIN_GATHER_FLAG, VC_ATTRIBUTION, VC_FUND_ATTRIBUTE, VC_EXPLAIN,
                                  VC_LAST_MODIFY_DATE, VC_TRUSTEE_MODE, VC_TRUSTEE_ACCO_ID, VC_SH_ACCO_ID,
                                  VC_SZ_ACCO_ID, VC_SH_FARE_ACCO_ID, VC_SZ_FARE_ACCO_ID, VC_COLLECT_FLAG,
                                  VC_TA_DEAL_TIME, EN_FUND_ID, VC_TRUSTEE_DIV_MODE, VC_PRODUCT_GROUP_CODE,
                                  VC_CUSTODIAN_NO, VC_SUB_INTEREST_MODE, L_SUB_SCRIBE_DAY, VC_SUB_FARE_FLAG,
                                  VC_PROFIT_BUSIN_FLAG, VC_SERVICE_FARE_FLAG, VC_RECSF_SETTLE_FLAG,
                                  VC_PAYSF_SETTLE_FLAG, VC_TG_NOT_SETTLE_BUSIN, VC_COMP_FARE_ACCO_ID, VC_CAPDATE_CODE,
                                  VC_SUBINTEREST_MAIN_MODE, EN_INVESTMENT_ADV_RATE, VC_INVESTMENT_ADV_ACCO_ID,
                                  VC_FARE_DELAY_DAY, C_PRODUCT_STATE, C_PRODUCT_SUB_TYPE)
        VALUES ('10000', %s, %s, null, %s, '156',
                'TAH001', 'MJH001', 'ZXB001', '1', '0', '0', null, '1', '0', null, '1', null, null, null, null, null,
                null, null, null, null, '0', null, '0', '000000', null, '1', null, null, null, '0', null, null, null,
                null, null, null, null, null, null, '0', null);
        """

        for i in range(0, self._ta_cnt):
            try:
                ta_code = "{0}".format(str(i).zfill(2))
                cursor.execute(sql_ta, [ta_code,
                                        "TA{0}".format(str(i).zfill(3))])

                for j in range(0, self.prd_cnt // self.ta_cnt):
                    cursor.execute(sql_prd, [ta_code + "{0}".format(str(j).zfill(4)), "压测产品{0}".format(str(j).zfill(4)),
                                             ta_code])

            except:
                traceback.print_exc()
                self.conn.rollback()

        self.conn.commit()
        # 关闭光标对象
        cursor.close()
        # 关闭数据库连接
        self.conn.close()
        print('%d rows ta info inserted' % self.ta_cnt)
        print('%d rows prd info inserted' % self.prd_cnt)


if __name__ == '__main__':
    ccs = CCSPreset('192.168.76.172', 3307, 'root', 'Caifu123rt', 'pu1ccs')
    ccs.ta_cnt = 2
    ccs.prd_cnt = 10
    ccs.insert_ta_info()
