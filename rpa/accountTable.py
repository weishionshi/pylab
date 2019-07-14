# -*- coding:utf-8 -*-
import os

try:
    import xlrd
except:
    pass
try:
    import xlwt
except:
    pass


class ExcelWrite(object):

    def __init__(self, encoding='unicode_escape'):
        self.workbook = xlwt.Workbook(encoding=encoding)

    def save(self, file):
        # 先删除已存在文件
        if os.path.exists(file):
            os.remove(file)
        # 保存文件
        self.workbook.save(file)

    def writeByTableData(self, tabledata, rows, cols, sheetname='sheet1'):
        '''
        将数据列表写入xls文件
        :param sheetname:Excel的sheet页名称
        :param tabledata: 表格数据列表
        :param rows:数据行数
        :param cols:数据列数
        :return:
        '''
        sheet = self.workbook.add_sheet(sheetname)
        for row in range(0, int(rows)):
            for col in range(0, int(cols)):
                sheet.write(row, col, tabledata[int(col + (row * cols))])

    def writeDataByRow(self, tabledata, sheetname='sheet1'):
        sheet = self.workbook.add_sheet(sheetname)
        for row in range(len(tabledata)):
            for col in range(len(tabledata[row])):
                sheet.write(row, col, tabledata[row][col])

    def writeDataByCol(self, tabledata, sheetname='sheet1'):
        sheet = self.workbook.add_sheet(sheetname)
        for col in range(len(tabledata)):
            for row in range(len(tabledata[col])):
                sheet.write(row, col, tabledata[col][row])


class ExcelRead(object):

    def __init__(self, file):
        self.workbook = xlrd.open_workbook(file)

    def readElementFromXls(self):
        '''
        获取xls表第一个sheet页的数据，A列为键，B列为值
        :return:
        '''
        xlsValues = dict()
        # 通过索引顺序获取工作表
        table = self.workbook.sheet_by_index(0)
        for i in range(table.nrows):
            xlsValues[table.cell(i, 0).value] = table.cell(i, 1).value
        return xlsValues

    def getDataFromXls(self):
        InputData = list()
        sheet = self.workbook.sheet_by_index(0)
        for i in range(0, sheet.nrows):
            row_data = sheet.row_values(i)
            for j in range(0, len(row_data)):
                row_data[j] = self.__changeIntData(row_data[j])
            InputData.append(row_data)
        return InputData

    def __trans_request_array(self, import_data):
        """
        将申请文件再转化为数据结构
        :param data: 文件数据
        :return: 结构化数据
        """
        # 判断文件是否为空
        if 1 >= len(import_data):
            raise Exception("文件内容为空，请检查！")

        reuest_array = []  # 交易序列
        key_array = import_data[0]  # 列名序列

        # 按行遍历文件(跳过文件头，即第一行)
        for request_index in range(1, len(import_data)):
            # 获取当前行数据
            request_temp = import_data[request_index]

            request_params = {}  # 申请参数值
            # 遍历申请参数值，并将值和列名组装成字典
            for value_index in range(0, len(key_array)):
                key = key_array[value_index]
                value = request_temp[value_index]
                request_params[key] = value

            #  将新申请添加到序列中
            reuest_array.append(request_params)

        return reuest_array

    def trans_xls_to_json(self):
        """
        将xls文件转化为json
        :param xls_path: xls文件路径
        :return:
        """
        # 读取文件内容
        xls_content = self.getDataFromXls()

        # 将文件内容转为 由字典构成的序列的数据结构
        reuest_array = self.__trans_request_array(xls_content)

        # 将数据结构转化为json字符串
        json_str = json.dumps(reuest_array[0], ensure_ascii=False, indent=4).strip()
        return json_str

    def __changeIntData(self, data):
        try:
            temp = int(data)
            if temp == data:
                data = temp
        except:
            pass
        return str(data)


if __name__ == '__main__':
    ee = ExcelRead(r'C:\rpa\账户总表.xls')
    # print(ee.getDataFromXls())
    # xlsReader = ExcelRead(xls_path)
    self.gv_3_accout_table_json = ee.trans_xls_to_json()
    print("===fisrt row in account table: "+ self.gv_3_accout_table_json)

