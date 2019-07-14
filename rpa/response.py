#!/usr/bin/env python
# _*_coding:utf-8_*_

'''
@File     : CombineMessage.py
@copyright: HS
@Author   : huyb20630
@Date     : 2019-07-10 9:13
@Desc     : 数据存放类
'''
import json
import ast
import logging
import time

# 创建一个日志器logger并设置其日志级别为DEBUG
logger = logging.getLogger('simple_logger')
logger.setLevel(logging.DEBUG)

# 创建一个流处理器handler并设置其日志级别为DEBUG
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)

# 创建一个格式器formatter并将其添加到处理器handler
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

# 为日志器logger添加上面创建的处理器handler
logger.addHandler(handler)


class ReturnObject(object):
    """
    所有返回数据的父类，用于实现公用方法
    """

    def __init__(self):
        raise NotImplementedError("当前类为接口类")

    def __str__(self):
        return json.dumps(self.__dict__, default=lambda o: o.__dict__, ensure_ascii=False)


class BankReceipt(ReturnObject):
    """
    电子回单信息
    """

    def __init__(self):
        self.occurDate = ""
        self.bankNo = ""
        self.bankName = ""
        self.bankAcco = ""
        self.fileName = ""
        self.filePath = ""
        self.importTime = ""
        self.bankSerialNo = ""


class BankTradeDetail(ReturnObject):
    """
    银行交易明细
    """

    def __init__(self):
        self.occurDate = ""
        self.occurTime = ""
        self.bankNo = ""
        self.bankName = ""
        self.bankAcco = ""
        self.otherBankAcco = ""
        self.otherAccoName = ""
        self.otherBankName = ""
        self.direct = ""
        self.occurBala = 0
        self.moneyType = 0
        self.transType = ""
        self.totalBala = 0
        self.purpos = ""
        self.postScript = ""
        self.nameInBank = ""
        self.importTime = ""
        self.fundCode = ""
        self.bankSerialNo = ""
        self.otherLargeBankNo = ""
        self.dataMode = 2
        self.summary = ""
        self.bankReceipts = None


class BankAccoBala(ReturnObject):
    """
    账户余额
    """

    def __init__(self):
        self.acctNo = ""
        self.bankNo = ""
        self.nameInBank = ""
        self.date = ""
        self.importTime = ""
        self.moneyType = ""
        self.totalBala = 0
        self.usableBala = 0
        self.fundCode = ""
        self.dataMode = 2


class ResultJson(ReturnObject):
    """
    结果报文
    """

    def __init__(self):
        self.bankName = "招商银行"
        self.loginInBankAcco = ""
        self.bankAccoBalas = []
        self.banktradedetails = []


class Response(ReturnObject):
    """
    响应报文
    """

    def __init__(self):
        self.taskId = ""
        self.type = 5
        self.code = ""
        self.msg = ""
        self.status = 0
        self.resultJson = []


def assemble(account_table, trade_detail, result_json):
    # 封装账户余额
    # logger.debug("===original account info:" + str(account_table))

    account_balance = BankAccoBala()
    balance_dict = ast.literal_eval(account_table)[0]
    logger.debug("=== account summary:" + str(balance_dict))
    account_balance.acctNo = balance_dict['账号'].split(",")[1]
    # TODO,bankNO待确认
    account_balance.bankNo = "15"
    account_balance.nameInBank = balance_dict['账户名']
    account_balance.moneyType = balance_dict['账号'].split(",")[2]
    account_balance.totalBala = balance_dict['余额']
    account_balance.usableBala = balance_dict['可用额度']
    # TODO
    # account_balance.date
    # account_balance.fundCode
    account_balance.dataMode = "2"

    logger.info("账户余额对象：" + account_balance.__str__())

    # 封装交易明细
    trade_detail_list = []
    temp_list = ast.literal_eval(trade_detail)
    for temp in temp_list:
        # init obj
        trade_detail = BankTradeDetail()
        receipt = BankReceipt()
        # set attribute
        trade_detail.occurDate = temp['交易日']
        trade_detail.occurTime = temp['交易时间']
        trade_detail.bankNo = account_balance.bankNo
        # TODO,bankName
        trade_detail.bankName = "招商银行" + balance_dict['账号'].split(",")[0]
        trade_detail.nameInBank = account_balance.nameInBank
        trade_detail.bankAcco = account_balance.acctNo
        trade_detail.otherBankName = temp['收/付方开户行名']
        trade_detail.otherAccoName = temp['收/付方名称']
        trade_detail.otherBankAcco = temp['收/付方账号']
        # TODO
        if len(temp['借方金额']) > 0:
            trade_detail.direct = "借"
            trade_detail.occurBala = temp['借方金额']
        if len(temp['贷方金额']) > 0:
            trade_detail.direct = "贷"
            trade_detail.occurBala = temp['贷方金额']

        trade_detail.moneyType = account_balance.moneyType
        trade_detail.transType = temp['交易类型']
        trade_detail.totalBala = temp['余额']
        trade_detail.purpos = temp['用途']
        # TODO trade_detail.postScript = temp['业务摘要']
        # TODO trade_detail.importTime =
        # TODO trade_detail.fundCode =
        trade_detail.bankSerialNo = temp['流水号']
        # TODO trade_detail.otherLargeBankNo = temp['']
        trade_detail.dataMode = "2"
        trade_detail.summary = temp['摘要']

        # set attribute for bank receipt
        receipt.bankSerialNo = trade_detail.bankSerialNo
        # TODO receipt.importTime =
        receipt.bankAcco = trade_detail.bankAcco
        receipt.bankNo = trade_detail.bankNo
        receipt.bankName = trade_detail.bankName
        receipt.fileName = "CMBReceipt-" + receipt.bankSerialNo + ".pdf"
        receipt.filePath = self.gv_3_base_dir + '\\' + time.strftime("%Y%m%d",
                                                                     time.localtime()) + '\\' + receipt.fileName
        receipt.occurDate = trade_detail.occurDate

        trade_detail.bankReceipts = receipt

        trade_detail_list.append(trade_detail)

        # logger.debug("for each trade_detail:" + str(trade_detail))

    logger.info("trade_detail_list:" + str(trade_detail_list))

    result_json.bankAccoBalas.append(account_balance)
    result_json.banktradedetails.append(trade_detail_list)


if __name__ == '__main__':
    # init response
    resultJson = ResultJson()
    response = Response()

    for tuple_ in self.gv_3_file_json_list:
        assemble(tuple_[1], tuple_[2], resultJson)
    # TODO response.taskId = ""
    response.resultJson = resultJson
    logger.debug("response json:" + response.__str__())
