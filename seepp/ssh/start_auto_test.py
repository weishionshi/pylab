#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author  : shiwx27477
# @time    : 2020/9/21 10:08
# @file    : start_auto_test.py
from util.ssh.ssh_client import SSHClient


def restart_auto_test(self):
    items = self.__sections_map['autotest']
    client = SSHClient(items.get('host'), items.get('user'), items.get('password'),
                       items.get('ssh_port'))
    # stop process
    cmd = items.get('deploy_path') + '/stop.sh'
    client.exec_cmd(cmd)
    # start process
    cmd = 'nohup sh %s/%s >nohup.log 2>&1 &' % (items.get('deploy_path'), items.get('start_shell'))
    client.exec_cmd_nb(cmd)
    # self.assertIsNotNone(latest_dir, 'lastest cannot be null')


if __name__ == '__main__':
    restart_auto_test()