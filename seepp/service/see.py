#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author  : shiwx27477
# @time    : 2021/4/28 15:39
# @file    : see.py

import base64
import datetime
import hashlib
import hmac
import json
import logging
import os
import time
import uuid
import requests
import sys
import traceback

from util.logging.logger_manager import LoggerFactory

if sys.version_info[0] == 2:
    from urllib import urlencode, quote
else:
    from urllib.parse import urlencode, quote

logger = LoggerFactory(__name__).get_logger()

'*********************************************SEE平台客户端****************************************'


class RequestFailed(Exception):
    pass


class SeeBaseClient(object):

    def __init__(self, url, user, passwd):
        self.session = requests.Session()
        self.url = url
        self.access_key_id = user
        # self.access_key_secret = hashlib.sha512(passwd).hexdigest()
        sha512 = hashlib.sha512()
        sha512.update(bytes(passwd, encoding='utf-8'))
        self.access_key_secret = sha512.hexdigest().encode('utf-8')

    def signature(self, method, params):
        if params is None:
            params = {}
        public = {
            "Version": "v1",
            "AccessKeyId": self.access_key_id,
            "TimeStamp": self.timestamp(),
            "SignatureMethod": "HMAC-SHA1",
            "SignatureVersion": '1.0',
            "SignatureNonce": str(uuid.uuid4()),
            "Format": "JSON",
            "AccesKeySecret": self.access_key_secret
        }
        params.update(public)
        for k, v in params.items():
            if isinstance(v, (list, dict)):
                params[k] = json.dumps(v)
        query = urlencode(sorted(params.items())).replace('+', '%20').replace('%7E', '~')
        to_sign = method.upper() + '&' + quote('/', safe='') + '&' + quote(query, safe='')
        signature = hmac.new((self.access_key_secret.decode('utf-8') +
                              '&').encode('utf-8'), to_sign.encode('utf-8'), hashlib.sha1)
        params['Signature'] = base64.encodestring(signature.digest()).strip()
        return params

    @staticmethod
    def quote(s):
        return quote(s).replace('%7E', '~')

    @staticmethod
    def timestamp():
        return datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    def get(self, params=None, **kwargs):
        params = self.signature('get', params)
        try:
            rsp = self.session.get(self.url, params=params, **kwargs)
            if rsp.status_code != 200:
                raise RequestFailed('%srequest failed: %s' % (params.get('Action', ''), rsp.text))
        except requests.RequestException as e:
            raise RequestFailed('request failed: %s' % str(e))
        else:
            return json.loads(rsp.text)


class SeeClient(SeeBaseClient):

    def app_system_list(self, app_name, prod_type_name, prod_type, prod_id="", life_cycle="", env_id="001"):
        """
        获取应用系统列表
        :param app_name: 应用名称
        :param prod_type_name: 发布物次类型
        :param prod_type: 发布物类型 SEE.PATCH或者SEE.PRODUCT（不传则获取所有）
        :param prod_id: 发布物ID
        :param life_cycle: 应用系统状态 成功: 100 失败: 140 待部署: 60 部署中: 80
        :param env_id: 环境ID
        :return:
        """
        data = {
            'Action': 'AppSystemList',
            'SystemId': '',
            'Name': app_name,
            'LifeCycle': life_cycle,
            'ProductId': prod_id,
            'ProductType': prod_type,
            'ProductVersion': '',
            'Category': '',
            'ProductTypeName': prod_type_name,
            'EnvironmentId': env_id
        }
        if life_cycle is None:
            data.pop("LifeCycle")
        return self.get(params=data)

    def get_app(self, prod_type_name="", prod_type="", prod_id="", app_name="", life_cycle="", env_id="001"):
        """
        获取应用系统列表
        :param prod_type_name: 发布物次类型（应用类型）
        :param prod_type: 发布物类型 SEE.PATCH或者SEE.PRODUCT（不传则获取所有）
        :param prod_id: 发布物ID
        :param app_name: 应用名称
        :param life_cycle: 应用系统状态 成功: 100 失败: 140 待部署: 60 部署中: 80
        :param env_id: 环境ID
        :return:
        """
        apps = self.app_system_list(app_name, prod_type_name, prod_type, prod_id, life_cycle, env_id)
        # print("application: {0}".format(",".join([item['productId'] for item in apps])))
        if len(apps) != 0:
            logger.debug('app list:' + str(apps))
            return apps[0]
        else:
            raise Exception("{0}应用不存在，请检查！{1}".format(prod_type_name, traceback.print_exc()))
            sys.exit(1)

    def upgrade_app(self, prod_id="", app_id="", *servers, env_id="001"):
        """
        根据指定的发布物升级指定的应用
        :param prod_id: 发布物ID
        :param app_id: 应用ID
        :param servers: {
                            "cs_instance_id": "",  # id或者ip必须填一项
                            "ip": "127.0.0.1",  # id或者ip必须填一项
                            "user": "用户名",  # 选填,使用该用户安装
                            "workspace": "安装目录",  # 选填,安装目录
                            "is_delete": "true",  # 选填,标记删除
                            "args": {}
                        }
        :return:
        """
        data = {
            "Action": "AppUpgradeByProduct",
            "ProductId": prod_id,
            "SystemId": app_id,
            'EnvironmentId': env_id,  # 环境id 默认是001
            "Nodes": [{
                'ID': '',
                'Servers': servers
            }]

        }
        return self.get(params=data)

    def get_stacks(self, **kwargs):
        """
        获取栈信息
        :return:
        """
        env_id = kwargs.get("environment") or "001"

        data = {
            "Action": "CiStackList",
            'EnvironmentId': env_id,  # 环境id 默认是001
        }
        resp = self.get(params=data)
        # logger.info("获取到栈信息：{0}".format(resp))
        for stack in resp:
            flag = True
            for param in kwargs:
                if kwargs[param] != stack.get(param):
                    flag = False
                    break

            if flag:
                yield stack

    def product_upload(self, ftp_host="", ftp_port="", ftp_path="", ftp_usr="", ftp_pwd="", env_id="001"):
        """
        微服务上传see
        :param ftp_host: ip
        :param ftp_port: port
        :param ftp_path: 发布包路径
        :param ftp_usr: 用户
        :param ftp_pwd: 密码
        :param env_id: 环境ID
        :return:
        """
        data = {
            'Action': 'ProductUpload',
            'RepositoryType': 'SFTP',
            'RepositoryHost': ftp_host,
            'RepositoryPort': ftp_port,
            'RepositoryPath': ftp_path,
            'RepositoryUser': ftp_usr,
            'RepositoryPwd': ftp_pwd,
            'RepositoryEncoding': 'utf-8',
            'EnvironmentId': env_id
        }

        return self.get(params=data)


