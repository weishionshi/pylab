#!/usr/bin/env python
# coding: utf-8

"""
@File     : ds50Acco.py
@copyright: HS
@Author   : huyb20630
@Date     : 2020/7/4 下午4:32
@Desc     :
"""
import traceback

import cx_Oracle
import MySQLdb
import os
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'


class AccoCreate:

    def __init__(self, username, password, dsn, charset="utf8"):
        # self.conn = cx_Oracle.connect("{0}/{1}@{2}".format(username, password, dsn))
        self.conn = MySQLdb.connect(host=dsn, user=username, passwd=password, db="p1lcs", charset=charset)

        self.cursor = self.conn.cursor()

    def execute(self, sql, params):
        self.cursor.executemany(sql, params)

    def close(self):
        if self.cursor:
            self.cursor.close()

        if self.conn:
            self.conn.close()


# conn_info = {"username": "root", "password": "Caifu123rt", "dsn": "192.168.76.172:3306/p1lcs"}
conn_info = {"username": "root", "password": "Caifu123rt", "dsn": "192.168.76.172"}
conn = AccoCreate(**conn_info)

# 账户信息 cust_no cust_name identity_no
sql_custinfo = f""" INSERT INTO `lc_tcustinfo`(`VC_TENANT_ID`, `VC_CUST_NO`, `C_CUST_TYPE`, `VC_CUSTOM_NAME`, `C_IDENTITY_TYPE`, `VC_IDENTITY_NO`, `C_ACCO_STATE`, `VC_LAST_DATE`, `GMT_CREATE`, `GMT_MODIFIED`, `C_CUST_KIND`)
               VALUES ('10000', %s, '1', %s, '1', %s, '0', '20191212', NULL, NULL, NULL)"""
params_custinfo = []

# 基金账号信息 cust_no fund_acco
sql_fundacco = f"""INSERT INTO `lc_tfundacco`(`VC_TENANT_ID`, `VC_CUST_NO`, `VC_FUND_ACCO`, `C_ACCO_STATE`, `VC_TA_CODE`, `C_TA_CUST_TYPE`, `GMT_CREATE`, `GMT_MODIFIED`)
               VALUES ('10000', %s, %s, '0', '25', NULL, NULL, NULL)"""
params_fundacco = []

# 银行账户信息 cust_no cust_name
sql_accobank = f"""INSERT INTO `lc_taccobank`(`VC_TENANT_ID`, `VC_CUST_NO`, `C_BANK_NO`, `VC_BANK_ACCO`, `VC_BANK_NAME`, `VC_NAME_IN_BANK`, `VC_BANK_PROVINCE_CODE`, `VC_BANK_CITY_NO`, `C_ACCO_STATE`, `C_BACK_FLAG`, `GMT_CREATE`, `GMT_MODIFIED`, `VC_BANK_CARD_NO`, `VC_BRANCH_BANK`)
                VALUES ('10000', %s, '003', '002444598585840128', '中国农业银行', %s, NULL, NULL, '0', '1', NULL, NULL, %s, NULL)"""
params_accobank = []

# 交易账号信息 cust_no bank_card_no trade_acco
sql_accoinfo = f"""INSERT INTO `lc_taccoinfo`(`VC_TENANT_ID`, `VC_CUST_NO`, `VC_BANK_CARD_NO`, `C_CUST_TYPE`, `VC_TRADE_ACCO`, `VC_NET_NO`, `VC_BROKER`, `VC_CENTER_NO`, `C_USER_TYPE`, `VC_COME_FROM`, `C_ACCO_STATE`, `C_DIVIDEND_METHOD`, `C_AUTO_FLAG`, `VC_LAST_DATE`, `VC_SELLER`, `VC_MANAGER_CODE`, `GMT_CREATE`, `GMT_MODIFIED`, `VC_CITY_NO`)
                VALUES ('10000', %s, %s, '1', %s, '0001', NULL, '000', NULL, NULL, '0', NULL, NULL, '20191215', NULL, NULL, NULL, NULL, NULL)"""
params_accoinfo = []

# 资金账号信息 cust_no trade_acco cap_acco bank_card_no
sql_capitalacco = f"""INSERT INTO `lc_tcapitalacco`(`VC_TENANT_ID`, `VC_CUST_NO`, `VC_TRADE_ACCO`, `VC_CAP_ACCO`, `VC_BANK_CARD_NO`, `C_CAPITAL_MODE`, `C_SUB_CAPITAL_MODE`, `VC_CD_CARD`, `C_REMITTANCE_FLAG`, `C_INTERFACE_TYPE`, `C_ACCO_STATE`, `VC_LAST_DATE`, `GMT_CREATE`, `GMT_MODIFIED`)
                   VALUES ('10000', %s, %s, %s, %s, 'A', NULL, '1', '0', NULL, '0', '20191212', NULL, NULL)"""
