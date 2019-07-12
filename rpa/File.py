# -*- coding:utf-8 -*-
import os


def listdir(path, list_name):
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
            listdir(file_path, list_name)
        elif os.path.splitext(file_path)[1] == '.xls':
            list_name.append(file_path)


def get_file_name_list(path, file_list):
    for files in os.walk(path):
        for file_ in files[2]:
            if file_.startswith("账户总表"):
                pos = file_.find(".xls")
                account_no = file_[5:pos]
                print("account no:" + account_no)
                path = os.path.join(files[0], file_)
                # TODO 检查改文件是否存在
                trade_detail_path = os.path.join(files[0], "历史交易-" + account_no + ".xls")
                file_tuple = (account_no, path, trade_detail_path)
        file_list.append(file_tuple)


if __name__ == '__main__':
    base_dir = 'c:\\rpa\\20190711'

    # for files in os.walk(base_dir):
    #     print(files)
    #
    # name_list = []
    # listdir(base_dir, name_list)
    # print("files:" + str(name_list))

    file_list = []
    get_file_name_list(base_dir, file_list)
    print(str(file_list))