def upgrade_app(see, prod_id, app_id, env_id="001", ):
    """
    升级应用
    :param prod_id: 发布物ID
    :param app_id: 应用ID
    :return:
    """
    logger.info("开始更新应用。")
    for i in range(3):
        result = see.upgrade_app(prod_id, app_id, env_id=env_id)
        logger.info("第 {0} 次更新应用：{1}".format(i + 1, result))

        if 'System config synchronize successfully' in result.get('Message', ""):
            logger.info("应用更新成功。")
            break
        elif 'System config not changed' in result.get('Message', ""):
            logger.info('当前系统配置未做变更，无需升级')
            break
        else:
            time.sleep(10)
    else:
        raise Exception('应用更新失败！！！ {}'.format(json.dumps(result)))


def wait_upgrade_app_finish(see, prod_type_name, prod_type, app_name, env_id="001", timeout=30):
    """
    部署应用
    :param prod_type_name: 发布物次类型（应用类型）
    :param prod_type: 发布物类型 SEE.PATCH或者SEE.PRODUCT（不传则获取所有）
    :param app_name: 应用名称
    :param env_id: 环境ID
    :param timeout: 超时时间
    :return:
    """
    start = time.time()
    while True:
        if time.time() - start > timeout:
            raise Exception("等待超时。")

        appInfo = see.get_app(prod_type_name, prod_type, app_name=app_name, env_id=env_id)
        try:
            app_id = appInfo.get('id')
            clife_cycle = appInfo.get('lifeCycle')
            if clife_cycle == 80:
                logger.info('应用正在部署中。。。')
                time.sleep(10)
            elif clife_cycle == 140:
                raise Exception("应用部署失败。请检查配置。")
            elif clife_cycle == 100:
                logger.info('应用部署成功。。。')
                break
            elif clife_cycle == 60:
                raise Exception('应用待部署异常。原因未知。')

        except (IndexError, KeyError):
            raise Exception("找不到ID是'{}'的应用。".format(app_id))


def get_var(var, default=None):
    """
    获取环境变量
    :param:
    :return:
    """
    if sys.platform == 'win32':
        var = var.upper()
    if default is None:
        assert var in os.environ, "请配置环境变量'{}'".format(var)
    value = os.environ.get(var, default)
    logger.info("{}: {}".format(var, value))
    return value


def main():
    # see 登录信息
    see_url = "http://10.20.26.100:8081/acm/api/v1/application"
    # see_url = "http://{0}/acm/api/v1/application".format(os.environ["SeeURL"])
    see_usr = 'admin'
    see_pwd = '1'

    # 环境信息
    app_name = ""
    # 发布物类型
    prod_type = ''
    # 应用类型
    prod_type_name = ''
    # 环境ID（分配空间）
    env_id = 'hft'

    # 获取ftp信息
    # ftp_path = sys.argv[3]  # ftp路径
    # ftpAccount = json.loads(os.environ["ftpAccount"])
    # ftp_info = []
    # for item in ftpAccount:
    #     ftp_info.append(ftpAccount[item])
    # ftp_host = ftp_info[0]  # ftp地址
    # ftp_port = ftp_info[1]  # ftp端口
    # ftp_usr = ftp_info[2]  # ftp用户名
    # ftp_pwd = ftp_info[3]  # ftp密码

    see = SeeClient(see_url, see_usr, see_pwd)

    # 微服务程序包上传see
    # product = see.product_upload(ftp_host, ftp_port, ftp_path, ftp_usr, ftp_pwd, env_id=env_id)
    # if product.get('Status', None) == 'success':
    #     logger.info("微服务{0}成功上传see。".format(prod_type_name))
    #     prod_id = product["productId"]
    # else:
    #     raise Exception("微服务{}上传失败".format(prod_type_name))
    #     sys.exit(1)

    # 获取应用ID
    application = see.get_app(prod_type_name, prod_type, app_name=app_name, env_id=env_id)
    app_id = application["id"]
    logger.info('app id = ' + app_id)

    # 应用升级
    # upgrade_app(see, prod_id, app_id, env_id=env_id)
    # wait_upgrade_app_finish(see, prod_type_name, prod_type, app_name=app_name, env_id=env_id, timeout=timeout)


if __name__ == "__main__":
    main()