params_capitalacco = []

# 账户关联表 cust_no fund_acco trade_acco
sql_relation = f"""INSERT INTO `lc_taccorelation`(`VC_TENANT_ID`, `VC_CUST_NO`, `VC_FUND_ACCO`, `VC_TRADE_ACCO`, `VC_TA_CODE`, `GMT_CREATE`, `GMT_MODIFIED`)
                VALUES ('10000', %s, %s, %s, '25', NULL, NULL)"""
params_relation = []

# 账户确认表 cust_no trade_acco fund_acco requeset_no comfirm_no identity_no VC_CUSTOM_NAME
sql_accoconfirm = f"""INSERT INTO `lc_taccoconfirm`(`VC_TENANT_ID`, `VC_CUST_NO`, `VC_TRADE_ACCO`, `VC_FUND_ACCO`, `C_TRUST`, `VC_REQUEST_NO`, `VC_CONFIRM_DATE`, `VC_CONFIRM_NO`, `C_BUSIN_FLAG`, `VC_REQUEST_DATE`, `VC_REQUEST_TIME`, `VC_NET_NO`, `C_CUST_TYPE`, `C_FROZEN_CAUSE`, `VC_ERROR_CODE`, `VC_ERROR_CAUSE`, `EN_UNFROZEN_BALA`, `VC_TA_CUST_NO`, `C_ORGANIGER`, `C_CONFIRM_FLAG`, `VC_BROKER`, `VC_CITY_NO`, `VC_SELLER`, `VC_TA_CODE`, `C_IDENTITY_TYPE`, `VC_IDENTITY_NO`, `VC_CUSTOM_NAME`, `VC_PRODUCT_ACCO_RECORD_NO`, `GMT_CREATE`, `GMT_MODIFIED`, `VC_REMARK`)
                   VALUES ('10000', %s, %s, %s, '2', %s, '20191215', %s, '101', '20191212', '015030', '0001', '1', NULL, '0000', NULL, NULL, NULL, '0', '1', NULL, NULL, NULL, '25', '1', %s, %s, NULL, NULL, NULL, NULL)"""
params_accoconfirm = []

# 账户申请表 cust_no requeset_no trade_acco fund_acco identity_no bank_card_no
sql_accorequest = f"""INSERT INTO `lc_taccorequest`(`VC_TENANT_ID`, `VC_CUST_NO`, `VC_REQUEST_NO`, `VC_TRADE_ACCO`, `VC_FUND_ACCO`, `C_TRUST`, `VC_REQUEST_DATE`, `VC_REQUEST_TIME`, `C_CONFIRM_FLAG`, `C_FROZEN_FLAG`, `C_FROZEN_CAUSE`, `C_BUSIN_FLAG`, `C_FIX_BUSIN_FLAG`, `VC_NET_NO`, `VC_CENTER_NO`, `VC_ORIGIN_NO`, `VC_SYS_DATE`, `VC_TA_CODE`, `VC_MACHINE_DATE`, `VC_MACHINE_TIME`, `VC_COME_FROM`, `VC_BATCH_REQUEST_NO`, `VC_CHINA_PAY_SERIAL_NO`, `VC_OTHER_USER_ID`, `VC_PARTNER_ID`, `VC_MANAGER_CODE`, `VC_CONFIRM_SETTLE_DATE`, `C_EXPORT_STATE`, `VC_ADDRESS`, `VC_INSTREPR_NO`, `C_INSTREPR_TYPE`, `VC_INSTREPR_NAME`, `C_IDENTITY_TYPE`, `VC_IDENTITY_NO`, `VC_CUSTOM_NAME`, `C_CUST_TYPE`, `VC_ZIP`, `VC_CONT_ID_NO`, `C_CONT_TYPE`, `VC_CONTACT`, `VC_BIRTH_DATE`, `VC_CITY_NO`, `C_EDUCATION`, `VC_EMAIL`, `VC_FAX_NO`, `C_VOCATION`, `VC_PHONE`, `EN_YEAR_INCOME`, `VC_MOBILE_NO`, `VC_CIPHER_TEXT`, `C_SEX`, `VC_SH_ACCO`, `VC_SZ_ACCO`, `C_BILL_WAY`, `VC_NAME_IN_BANK`, `VC_BANK_NAME`, `VC_BANK_ACCO`, `C_BANK_NO`, `C_BILL_PATH`, `VC_NATIONALITY`, `VC_BROKER`, `VC_OFFICE`, `VC_ID_VALID_DATE`, `VC_INSTREPR_VALID_DATE`, `VC_ORG_HOLDING_NAME`, `VC_HOLDING_NAME`, `C_MARRIAGE`, `C_CUST_KIND`, `VC_FIRST_NAME`, `VC_LAST_NAME`, `VC_TRADE`, `C_EMPLOYEE_NUM`, `C_INTEREST`, `C_PROVINCE_CODE`, `VC_COUNTY_NO`, `VC_RECOMMENDER`, `C_RECOMMENDER_TYPE`, `C_COR_PROPERTIY`, `VC_BATCH_NO`, `VC_ALLOW_TRUST`, `GMT_CREATE`, `GMT_MODIFIED`, `C_DIVIDEND_METHOD`, `VC_BANK_PROVINCE_CODE`, `VC_BANK_CITY_NO`, `C_SUB_CAPITAL_MODE`, `VC_CD_CARD`, `C_USER_TYPE`, `VC_CONT_VALID_DATE`, `VC_PRODUCT_ACCO_RECORD_NO`, `VC_SELLER`, `C_ORG_TYPE`, `VC_INVESTOR_PRODUCT_CODE`, `VC_ASSIST_ID_TYPE`, `VC_ASSIST_ID_NO`, `VC_ASSIST_ID_VALID_DATE`, `VC_IP_ADDRESS`, `VC_MAC_ADDRESS`, `VC_IMEI`, `VC_UUID`, `L_NO`)
                   VALUES ('10000', %s, %s, %s, %s, '2', '20191212', '015030', '1', NULL, NULL, '001', NULL, '0001', '000', NULL, '20191212', '25', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '20191215', '1', NULL, NULL, NULL, NULL, '1', %s, '对接投顾003', '1', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '对接投顾003', '中国农业银行', %s, '003', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '0201912121517153044', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '1', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, %s)"""
params_accorequest = []

for index in range(426000, 750000):
    cust_no = "TMP{0}".format(str(index).zfill(8))
    identity_no = "2018080700{0}".format(str(index).zfill(8))
    cust_name = "create{0}".format(str(index).zfill(8))
    fund_acco = "2500{0}".format(str(index).zfill(8))
    bank_card_no = "{0}".format(str(index).zfill(8))
    trade_acco = "{0}".format(str(index).zfill(8))
    cap_acco = "{0}".format(str(index).zfill(8))
    requeset_no = "20180807{0}".format(str(index).zfill(6))
    comfirm_no = "20180807{0}".format(str(index).zfill(6))


    # 账户信息 cust_no cust_name identity_no
    params_custinfo.append((cust_no, cust_name, identity_no))

    # 基金账号信息 cust_no fund_acco
    params_fundacco.append((cust_no, fund_acco))

    # 银行账户信息 cust_no cust_name
    params_accobank.append((cust_no, cust_name, bank_card_no))

    # 交易账号信息 cust_no bank_card_no trade_acco
    params_accoinfo.append((cust_no, bank_card_no, trade_acco))

    # 资金账号信息 cust_no trade_acco cap_acco bank_card_no
    params_capitalacco.append((cust_no, trade_acco, cap_acco, bank_card_no))

    # 账户关联表 cust_no fund_acco trade_acco
    params_relation.append((cust_no, fund_acco, trade_acco))

    # 账户确认表 cust_no trade_acco fund_acco requeset_no comfirm_no identity_no
    params_accoconfirm.append((cust_no, trade_acco, fund_acco, requeset_no, comfirm_no, identity_no, cust_name))

    # 账户申请表 cust_no requeset_no trade_acco fund_acco identity_no bank_card_no
    params_accorequest.append((cust_no, requeset_no, trade_acco, fund_acco, identity_no, bank_card_no, index))

    if index != 0 and index%100 == 0:
        print(index)
        try:
            # print('params_custinfo:', params_custinfo)
            conn.execute(sql_custinfo, params_custinfo)
            conn.execute(sql_fundacco, params_fundacco)
            conn.execute(sql_accobank, params_accobank)
            conn.execute(sql_accoinfo, params_accoinfo)
            conn.execute(sql_capitalacco, params_capitalacco)
            conn.execute(sql_relation, params_relation)
            conn.execute(sql_accoconfirm, params_accoconfirm)
            conn.execute(sql_accorequest, params_accorequest)
            conn.conn.commit()

            # 初始化
            params_custinfo = []
            params_fundacco = []
            params_accobank = []
            params_accoinfo = []
            params_capitalacco = []
            params_relation = []
            params_accoconfirm = []
            params_accorequest = []

        except:
            traceback.print_exc()
            conn.conn.rollback()

conn.close()
